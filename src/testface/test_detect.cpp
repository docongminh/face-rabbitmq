#include <iostream>
#include <time.h>
#include <opencv2/opencv.hpp>
#include "net.h"
#include "face_engine.h"
#include "utils.h"
using namespace engine;

int TestDetecter(int argc, char* argv[]) {
	const char* img_file = "../images/2_faces.jpg";
	cv::Mat img_src = cv::imread(img_file);
	const char* root_path = "../models";
	//
	double start_load = static_cast<double>(cv::getTickCount());
	engine::FaceEngine* face_engine = new engine::FaceEngine();
	face_engine->LoadModel(root_path);
	double end_load = static_cast<double>(cv::getTickCount());
	double load_cost = (end_load - start_load) / cv::getTickFrequency() * 1000;
	std::cout << "load model cost: " << load_cost << "ms" << std::endl;
	//
	std::vector<utils::FaceInfo> faces;
	for (int i=0; i<=10; i++){
		std::cout << "-----------------------" << std::endl;
		double start = static_cast<double>(cv::getTickCount());
		face_engine->DetectFace(img_src, &faces);
		
		// time
		double end = static_cast<double>(cv::getTickCount());
		double time_cost = (end - start) / cv::getTickFrequency() * 1000;
		//
		std::cout << "time detect cost: " << time_cost << "ms" << std::endl;
	}
	cv::Mat face1 = img_src(faces[0].location_).clone();
	cv::Mat face2 = img_src(faces[1].location_).clone();
	for (int i = 0; i < static_cast<int>(faces.size()); ++i) {
		utils::FaceInfo face_info = faces.at(i);
		cv::rectangle(img_src, face_info.location_, cv::Scalar(0, 255, 0), 2);
	#if 1
		for (int num = 0; num < 5; ++num) {
			cv::Point curr_pt = cv::Point(face_info.keypoints_[num],
										  face_info.keypoints_[num + 5]);
			cv::circle(img_src, curr_pt, 2, cv::Scalar(255, 0, 255), 2);
		}	
	#endif 
	}
	cv::imwrite("../images/retinaface_result.jpg", img_src);
	cv::imwrite("../images/face1.jpg", face1);
	cv::imwrite("../images/face2.jpg", face2);
	delete face_engine;
	face_engine = nullptr;

	return 0;
}

int main(int argc, char* argv[])
{
	return TestDetecter(argc, argv);
}