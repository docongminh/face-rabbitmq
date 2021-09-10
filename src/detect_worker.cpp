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
//
using namespace AMQP;
using namespace engine;

void ImageDecoder(std::string image, cv::Mat &decoded_image){
    // TODO add try-exception
    decoded_image = base64::base64_decode_image(image);

}

void ImageEncoder(cv::Mat image, std::string &encoded_image){
    // TODO add try-exception
    encoded_image = base64::base64_encode_image(image);

}

int worker() {

    const std::string EXCHANGE_NAME = "Face";

    const std::string ROUTING_KEY = "detect_key";
    const std::string QUEUE_NAME = "q_detect";
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
        std::cout << "Start consume `q_detect`..." << std::endl;
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
        
        nlohmann::json json_message = nlohmann::json::parse(message_string);
        // // get image base 64
        std::string base64_str = json_message["image"];
        // std::cout << "11111" <<std::endl;
        // // std::cout << "base64 str: " << base64_str <<std::endl;
        // std::regex regexp("^data:image/.+;base64,");
        // // std::cout << "222" <<std::endl;
        // std::string base64_image = std::regex_replace(base64_str, regexp, "");
        // // std::string base64_image = regex_replace(base64_str, std::regex("^data:image/.+;base64,"), "");

        cv::Mat image_decoded;
        ImageDecoder(base64_str, image_decoded);
        cv::imwrite("test.jpg", image_decoded);
        //
        std::vector<utils::FaceInfo> faces;
        double detect_time;
        double start = static_cast<double>(cv::getTickCount());
        face_engine->DetectFace(image_decoded, &faces);
        double end = static_cast<double>(cv::getTickCount());
        detect_time = (end - start) / cv::getTickFrequency() * 1000;
        //
        // cv::rectangle(img, faces.at(0).location_, cv::Scalar(0, 255, 0), 2);
        // cv::imwrite("retinaface_result.jpg", img);
        std::cout << "time detect cost: " << detect_time << "ms" << std::endl;

        // delete face_engine;
        // face_engine = nullptr;


        // channel.ack(deliveryTag);
        // process data detected and prepare for publish new message
        nlohmann::json detect_message;
        nlohmann::json detect_storage;
        for (int i = 0; i < static_cast<int>(faces.size()); ++i) {
		    utils::FaceInfo face_info = faces.at(i);
            cv::Rect loc = face_info.location_;
           
            float x = loc.tl().x, y = loc.tl().y, width = loc.br().x, height = loc.br().y;
            cv::Mat face_cropped = image_decoded(loc).clone();
            // cv::imwrite("face.jpg", face_cropped);
            std::string face;
            ImageEncoder(face_cropped, face);
            //
            detect_storage[std::to_string(i)]["face"] = face;
            detect_storage[std::to_string(i)]["loc"] = {x, y, width, height};
            detect_storage[std::to_string(i)]["keypoints"] = face_info.keypoints_;
            detect_storage[std::to_string(i)]["score"] = face_info.score_;
        }
        detect_message["data"] = detect_storage;
        detect_message["num_faces"] = faces.size();
        detect_message["time_detect"] = detect_time;
        std::string body_message = detect_message.dump(4); // indent = 4
        std::cout << "Message send to Extract: " << body_message << std::endl;
        
        channel.startTransaction();

        channel.publish("Face", "extract_key", body_message);

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