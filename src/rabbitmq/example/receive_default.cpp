#include <iostream>
#include <algorithm>
#include <thread>
#include <chrono>

#include "handler/poco_handler.h"

int main(void)
{
        PocoHandler handler(HOST, 5672);

    AMQP::Connection connection(&handler, AMQP::Login("guest", "guest"), "/");

    AMQP::Channel channel(&connection);
    
    channel.declareQueue("TEST");
    channel.consume("TEST", AMQP::noack).onReceived(
            [](const AMQP::Message &message,
                       uint64_t deliveryTag,
                       bool redelivered)
            {

                std::cout <<" [x] Received "<<message.body() << std::endl;
            });

    std::cout << " [*] Waiting for messages. To exit press CTRL-C\n";
    handler.loop();
    return 0;
}
