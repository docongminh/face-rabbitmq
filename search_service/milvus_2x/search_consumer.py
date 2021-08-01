import sys
import time
import json
import numpy as np
from search_service.milvus_2x.engine import SearchEngine
sys.path.append("../rabbitmq")
from rabbitmq.consumer import Consumer
from rabbitmq import consumer_utils, publisher

class SearchConsumer(Consumer):
    def __init__(self, milvus_config, rabbitmq_config, publisher_config):
        super().__init__(rabbitmq_config)
        self.milvus_config = milvus_config
        self.publisher_config = publisher_config
        self.engine = SearchEngine(self.milvus_config)
    
    def callback(self, ch, method, properties, body):
        """
        
        """
        start_time = time.time()
        content = json.loads(body.decode(encoding="utf-8"))
        search_message = {}
        # parsing content
        phase = content["phase"]
        data = content["data"]
        num_face = content["num_faces"]
        detect_time = content["detect_time"]
        extract_time = content["extract_time"]

        if phase == 'insert' and num_face>1:
            search_message["message"] = "Insert phase must be only single face"
        elif phase == 'insert' and num_face == 1:
            key = list(data.keys())[0]
            embedding = data[key]["embedding"]
            bbox = data[key]["bbox"]
            index, total_entities = self.engine.insert(embedding)
            # define message
            search_message["detect_time"] = content["detect_time"]
            search_message["extract_time"] = content["extract_time"]
            search_message["index"] = index
            search_message["total_entities"] = total_entities
        elif phase == 'search':
            keys = list(data.keys())
            # TODO later
        #
        data_json = json.dumps(search_message)
        # print(data_json)
        publisher.send(exchange_name=self.publisher_config["exchange_name"],
                        key=self.publisher_config["routing_key"],
                        message=data_json)
