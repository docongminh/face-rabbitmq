#ifndef BASE_64_H
#define BASE_64_H

#include "base64.h"
#include <iostream>
#include <algorithm>
#include <stdexcept>
#include <opencv2/opencv.hpp>

namespace base64{
   std::string base64_encode(std::string const& s, bool url = false);
   std::string base64_encode(unsigned char const*, size_t len, bool url = false);
   std::string base64_encode_image(cv::Mat mat, bool url = false);


   std::string base64_decode(std::string const& s, bool remove_linebreaks = false);
   cv::Mat base64_decode_image(std::string const& s, bool url = false);
   
/*
    end of namespace
*/
}

#endif  /* BASE_64_H ! */