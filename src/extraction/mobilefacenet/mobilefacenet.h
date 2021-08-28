#ifndef MOBILEFACENET_H
#define MOBILEFACENET_H
#include "net.h"
#include "extractor.h"
// #include "opencv2/opencv.hpp"

namespace extract {
	class MobileFaceNet : public Extractor {
	public:
		MobileFaceNet();
		~MobileFaceNet();
		int LoadModel(const char* root_path);
		int ExtractFeature(const cv::Mat& face_aligned, std::vector<float>* embedding);
	private:
		ncnn::Net* mobile_net;
		ncnn::Mat ncnn_img;
		// std::vector<float> embedding_output;
	};
}

#endif // !MOBILEFACENET_H