#include <iostream>
#include <sstream>
#include <time.h>
#include <regex>
#include <opencv2/opencv.hpp>
#include "handler/poco_handler.h"
#include "net.h"
#include "json.hpp"
#include "face_engine.h"
#include "utils.h"
#include "base64.h"
// #include "Poco/Base64Encoder.h"
using namespace AMQP;
using namespace engine;

int worker() {

    const std::string EXCHANGE_NAME = "Face";

    const std::string ROUTING_KEY = "extract_key";
    const std::string QUEUE_NAME = "q_extract";
    //
    // Load model
    const char* root_path = "../models";
    double start_load = static_cast<double>(cv::getTickCount());
	engine::FaceEngine* face_engine = new engine::FaceEngine();
	face_engine->LoadModel(root_path);
	double end_load = static_cast<double>(cv::getTickCount());
	double load_cost = (end_load - start_load) / cv::getTickFrequency() * 1000;
	std::cout << "load model cost: " << load_cost << "ms" << std::endl;

    //
    PocoHandler handler(HOST, 5672);

    AMQP::Connection connection(&handler, AMQP::Login("guest", "guest"), "/");

    AMQP::Channel channel(&connection);

    channel.onError([](const char *message) {
        // report error
        std::cout << "channel error: " << message << std::endl;
    });
    channel.setQos(1);

    // queue_arguments["x-max-priority"] = 10;

    // channel.declareExchange(EXCHANGE_NAME, AMQP::direct, AMQP::durable);
    channel.declareExchange(EXCHANGE_NAME, AMQP::direct);
    //
    // channel.declareQueue(QUEUE_NAME, AMQP::durable);
    channel.declareQueue(QUEUE_NAME, AMQP::exclusive);
    //
    channel.bindQueue(EXCHANGE_NAME, QUEUE_NAME, ROUTING_KEY);

    // callback function that is called when the consume operation starts
    auto startCb = [](const std::string &consumertag) {
        std::cout << "Start consume `q_extract`" << std::endl;
    };

    // callback function that is called when the consume operation failed
    auto errorCb = [](const char *message) {
        std::cout << "consume operation failed " << message << std::endl;
    };

    // callback operation when a message was received
    auto messageCb = [&channel, &face_engine](const AMQP::Message &message,
                            uint64_t deliveryTag, bool redelivered) 
    {
        // std::string str = message.body();
        // str.erase(std::find(str.begin(), str.end(), '\0'), str.end());

        std::string message_string;

        for (int i = 0; i < message.bodySize(); i++) {
            message_string += message.body()[i];
        }
        // std::cout << message_string << std::endl;
        
        nlohmann::json json_message = nlohmann::json::parse(message_string);
        // // get image base 64
        // std::cout << json_message << std::endl;
        int num_faces = json_message["num_faces"];
        double time_extract = 0;
        for(int i=0; i<num_faces; i++){
            std::string key = std::to_string(i);
            std::string image_base64 = json_message["data"][key]["face"];
            cv::Mat face_decoded = base64::base64_decode_image(image_base64);
            // do extract
            std::vector<float> feature;
            double start = static_cast<double>(cv::getTickCount());
            face_engine->ExtractFeature(face_decoded, &feature);
            double end = static_cast<double>(cv::getTickCount());
            double extract_cost = (end - start) / cv::getTickFrequency() * 1000;
            time_extract += extract_cost;
            std::cout << "detect cost: " << extract_cost << "ms" << std::endl;
            // convert to array
            float embedding[128];
            std::copy(feature.begin(), feature.end(), embedding);
            json_message["data"][key]["embedding"] = embedding;
            json_message["data"][key]["time_extract_per_face"] = extract_cost;
        }
        json_message["time_extract"] = time_extract;
        std::string body_message = json_message.dump(4); // indent = 4
        std::cout << "Message send to Response: " << body_message << std::endl;
        
        channel.startTransaction();

        channel.publish("Face", "response_key", body_message);

        channel.commitTransaction()
                .onSuccess([]() {
                    printf("successfully published\n");
                })
                .onError([](const char *message) {
                    fprintf(stderr, "%s\n", message);
                });
        std::cout << "--------------------------------" << std::endl;
    };

    channel.consume(QUEUE_NAME, AMQP::noack)
            .onReceived(messageCb)
            .onSuccess((AMQP::ConsumeCallback) startCb)
            .onError(errorCb);

    handler.loop();
    return 0;

}

int main(){
    
    
    worker();

}