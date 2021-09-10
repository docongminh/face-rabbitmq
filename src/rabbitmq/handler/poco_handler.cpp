#include <vector>
#include <thread>
#include <chrono>
#include <cstring>
#include <cassert>
#include <iostream>
#include <Poco/Net/StreamSocket.h>

#include "poco_handler.h"

namespace
{
    class Buffer
    {
    public:
        Buffer(size_t size) :
                m_data(size, 0),
                m_use(0)
        {
        }

        size_t write(const char* data, size_t size)
        {
            if (m_use == m_data.size())
            {
                return 0;
            }

            const size_t length = (size + m_use);
            size_t write =
                    length < m_data.size() ? size : m_data.size() - m_use;
            memcpy(m_data.data() + m_use, data, write);
            m_use += write;
            return write;
        }

        void drain()
        {
            m_use = 0;
        }

        size_t available() const
        {
            return m_use;
        }

        const char* data() const
        {
            return m_data.data();
        }

        void shl(size_t count)
        {
            assert(count<m_use);

            const size_t diff = m_use - count;
            std::memmove(m_data.data(), m_data.data()+count, diff);
            m_use = m_use - count;
        }

    private:
        std::vector<char> m_data;
        size_t m_use;
    };
}

struct PocoHandlerImpl
{
    PocoHandlerImpl() :
            connected(false),
            connection(nullptr),
            quit(false),
            inputBuffer(PocoHandler::BUFFER_SIZE),
            outBuffer(PocoHandler::BUFFER_SIZE),
            tmpBuff(PocoHandler::TEMP_BUFFER_SIZE)
    {
    }

    Poco::Net::StreamSocket socket;
    bool connected;
    AMQP::Connection* connection;
    bool quit;
    Buffer inputBuffer;
    Buffer outBuffer;
    std::vector<char> tmpBuff;
};

PocoHandler::PocoHandler(const std::string& host, uint16_t port) :
        m_impl(new PocoHandlerImpl)
{
    const Poco::Net::SocketAddress address(host, port);
    m_impl->socket.connect(address);
    m_impl->socket.setKeepAlive(true);
}

PocoHandler::~PocoHandler()
{
    close();
}

void PocoHandler::loop()
{
    try
    {
        while (!m_impl->quit)
        {
            if (m_impl->socket.available() > 0)
            {
                size_t avail = m_impl->socket.available();
                if(m_impl->tmpBuff.size()<avail)
                {
                    m_impl->tmpBuff.resize(avail,0);
                }

                m_impl->socket.receiveBytes(&m_impl->tmpBuff[0], avail);
                m_impl->inputBuffer.write(m_impl->tmpBuff.data(), avail);

            }
            if(m_impl->socket.available()<0)
            {
                std::cerr<<"SOME socket error!!!"<<std::endl;
            }

            if (m_impl->connection && m_impl->inputBuffer.available())
            {
                size_t count = m_impl->connection->parse(m_impl->inputBuffer.data(),
                        m_impl->inputBuffer.available());

                if (count == m_impl->inputBuffer.available())
                {
                    m_impl->inputBuffer.drain();
                } else if(count >0 ){
                    m_impl->inputBuffer.shl(count);
                }
            }
            sendDataFromBuffer();

            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        if (m_impl->quit && m_impl->outBuffer.available())
        {
            sendDataFromBuffer();
        }

    } catch (const Poco::Exception& exc)
    {
        std::cerr<< "Poco exception " << exc.displayText();
    }
}

void PocoHandler::quit()
{
    m_impl->quit = true;
}

void PocoHandler::PocoHandler::close()
{
    m_impl->socket.close();
}

void PocoHandler::onData(
        AMQP::Connection *connection, const char *data, size_t size)
{
    m_impl->connection = connection;
    const size_t writen = m_impl->outBuffer.write(data, size);
    if (writen != size)
    {
        sendDataFromBuffer();
        m_impl->outBuffer.write(data + writen, size - writen);
    }
}

void PocoHandler::onConnected(AMQP::Connection *connection)
{
    m_impl->connected = true;
}

void PocoHandler::onError(
        AMQP::Connection *connection, const char *message)
{
    std::cerr<<"AMQP error "<<message<<std::endl;
}

void PocoHandler::onClosed(AMQP::Connection *connection)
{
    std::cout<<"AMQP closed connection"<<std::endl;
    m_impl->quit  = true;
}

bool PocoHandler::connected() const
{
    return m_impl->connected;
}

void PocoHandler::sendDataFromBuffer()
{
    if (m_impl->outBuffer.available())
    {
        m_impl->socket.sendBytes(m_impl->outBuffer.data(), m_impl->outBuffer.available());
        m_impl->outBuffer.drain();
    }
}

