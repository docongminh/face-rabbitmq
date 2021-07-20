from detect_service.detect_consumer import DetectConsumer
import config

if __name__ == '__main__':
    cfg = config.detect_service
    model_config = cfg["model_config"]
    rabbitmq_config = cfg["rabbitmq_config"]
    publisher_config = cfg["publisher_config"]
    consumer = DetectConsumer(model_config=model_config,
                            rabbitmq_config=rabbitmq_config,
                            publisher_config=publisher_config)
    print("Start Consumer !")
    consumer.start()
    