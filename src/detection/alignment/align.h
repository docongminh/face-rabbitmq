#ifndef FACE_ALIGN_H
#define FACE_ALIGN_H

#include "opencv2/core.hpp"

namespace detect {
    class Aligner {
    public:
        Aligner();
        ~Aligner();

        int AlignFace(const cv::Mat & img_src,
            const std::vector<cv::Point2f>& keypoints, cv::Mat * face_aligned);

    private:
        class Impl;
        Impl* impl_;
    };

}

#endif // !FACE_ALIGN_H