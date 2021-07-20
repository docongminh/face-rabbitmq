from extract_service.extract_consumer import ExtractConsumer
import config

if __name__ == '__main__':
    cfg = config.extract_service
    model_config = cfg["model_config"]
    rabbitmq_config = cfg["rabbitmq_config"]
    publisher_config = cfg["publisher_config"]
    consumer = ExtractConsumer(model_config=model_config,
                            rabbitmq_config=rabbitmq_config,
                            publisher_config=publisher_config)
    print("Start Consumer !")
    consumer.start()
    