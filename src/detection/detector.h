#ifndef DETECTOR_H
#define DETECTOR_H
#include "opencv2/core.hpp"
#include "utils.h"

namespace detect {
    // Base detect
    class Detecter {
    public:
        virtual ~Detecter() {};
        virtual int LoadModel(const char* root_path) = 0;
        virtual int DetectFace(const cv::Mat& img_src, std::vector<utils::FaceInfo>* faces) = 0;

    };
    class Landmarker {
    public:
        virtual ~Landmarker() {};
        virtual int LoadModel(const char* root_path) = 0;
        virtual int ExtractKeypoints(const cv::Mat& img_src,
            const cv::Rect& face, std::vector<cv::Point2f>* keypoints) = 0;
    };
    // Factory
    // Detect 
    class DetecterFactory {
    public:
        virtual Detecter* CreateDetecter() = 0;
        virtual ~DetecterFactory() {};
    };
    // Landmark
    class LandmarkerFactory {
    public:
        virtual Landmarker* CreateLandmarker() = 0;
        virtual ~LandmarkerFactory() {}
    };
    // Implement
    // Retina face detector
    class RetinafaceFactory : public DetecterFactory {
    public:
        RetinafaceFactory() {}
        ~RetinafaceFactory() {}
        Detecter* CreateDetecter();
    };
    // Landmark
    class InsightfaceLandmarkerFactory : public LandmarkerFactory {
    public:
        InsightfaceLandmarkerFactory(){}
        Landmarker* CreateLandmarker();
        ~InsightfaceLandmarkerFactory() {}
    };

}

#endif // !DETECTOR_H

