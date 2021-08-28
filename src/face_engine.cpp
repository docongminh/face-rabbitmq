#include <iostream>
#include "face_engine.h"
#include "detector.h"
#include "extractor.h"
#include "align.h"

namespace engine {
    class FaceEngine::Impl {
        public:
            Impl() {
                detecter_factory_ = new detect::RetinafaceFactory();
                landmarker_factory_ = new detect::InsightfaceLandmarkerFactory();
                mobile_net_factory_ = new extract::MobileFacenetFactory();

                
                detecter_ = detecter_factory_->CreateDetecter();
                landmarker_ = landmarker_factory_->CreateLandmarker();
                extract_ = mobile_net_factory_-> CreateExtractor();

                aligner_ = new detect::Aligner();
                initialized_ = false;
            }

            ~Impl() {
                if (detecter_) {
                    delete detecter_;
                    detecter_ = nullptr;
                }

                if (landmarker_) {
                    delete landmarker_;
                    landmarker_ = nullptr;
                }

                if (detecter_factory_) {
                    delete detecter_factory_;
                    detecter_factory_ = nullptr;
                }

                if (landmarker_factory_) {
                    delete landmarker_factory_;
                    landmarker_factory_ = nullptr;
                }

                if (mobile_net_factory_){
                    delete mobile_net_factory_;
                    mobile_net_factory_ = nullptr;
                }
            }

            int LoadModel(const char* root_path) {
                if (detecter_->LoadModel(root_path) != 0) {
                    std::cout << "load face detecter failed." << std::endl;
                    return 10000;
                }

                if (landmarker_->LoadModel(root_path) != 0) {
                    std::cout << "load face landmarker failed." << std::endl;
                    return 10000;
                }

                if (extract_->LoadModel(root_path) != 0){
                    std::cout << "load mobilefacenet failed." << std::endl;
                    return 10000;
                }
                initialized_ = true;

                return 0;
            }
            inline int DetectFace(const cv::Mat& img_src, std::vector<utils::FaceInfo>* faces) {
                return detecter_->DetectFace(img_src, faces);
            }
            inline int ExtractKeypoints(const cv::Mat& img_src,
                const cv::Rect& face, std::vector<cv::Point2f>* keypoints) {
                return landmarker_->ExtractKeypoints(img_src, face, keypoints);
            }
            inline int AlignFace(const cv::Mat& img_src, const std::vector<cv::Point2f>& keypoints, cv::Mat * face_aligned) {
                return aligner_->AlignFace(img_src, keypoints, face_aligned);
            }
            inline int ExtractFeature(const cv::Mat& face_aligned, std::vector<float>* embedding){
                return extract_->ExtractFeature(face_aligned, embedding);
            }

        private:
            detect::DetecterFactory* detecter_factory_ = nullptr;
            detect::LandmarkerFactory* landmarker_factory_ = nullptr;
            extract::MobileFacenetFactory* mobile_net_factory_ = nullptr;

        private:
            bool initialized_;
            detect::Aligner* aligner_ = nullptr;
            detect::Detecter* detecter_ = nullptr;
            detect::Landmarker* landmarker_ = nullptr;
            extract::Extractor* extract_ = nullptr;

    };

    FaceEngine::FaceEngine() {
        impl_ = new FaceEngine::Impl();
    }

    FaceEngine::~FaceEngine() {
        if (impl_) {
            delete impl_;
            impl_ = nullptr;
        }
    }

    int FaceEngine::LoadModel(const char* root_path) {
        return impl_->LoadModel(root_path);
    }

    int FaceEngine::DetectFace(const cv::Mat& img_src, std::vector<utils::FaceInfo>* faces) {
        return impl_->DetectFace(img_src, faces);
    }

    int FaceEngine::ExtractKeypoints(const cv::Mat& img_src,
        const cv::Rect& face, std::vector<cv::Point2f>* keypoints) {
        return impl_->ExtractKeypoints(img_src, face, keypoints);
    }

    int FaceEngine::AlignFace(const cv::Mat& img_src, const std::vector<cv::Point2f>& keypoints, cv::Mat* face_aligned) {
        return impl_->AlignFace(img_src, keypoints, face_aligned);
    }

    int FaceEngine::ExtractFeature(const cv::Mat& face_aligned, std::vector<float>* embedding){
        return impl_->ExtractFeature(face_aligned, embedding);
    }
}