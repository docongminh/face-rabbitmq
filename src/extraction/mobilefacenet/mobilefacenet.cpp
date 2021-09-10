 #include<iostream>
#include "mobilefacenet.h"

namespace extract {
// 
	MobileFaceNet::MobileFaceNet(){
		mobile_net = new ncnn::Net();
	}
	int MobileFaceNet::LoadModel(const char* root_path) {
		std::string param_path = std::string(root_path) + "/extract/mobilefacenet/non-mask/mobilefacenet.param";
		std::string bin_path = std::string(root_path) + "/extract/mobilefacenet/non-mask/mobilefacenet.bin";
		if(mobile_net->load_param(param_path.c_str()) == -1 ||
			mobile_net->load_model(bin_path.c_str()) == -1){
				std::cout << "load model extract fail" << std::endl;
			}
		return 0;
	}

	MobileFaceNet::~MobileFaceNet() {
		if(mobile_net){
			mobile_net->clear();
		}
	}

	int MobileFaceNet::ExtractFeature(const cv::Mat& face_aligned, std::vector<float>* embedding) {
		// std::cout << "start extract embedding..." << std::endl;
		embedding->clear();
		ncnn::Mat ncnn_img = ncnn::Mat::from_pixels_resize(face_aligned.data, ncnn::Mat::PIXEL_BGR2RGB, face_aligned.cols, face_aligned.rows, 112, 112);
		ncnn::Extractor ex = mobile_net->create_extractor();
		// ex.set_num_threads(4);
		ex.set_light_mode(true);
		ex.input("data", ncnn_img);
		ncnn::Mat out;
		ex.extract("fc1", out);
		// with specified elements: use at() / operator[]
		// add new element: use push_back
		// embedding -> resize(128);

		for (int j = 0; j < 128; j++)
		{
			// embedding -> at(j) = out[j];
			embedding -> push_back(out[j]);
		}
		// cv::normalize(feature, embedding_output, cv::NORM_L2);

		return 0;
	}
}

