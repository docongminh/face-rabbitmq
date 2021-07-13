from rabbitmq import setup

def send(exchange_name, key, message):
	"""
	"""
	connection = setup.connect(use_url=False)
	channel = setup.create_channel(connection)
	channel.basic_publish(exchange=exchange_name,
						routing_key=routing_key,
						body=message)


