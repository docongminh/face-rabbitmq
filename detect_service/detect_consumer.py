import sys
import time
import json
from detect_service.engine import MtcnnEngine
sys.path.append("../rabbitmq")
from rabbitmq.consumer import Consumer
from rabbitmq import consumer_utils, publisher

class DetectConsumer(Consumer):
    def __init__(self, model_config, rabbitmq_config, publisher_config):
        super().__init__(rabbitmq_config)
        self.model_config = model_config
        self.publisher_config = publisher_config
        self.model = MtcnnEngine(self.model_config)
    
    def callback(self, ch, method, properties, body):
        start_time = time.time()
        content = json.loads(body.decode(encoding="utf-8"))
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
        faces_aligned, bboxs, num_face = self.model.get_faces(self.imgdata)
        detect_message["detect_time"] = time.time()-start_time
        # check num of faces
        if num_face == 0:
            detect_message["message"] = "No face detected"
            consumer_utils.error_response(ch, method, detect_message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        data = {}
        for i in range(0, num_face):
            meta_face = {}
            meta_face["face"] = faces_aligned[i].tolist()
            meta_face["bbox"] = bboxs[i].tolist()
            idx_key = str(i)
            data[idx_key] = meta_face
        #
        detect_message["data"] = data
        detect_message["num_faces"] = num_face
        data_json = json.dumps(detect_message)
        # print(data_json)
        publisher.send(exchange_name=self.publisher_config["exchange_name"],
                        key=self.publisher_config["routing_key"],
                        message=data_json)
        ch.basic_ack(delivery_tag=method.delivery_tag)
