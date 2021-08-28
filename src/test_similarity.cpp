#include <iostream>
#include <time.h>
#include <experimental/filesystem>
#include <opencv2/opencv.hpp>
#include "net.h"
#include "math.h"
#include "face_engine.h"
#include "utils.h"
using namespace engine;

int ExtractSimilary(int argc, char* argv[])
{
	cv::Mat img1 = cv::imread(argv[1], cv::IMREAD_COLOR);
	cv::Mat img2 = cv::imread(argv[2], cv::IMREAD_COLOR);
	const char* root_path = "../models";

	double start_load = static_cast<double>(cv::getTickCount());
	FaceEngine* face_engine = new FaceEngine();
	face_engine->LoadModel(root_path);
	double end_load = static_cast<double>(cv::getTickCount());
	double load_cost = (end_load - start_load) / cv::getTickFrequency() * 1000;
	std::cout << "load model cost: " << load_cost << "ms" << std::endl;
	
	std::vector<float> feature1;
	std::vector<float> feature2;
	//
	double totaltime = 0;
    double total_cosin = 0;
	//
	for (int i=0; i< 100; i++){
		//
		double start_time = static_cast<double>(cv::getTickCount());
		//
		face_engine->ExtractFeature(img1, &feature1);
		face_engine->ExtractFeature(img2, &feature2);
		// cal cosin
        float cosin_similary = utils::CosinSimilar(feature1, feature2);
		//
		double finish_time = static_cast<double>(cv::getTickCount());
		double extract_time = (finish_time - start_time) / cv::getTickFrequency() * 1000;
		//
		totaltime += extract_time;
		total_cosin += cosin_similary;
	}
    std::cout << "-----------------------" << std::endl;
	std::cout << "Average time: "<< totaltime/100 << "ms" << std::endl;
    std::cout << "Average Cosin similarity: "<< total_cosin/100 << std::endl;

	delete face_engine;
	face_engine = nullptr;

	return 0;
}

int Extract_noAlign(int argc, char* argv[])
{
	cv::Mat img1 = cv::imread(argv[1], cv::IMREAD_COLOR);
	cv::Mat img2 = cv::imread(argv[2], cv::IMREAD_COLOR);
	std::cout << "argv 0: " <<argv[0] <<std::endl;
	std::cout << "argv 1: " <<argv[1] <<std::endl;
	std::cout << "argv 2: " <<argv[2] <<std::endl;
	std::cout << "argv 3: " <<argv[3] <<std::endl;
	std::cout << "argv 4: " <<argv[4] <<std::endl;
	std::vector<float> feature1;
	std::vector<float> feature2;
	cv::Mat image1, image2;
	std::string label;
	float accuracy;
	std::string path = argv[3];
	std::string name = argv[4];

	//
	double totaltime = 0;
    double total_cosin = 0;
	//
	std::vector<utils::FaceInfo> face1;
	std::vector<utils::FaceInfo> face2;
	cv::Mat merge;


	const char* root_path = "../models";

	double start_load = static_cast<double>(cv::getTickCount());
	FaceEngine* face_engine = new FaceEngine();
	face_engine->LoadModel(root_path);
	double end_load = static_cast<double>(cv::getTickCount());
	double load_cost = (end_load - start_load) / cv::getTickFrequency() * 1000;
	std::cout << "load model cost: " << load_cost << "ms" << std::endl;
	// for (int i=0; i< 1; i++){
		
		//
	double start_time = static_cast<double>(cv::getTickCount());
	//
	face_engine -> DetectFace(img1.clone(), &face1);
	utils::draw(img1.clone(), face1, image1);
	face_engine->ExtractFeature(img1(face1[0].location_).clone(), &feature1);
	//
	face_engine -> DetectFace(img2.clone(), &face2);
	utils::draw(img2.clone(), face2, image2);
	face_engine->ExtractFeature(img2(face2[0].location_).clone(), &feature2);
	utils::JoinTwoImage(image1, image2, merge);

	float cosin_similary = utils::CosinSimilar(feature1, feature2);
	accuracy = abs(cosin_similary);
	if(accuracy < 0.5 ){
		label = "FALSE - Confidence: " + std::to_string(100-accuracy*100) + " %" + "- Cosin value: " + std::to_string(cosin_similary);
		cv::putText(merge, label, cv::Point(50, 50), cv::FONT_HERSHEY_DUPLEX, 1, cv::Scalar(0,0,255), 2, false);
	}
	else{
		label = "TRUE - Confidence: " + std::to_string(accuracy*100) + " %" + "- Cosin value: " + std::to_string(cosin_similary);
		cv::putText(merge, label, cv::Point(50, 50), cv::FONT_HERSHEY_DUPLEX, 1, cv::Scalar(0,255,0), 2, false);
	}
	
	cv::imwrite(path + "/" + name + "_.jpg", merge);
	//
	double finish_time = static_cast<double>(cv::getTickCount());
	double extract_time = (finish_time - start_time) / cv::getTickFrequency() * 1000;
	// 	//
	// 	totaltime += extract_time;
	// 	total_cosin += cosin_similary;
	// }
    std::cout << "-----------------------" << std::endl;
	std::cout << "Average time: "<< totaltime/100 << "ms" << std::endl;
    std::cout << "Average Cosin similarity: "<< total_cosin/100 << std::endl;

	delete face_engine;
	face_engine = nullptr;

	return 0;
}



int main(int argc, char* argv[])
{
	// return ExtractSimilary(argc, argv);
	return Extract_noAlign(argc, argv);
}