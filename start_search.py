from search_service.milvus_2x.search_consumer import SearchConsumer
import config

if __name__ == '__main__':
    cfg = config.search_service
    milvus_config = cfg["milvus_config"]
    rabbitmq_config = cfg["rabbitmq_config"]
    publisher_config = cfg["publisher_config"]
    consumer = SearchConsumer(milvus_config=milvus_config,
                            rabbitmq_config=rabbitmq_config,
                            publisher_config=publisher_config)
    print("Start Search Consumer !")
    consumer.start()