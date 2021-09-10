#include <iostream>
#include <time.h>
#include <opencv2/opencv.hpp>
#include "net.h"
#include "face_engine.h"
#include "utils.h"
using namespace engine;

int TestAlignFace(int argc, char* argv[]) {
	// 
	const char* root_path = "../models";
	cv::Mat img_src = cv::imread(argv[1]);
	// init engine & load model
	double start_load = static_cast<double>(cv::getTickCount());
	engine::FaceEngine* face_engine = new engine::FaceEngine();
	face_engine->LoadModel(root_path);
	double end_load = static_cast<double>(cv::getTickCount());
	double load_cost = (end_load - start_load) / cv::getTickFrequency() * 1000;
	std::cout << "load model cost: " << load_cost << "ms" << std::endl;
	//
	double average = 0;
	for(int j=0; j<1; j++){
		std::cout << "----------------------------" << std::endl;
		std::vector<utils::FaceInfo> faces;
		double start_detect = static_cast<double>(cv::getTickCount());
		face_engine->DetectFace(img_src, &faces);
		double end_detect = static_cast<double>(cv::getTickCount());
		double detect_cost = (end_detect - start_detect) / cv::getTickFrequency() * 1000;
		std::cout << "time detect cost: " << detect_cost << "ms" << std::endl;
		//
		double start_align = static_cast<double>(cv::getTickCount());
		for (int i = 0; i < static_cast<int>(faces.size()); ++i) {
			cv::Rect face = faces.at(i).location_;
			std::vector<cv::Point2f> keypoints;
			face_engine->ExtractKeypoints(img_src, face, &keypoints);
			cv::Mat face_aligned;
			face_engine->AlignFace(img_src, keypoints, &face_aligned);
			// std::cout << "aligned: " << face_aligned << std::endl;
			std::string name = "../images/" + std::to_string(i) + "_align.jpg";
			cv::imwrite(name.c_str(), face_aligned);
			for (int num = 0; num < 106; ++num) {
				cv::Point curr_pt = cv::Point(keypoints[num].x,
											keypoints[num].y);
				cv::circle(img_src, curr_pt, 1, cv::Scalar(255, 0, 255), 1);
			}
			
		}
		cv::imwrite("../images/landmark.jpg", img_src);
		double end_align = static_cast<double>(cv::getTickCount());
		double align_cost = (end_align - start_align) / cv::getTickFrequency() * 1000;
		std::cout << "time align cost: " << align_cost << "ms" << std::endl;
		double total = align_cost + detect_cost;
		average += total;
		std::cout << "time detect + align cost: " << total << "ms" << std::endl;
	}
	std::cout << "Average Time per 100 times loops test: "<< average/100 << std::endl;
	delete face_engine;
	face_engine = nullptr;
	
	return 0;
}

int main(int argc, char* argv[])
{
	return TestAlignFace(argc, argv);
}