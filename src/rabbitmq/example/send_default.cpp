#include <iostream>
#include "handler/poco_handler.h"

using namespace AMQP;

int main(void)
{
    SimplePocoHandler handler(HOST, 5672);

    AMQP::Connection connection(&handler, AMQP::Login("guest", "guest"), "/");
    AMQP::Channel channel(&connection);

    channel.onReady([&]()
    {   
        std::cout << "test" <<std::endl;
        // if(handler.connected())
        // {
        std::cout << "test connect" <<std::endl;
        channel.publish("", "TEST", "Hello World!");
        std::cout << " [x] Sent 'Hello World!'" << std::endl;
        handler.quit();
        // }
    });

    handler.loop();
    return 0;
}
