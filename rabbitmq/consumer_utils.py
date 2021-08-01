import numpy as np
import cv2
import base64
import re
import sys
import time
import json
from rabbitmq import config
from rabbitmq import publisher
sys.path.append('..')


def base64_to_image(base64_string):
    """
    """
    base64_data = re.sub('^data:image/.+;base64,', '', base64_string)
    imgdata = base64.b64decode(base64_data)
    imgdata = np.fromstring(imgdata, np.uint8)
    image = cv2.imdecode(imgdata, cv2.IMREAD_COLOR)

    return image

def error_response(ch, method, message):
    """
        Send error response to Response Queue.\
        After that, Server get error nessage from Response Queue to show on client side
    """
    data_json = json.dumps(message)
    publisher.send(exchange_name=config.broker["exchange_name"],
                key=config.routing_keys["response_key"],
                message=data_json)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    return