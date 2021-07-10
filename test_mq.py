import pika
import config

username = config.rabbit_config["username"]
password = config.rabbit_config["password"]
host = config.rabbit_config["host"]
port = config.rabbit_config["port"]
virtual_host = '/'
print(host, port)
# make connect
credentials = pika.PlainCredentials(username, password)
connection_params = pika.ConnectionParameters(host, port, virtual_host, credentials)
print(dir(connection_params))
connection = pika.BlockingConnection(connection_params)
print("Connected")