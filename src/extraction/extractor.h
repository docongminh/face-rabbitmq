#ifndef EXTRACT_H
#define EXTRACT_H
#include"opencv2/core.hpp"

namespace extract {
    class Extractor {
        public:
            virtual ~Extractor() {};
            virtual int LoadModel(const char* root_path) = 0;
            virtual int ExtractFeature(const cv::Mat& face_aligned, std::vector<float>* embedding) = 0;
    };

    class Factory{
        public:
            virtual Extractor* CreateExtractor() = 0;
            virtual ~Factory() {};
    };

    class MobileFacenetFactory : public Factory{
        public:
            MobileFacenetFactory() {};
            ~MobileFacenetFactory() {};
            Extractor* CreateExtractor();
    };
}


#endif  //!EXTRACT_H