import pika
from rabbitmq import config
import logging

logging.basicConfig(filename='log_setup_rabbitmq.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

def connect(use_url=False):
	"""
		Connect rabbitmq Broker
		use_url: https://pika.readthedocs.io/en/stable/modules/parameters.html#urlparameters
		use_params: https://pika.readthedocs.io/en/stable/modules/parameters.html#connectionparameters
	"""
	if not isinstance(use_url, bool):
		raise TypeError("Type of use_url must be boolean")

	if not use_url:
		credentials = pika.PlainCredentials(username=config.admin["username"],
										password=config.admin["password"],
										erase_on_connect=False)
		# connect parameters
		connect_params = pika.ConnectionParameters(config.admin["host"],
												config.admin["port"],
												config.admin["vhost"],
												credentials)
	else:
		url = ''
		connect_params = pika.pika.URLParameters(url)
	try:
		connection = pika.BlockingConnection(connect_params)
	except Exception as e:
		logging.error("Logging connect RabbitMQ...", exc_info=True)
		return

	return connection