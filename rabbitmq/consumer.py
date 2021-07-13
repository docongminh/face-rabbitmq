import numpy as np
import cv2
import base64
import re
import sys
import time
import json
from rabbitmq import config
from rabbitmq import publisher
from rabbitmq import setup
from rabbitmq import consumer_utils
sys.path.append('..')
from detect_service import engine

class Consumer:
    def __init__(self, model_path):
        self.model_path = model_path
        self.mtcnn = engine.MtcnnEngine(self.model_path)
        self.connection = setup.connect(use_url=False)
    
    def start(self):

        channel = self.connection.channel()
        channel.exchange_declare(exchange=config.broker["exchange_name"],
							exchange_type=config.broker["exchange_type"])
        channel.queue_declare(queue=config.broker["detect_queue"],
                            durable=False)
        channel.queue_bind(exchange=config.broker["exchange_name"],
                        queue=config.broker["detect_queue"],
                        routing_key=config.routing_keys["detect_key"])
        
        channel.basic_consume(queue=config.broker["detect_queue"],
                            on_message_callback=self.callback,
                            auto_ack=False)
        channel.start_consuming()
        print("Begin listening at:  ", config.broker["detect_queue"])

    def callback(self, ch, method, properties, body):
        # super(Consumer).__init__(self)
        start_time = time.time()
        content = json.loads(body.decode(encoding="utf-8"))
        print(content)
        detect_message = {}
        # check image base64 string exist value
        if 'image' not in content:
            detect_message["message"] = "No image in message"
            consumer_utils.error_response(ch, method, detect_message)
            return
        # decode base64
        imageContent = content['image']
        try:
            self.imgdata = consumer_utils.base64_to_image(imageContent)
        except:
            detect_message["message"] = "image invalid. Can not decode base64 image"
            consumer_utils.error_response(ch, method, detect_message)
            return
        # execute detect
        faces_aligned, bboxs, num_face = self.mtcnn.get_faces(self.imgdata)
        detect_message["detect_time"] = time.time()-start_time
        # check num of faces
        if num_face == 0:
            detect_message["message"] = "No face detected"
            consumer_utils.error_response(ch, method, detect_message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        data = []
        for i in num_face:
            meta_face = {}
            meta_face["face"] = faces_aligned[i]
            meta_face["bbox"] = bboxs[i]
            data.append(meta_face)

        detect_message["result"] = data
        detect_message["num_faces"] = num_face
        data_json = json.dumps(detect_message)
        consumer_utils.send(exchange_name=config.broker["exchange_name"],
                        key=config.routing_keys["extract_key"],
                        message=data_json)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        

    
