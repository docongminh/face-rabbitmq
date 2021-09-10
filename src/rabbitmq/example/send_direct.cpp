#include <iostream>
#include "handler/poco_handler.h"

using namespace AMQP;

int main(void)
{
    const std::string severity = "0";
    const std::string msg = "Hello World!";
    PocoHandler handler(HOST, 5672);

    AMQP::Connection connection(&handler, AMQP::Login("guest", "guest"), "/");

    AMQP::Channel channel(&connection);
    channel.declareExchange("direct_logs", AMQP::direct).onSuccess([&]()
    {
        channel.publish("direct_logs", severity, msg);
        std::cout << " [x] Sent "<<severity<<": "<<msg<< std::endl;
        handler.quit();
    });

    handler.loop();
    return 0;
}
