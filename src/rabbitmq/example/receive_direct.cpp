#include <iostream>
#include "handler/poco_handler.h"
using namespace AMQP;

int DirectExchange(void)
{
    const char* start = "0";
    const char* end = "5";
    const std::string queue = "TEST";
    const std::string routingkey = "info";

    PocoHandler handler(HOST, 5672);

    AMQP::Connection connection(&handler, AMQP::Login("guest", "guest"), "/");

    AMQP::Channel channel(&connection);

    channel.declareExchange("direct_logs", AMQP::direct);

    auto receiveMessageCallback =
            [](const AMQP::Message &message,
               uint64_t deliveryTag=1,
               bool redelivered=false)
            {
                std::cout <<" [x] "
                          <<message.routingkey()
                          <<":"
                          <<message.body()
                          << std::endl;
            };

    AMQP::QueueCallback callback = [&](const std::string &name, int msgcount, int consumercount)
    {
        std::for_each(&start,
                &end,
                [&](const char* severity)
                {
                    
                    channel.bindQueue("direct_logs", "TEST_INFO", severity);
                    channel.consume("TEST_INFO", AMQP::noack).onReceived(receiveMessageCallback);
                    std::cout << "test" << std::endl;
                });

    };
    channel.declareQueue("TEST_INFO", AMQP::exclusive).onSuccess(callback);

    std::cout << " [*] Waiting for messages. To exit press CTRL-C\n";
    handler.loop();
}

int main(){

    return DirectExchange();
}