from rabbitmq import consumer, config

if __name__ == '__main__':
    mtcnn_path = "./model_storage/mtcnn-model"
    consumer = consumer.Consumer(model_path=mtcnn_path)
    consumer.start()