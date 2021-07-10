import pymongo
import cv2
import numpy as np
import os
import time
import pika
import config
import traceback
import json
import math
# from recognition.arcface_mxnet import face_model
import datetime
import utils
import re
import base64
import requests
from detection.retina_face.base_detection import DetectBase
from alignment.align import *
from engine import FaceModel

faceTable = None
connection = None
r = None
queue_stores = {}
file_prefix = str(time.time())



def remove_file(path):
    os.remove(path)

def get_faces(image):
    """
    Input : image 
    return list [(face_1_cropped, [x, y, xx, yy, confidence])]
    """
    start = time.time()
    crop_size=(112,112)
    img = np.float32(image)
    dets, landms = detector.detect(img)
    print(landms)
    print("Time Detect: ", time.time()-start)
    for idx, land in enumerate(landms):
        points = [[land[i], land[i+1]] for i in range(0, 10, 2)]
        warped_face = warp_and_crop_face(image, points, reference, crop_size)
    print("Total time detect: ", time.time()-start)
    return warped_face, 1

# def extract_single_face(img, data):
#     start = time.time()
#     try:
#         img, face_size = model.get_input(img)
#         data["detect_duration"] = time.time() - start
#     except:
#         return None, 0
#     if face_size != 1:
#         data["detect_duration"] = time.time() - start
#         return None, face_size
#     start = time.time()
#     try:
#         new_embedding = np.array([model.get_feature(img)])
#     except:
#         traceback.print_exc()
#         return None, face_size

#     data["extract_duration"] = time.time() - start
#     return new_embedding, face_size

def extract_single_face(img, data):
    """
        test retina face 1MB landmarks
    """
    start = time.time()
    try:
        img, face_size = get_faces(img)
        img = np.transpose(img, (2, 1, 0))
        # img, face_size = model.get_input(img)
        print("alig: ", img.shape)
        data["detect_duration"] = time.time() - start
    except:
        return None, 0
    if face_size != 1:
        data["detect_duration"] = time.time() - start
        return None, face_size
    start = time.time()
    try:
        new_embedding = np.array([model.get_feature(img)])
    except:
        traceback.print_exc()
        return None, face_size

    data["extract_duration"] = time.time() - start
    return new_embedding, face_size


def connect_mq():
    credentials = pika.PlainCredentials(
        config.rabbit_config["username"], config.rabbit_config["password"])
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config.rabbit_config["host"], config.rabbit_config["port"], '/', credentials))
    return connection


def connect_redis():
    connection = redis.Redis(host=config.redis_config['host'], port=config.redis_config['port'],
                             db=config.redis_config['db'])
    return connection


def create_channel(queue_name):
    try:
        channel = connection.channel()
    except Exception as ex:
        traceback.print_exc()
        connect_mq()
        channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return channel


def get_channel(queue_name):
    if queue_name in queue_stores:
        return queue_stores[queue_name]
    channel = create_channel(queue_name)
    queue_stores[queue_name] = channel
    return channel


def send(queue_name, data):
    channel = get_channel(queue_name)
    try:
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=data)
    except:
        print('send message error', data)
        traceback.print_exc()
        return
    print('send message complete', data)


def connect_mongo():
    myclient = pymongo.MongoClient(config.mongo_config["uri"])
    mydb = myclient[config.mongo_config["database_name"]]
    faceTable = mydb[config.mongo_config["face_table"]]
    return faceTable


def base64_to_image(base64_string):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_string)
    imgdata = base64.b64decode(base64_data)
    imgdata = np.fromstring(imgdata, np.uint8)
    image = cv2.imdecode(imgdata, cv2.IMREAD_COLOR)
    print(type(image))
    print(image.shape)
    m_max = max([image.shape[0], image.shape[1]])
    if m_max > 600:
        scale = m_max / 600
        dim = (int(image.shape[1]/scale), int(image.shape[0]/scale))
        image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    print(image.shape)
    return image


def write_image(imagedata):
    now = datetime.datetime.now()
    # print(imageContent)
    imageDir = config.store_config["store_dir"] + "/" + \
               str(now.year) + "/" + str(now.month) + "/" + str(now.day)
    imageName = file_prefix + "-image-" + str(time.time())
    if not os.path.exists(imageDir):
        os.makedirs(imageDir)

    filename = imageDir + "/" + imageName + ".png"
    cv2.imwrite(filename, imagedata)
    return filename


def callback(ch, method, properties, body):
    print("callsback")
    start = time.time()
    content = json.loads(body.decode(encoding="utf-8"))
    duration = {}
    data_rs = {
        "code": 200,
        "message": "",
        "clientId": content["clientId"],
    }
    if 'image' not in content:
        data_rs["code"] = 1000
        data_rs["message"] = "image.miss"
        rs = json.dumps(data_rs)
        send(content["queue"], rs)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    imageContent = content['image']
    print("convert base64 to images")
    try:
        imgdata = base64_to_image(imageContent)
        duration['extract_image'] = time.time() - start
    except:
        print('Error at base64 decode')
        traceback.print_exc()
        data_rs["code"] = 1001
        data_rs["message"] = "image.invalid"
        duration['extract_image'] = time.time() - start
        data_rs['duration'] = duration
        rs = json.dumps(data_rs)
        send(content["queue"], rs)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    # if True:
    #     return
    print(duration)
    list_faces = []
    embedings = []
    embed, face_size = extract_single_face(imgdata, duration)
    print("embedding: ", embed)
    data_rs['duration'] = duration
    if face_size == 0:
        data_rs["code"] = 1009
        data_rs["message"] = "image.no_face"
        rs = json.dumps(data_rs)
        send(content["queue"], rs)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if face_size > 1:
        data_rs["code"] = 1008
        data_rs["message"] = "image.multi_face"
        rs = json.dumps(data_rs)
        send(content["queue"], rs)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if embed is None:
        data_rs["code"] = 1006
        data_rs["message"] = "image.extract_feauture_error"
        rs = json.dumps(data_rs)
        send(content["queue"], rs)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    face_id = ""
    # if index is not None:
    #     face_id = str(list_faces[index]["_id"])
    data_rs["features"] = embed.tolist()
    # data_rs["face"] = face_id
    # data_rs["distance"] = distance
    print("data_rs", data_rs)
    rs = json.dumps(data_rs)
    send(content["queue"], rs)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    durration = time.time() - start
    print("Total time: ", durration)
    print(duration)


if __name__ == '__main__':
    model = FaceModel()
    detector = DetectBase(
            net_type = 'slim',
            weight_path = './model_storage/retina_weights/slim_Final.pth',
            device='cpu',
            size=(480, 640),
            mean=[104, 117, 123],
            phase='test',
            confidence_threshold=0.6,
            nms_threshold=0.4,
            keep_top_k=750,
            top_k=5000
    )
    reference = get_reference_facial_points(default_square=True)
    # data = {}
    # img = cv2.imread("./source/imgs/test.png")
    # print(img)
    # embed, face_size = extract_single_face(img, data)
    # print(embed)
    # faceTable = connect_mongo()
    # print("Connect mongo complete ")
    connection = connect_mq()
    print("Connect rabbit mq ")
    # r = connect_redis()
    # print("Connect redis server")
    channel = create_channel(config.queue_config["q_identify_name"])

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=config.queue_config["q_identify_name"], on_message_callback=callback)

    channel.start_consuming()

    # print("Begin listening at ", config.queue_config["q_identify_name"])
