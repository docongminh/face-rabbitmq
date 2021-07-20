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
        self.connection = setup.connect(use_url=False)
    
    def start(self):

        channel = self.connection.channel()
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

    @abstractmethod
    def callback(self):
        """
            Should be override by all subclasses
            Different consumer may have different configuration
        """
        pass


        

    
