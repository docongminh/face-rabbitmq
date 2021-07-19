from rabbitmq import consumer, config

if __name__ == '__main__':
    mtcnn_path = "./models/mtcnn-model"
    consumer = consumer.Consumer(model_path=mtcnn_path)
    print(consumer)
    consumer.start()
    print("Start Consumer !")