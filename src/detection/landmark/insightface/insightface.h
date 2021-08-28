#ifndef INSIGHTFACE_LANDMARKER_H
#define INSIGHTFACE_LANDMARKER_H

#include "detector.h"
#include "net.h"

namespace detect {
    class InsightfaceLandmarker : public Landmarker {
    public:
        InsightfaceLandmarker();
        ~InsightfaceLandmarker();

        int LoadModel(const char* root_path);
        int ExtractKeypoints(const cv::Mat& img_src,
            const cv::Rect& face, std::vector<cv::Point2f>* keypoints);

    private:
        ncnn::Net* insightface_landmarker_net_;
        bool initialized;
    };

}

#endif // !INSIGHTFACE_LANDMARKER_H

