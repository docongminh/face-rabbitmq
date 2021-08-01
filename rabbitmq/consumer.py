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
from abc import ABCMeta, abstractmethod

class Consumer(metaclass=ABCMeta):
    """
        Base class for Rabbit MQ consumer
        All consumers need to inherit this base class
        And each new class needs to implement the "callback function" method
    """
    def __init__(self, config):
        self.config = config

    def start_consumer(self, connection):
        channel = connection.channel()
        # declare exchange type and name
        channel.exchange_declare(exchange=self.config["exchange_name"],
                            exchange_type=self.config["exchange_type"])
        # declare queue name
        channel.queue_declare(queue=self.config["queue_name"],
                            durable=self.config["durable"])
        # config binding
        channel.queue_bind(exchange=self.config["exchange_name"],
                        queue=self.config["queue_name"],
                        routing_key=self.config["binding_key"])
        # consumer queue
        channel.basic_consume(queue=self.config["queue_name"],
                            on_message_callback=self.callback,
                            auto_ack=False)
        print("Begin listening at:  ", self.config["queue_name"])
        channel.start_consuming()
        
    def start(self):
        """
            This way to reconnection rabbitMQ  is not best solution. I will update using retry soon.
            reference: - https://pika.readthedocs.io/en/stable/examples/blocking_consume_recover_multiple_hosts.html
                    - https://www.programmersought.com/article/90767106580/ 
                    - https://github.com/invl/retry
        """
        try:
            connection = setup.connect(use_url=False)
            self.start_consumer(connection)   
        except Exception as e:
            print(e)
            print("Reconnecting...")
            while True:
                connection = setup.connect(use_url=False)
                if connection and connection.is_open:
                    print("Reconnect successful !")
                    self.start_consumer(connection)

    @abstractmethod
    def callback(self):
        """
            Should be override by all subclasses
            Different consumer may have different configuration
        """
        pass


        

    
