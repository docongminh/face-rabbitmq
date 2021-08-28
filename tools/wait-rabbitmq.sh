#!/bin/sh
# wait-rabbitmq.sh

set -e
  
host="$1"
shift
  
until rabbitmq -h "$host" -U "rabbitmq" -c '\q'; do
  >&2 echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "RabbitMQ is up - executing command"
exec "$@"