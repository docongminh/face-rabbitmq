import sys
import time
import json
import numpy as np
from extract_service.engine import ExtractModel
sys.path.append("../rabbitmq")
from rabbitmq.consumer import Consumer
from rabbitmq import consumer_utils, publisher

class ExtractConsumer(Consumer):
    def __init__(self, model_config, rabbitmq_config, publisher_config):
        super().__init__(rabbitmq_config)
        self.model_config = model_config
        self.publisher_config = publisher_config
        self.model = ExtractModel(self.model_config)
    
    def callback(self, ch, method, properties, body):
        """
            Callback function extract consume
            >> message
            >> {
                    "phase": "insert" || "search"
                    "num_faces": num_face_exist_in_image
                    "detect_time": time
                    "extract_time": time
                    "data": {
                        "1": {
                            "embedding": embedding vector extracted,
                            "bbox": []
                        }
                    }
                } 
        """
        start_time = time.time()
        content = json.loads(body.decode(encoding="utf-8"))
        print("extract content: ", content)
        extract_message = {}
        #
        data = content["data"]
        num_faces = content["num_faces"]
        detect_time = content["detect_time"]
        keys = list(data.keys())
        # print("keys: ", keys)
        embedding_data = {}
        for key in keys:
            extract_data = {}
            # get data
            meta_face = data[key]
            bbox = meta_face["bbox"]
            face = np.asarray(meta_face["face"])
            # extract
            embedding = self.model.extract_feature(face)
            # storage data
            extract_data["embedding"] = embedding.tolist()
            extract_data["bbox"] = bbox
            embedding_data[key] = extract_data
        # message response
        extract_message["phase"] = content["phase"]
        extract_message["num_faces"] = num_faces
        extract_message["detect_time"] = detect_time
        extract_message["extract_time"] = time.time()-start_time
        extract_message["data"] = embedding_data
        data_json = json.dumps(extract_message)
        # print(data_json)
        publisher.send(exchange_name=self.publisher_config["exchange_name"],
                        key=self.publisher_config["routing_key"],
                        message=data_json)
        ch.basic_ack(delivery_tag=method.delivery_tag)
