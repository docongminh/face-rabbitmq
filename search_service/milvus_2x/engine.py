import os
import sys
import time
from pymilvus_orm import connections, Collection, DataType, FieldSchema, CollectionSchema

class SearchEngine:
    def __init__(self, milvus_config):
        self.milvus_config = milvus_config
        self.connect()
        self.collection = self.create_collection()
    
    def connect(self):
        host = self.milvus_config["host"]
        port = self.milvus_config["port"]
        try:
            print("Connecting to host: {} with port: {}".format(host, port))
            connections.add_connection(default={"host": host, "port": port})
            connections.connect(alias='default')
        except:
            raise ValueError("Check your host or ip")

    def create_collection(self):
        """
            reference: - Set DataType: https://github.com/milvus-io/pymilvus-orm/blob/main/pymilvus_orm/types.py
        """
        dim = self.milvus_config["embedding_size"]
        _id = FieldSchema(name="id", dtype=DataType.INT64, description="primary_field")
        embedding = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
        fields = [_id, embedding]
        schema = CollectionSchema(fields=fields, primary_field='id', auto_id=False, description='Collection Vector embedding')
        collection_name = self.milvus_config["collection_name"]
        collection = Collection(name=collection_name, schema=schema)
        
        return collection

    def insert(self, embedding):
        """
            - Insert data into the collection
            - In original docs type of `data` like tuple or list. But in my customize version i only use data as list type.
                See more: https://pymilvus-orm.readthedocs.io/en/latest/api/collection.html#pymilvus_orm.Collection.insert
            return: Number of entities after insert successfuly
            Exception: 
                - CollectionNotExistException – If the specified collection does not exist.
                - ParamError – If input parameters are invalid.
                - BaseException – If the specified partition does not exist.
        """
        if not isinstance(embedding, list):
            raise ValueError('data must be list of element')
        current_entities = self.collection.num_entities
        print("Current: ", current_entities)
        index = current_entities + 1
        print("index type: ", type(index))
        data = [[index], [embedding]]
        self.collection.insert(data=data)
        after_entities = self.collection.num_entities
        print("[SUCCESS] Inserted {} entities into {} collection".format((current_entities-after_entities), self.collection.name))
        return index, after_entities
        

    def search(self, params):
        """

        params example: {
                "data": [[1.0, 1.0]],
                "anns_field": "films",
                "param": {"metric_type": "L2"},
                "limit": 2,
                "expr": "film_id > 0",
            }
        
        reference: https://pymilvus-orm.readthedocs.io/en/latest/api/collection.html#pymilvus_orm.Collection.search
        """
        # load collection from memory
        self.collection.load()

        search_result = self.collection.search(**params)

        return search_result

    @classmethod
    def run_test(cls, config):

        engine = cls(config)
        #init data
        print("data prepring....")
        total_entities = 100
        dim = 128
        embd = []
        obj = []
        for i in tqdm.tqdm(range(total_entities)):
            embedding = [random.uniform(0, 1) for _ in range(128)]
            _obj = int(i)
            embd.append(embedding)
            obj.append(_obj)
        data = [embd]
        print("Starting insert data...")
        num = engine.insert(data)

        print("Preparing data to search")
        v = [random.uniform(0, 1) for _ in range(128)]
        anns_field = "embedding"
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        topK = 10
        params = {
                    "data": [v],
                    "anns_field": anns_field,
                    "param": {"metric_type": "L2"},
                    "limit": topK
                }
        start_time = time.time()
        print("Search embedding vector")

        # define output_fields of search result
        res = engine.search(params)
        end_time = time.time()
        # show result
        for hits in res:
            for hit in hits:
                # Get value of the random value field for search result
                print("ID: ", hit.id)
                print("distance: ", hit.distance)
                print("---")
        print("search latency = %.4fs" % (end_time - start_time))

if __name__ == "__main__":
    import tqdm
    import random
    import string

    config = {
        "host": "192.168.82.105", 
        "port": 19530,
        "embedding_size": 128,
        "collection_name": "Face_Embedding",
        "metric": "L2"
    }
    SearchEngine.run_test(config)