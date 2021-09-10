#ifndef POCOHANDLER_H
#define POCOHANDLER_H

#include <memory>
#include <amqpcpp.h>

#define HOST "192.168.82.101"
// https://github.com/CopernicaMarketingSoftware/AMQP-CPP/issues/265

class PocoHandlerImpl;
class PocoHandler: public AMQP::ConnectionHandler
{
public:

    static constexpr size_t BUFFER_SIZE = 8 * 1024 * 1024; //8Mb
    static constexpr size_t TEMP_BUFFER_SIZE = 1024 * 1024; //1Mb

    PocoHandler(const std::string& host, uint16_t port);
    virtual ~PocoHandler();

    void loop();
    void quit();

    bool connected() const;

private:

    PocoHandler(const PocoHandler&) = delete;
    PocoHandler& operator=(const PocoHandler&) = delete;

    void close();

    virtual void onData(
            AMQP::Connection *connection, const char *data, size_t size);

    virtual void onConnected(AMQP::Connection *connection);

    virtual void onError(AMQP::Connection *connection, const char *message);

    virtual void onClosed(AMQP::Connection *connection);

    void sendDataFromBuffer();

private:

    std::shared_ptr<PocoHandlerImpl> m_impl;
};

#endif /* POCOHANDLER_H */
