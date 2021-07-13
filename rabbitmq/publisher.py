from rabbitmq import setup

def send(exchange_name, key, message):
	"""
	"""
	connection = setup.connect(use_url=False)
	channel = connection.channel()
	channel.basic_publish(exchange=exchange_name,
						routing_key=key,
						body=message)


