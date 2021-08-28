#include <vector>
#include "utils.h"
#include "opencv2/core.hpp"

namespace engine {
    class FaceEngine {
        public:
            FaceEngine();
            ~FaceEngine();
            //
            int LoadModel(const char* root_path);
            //
            int DetectFace(const cv::Mat& img_src, std::vector<utils::FaceInfo>* faces);
            int ExtractKeypoints(const cv::Mat& img_src, const cv::Rect& face, std::vector<cv::Point2f>* keypoints);
            int AlignFace(const cv::Mat& img_src, const std::vector<cv::Point2f>& keypoints, cv::Mat* face_aligned);
            int ExtractFeature(const cv::Mat& face_aligned, std::vector<float>* embedding);

        private:
            class Impl;
            Impl* impl_;

    };

}
