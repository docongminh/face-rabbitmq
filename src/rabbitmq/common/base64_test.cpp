#include "base64.h"
#include <iostream>
#include <chrono>

using namespace base64;
int main() {

    const std::string data ="qwertyuiop[]asdfghjkl;'zxcvbnm,./1234567890\n";

    auto time_encoding_begin = std::chrono::system_clock::now();
    std::string encoded = base64::base64_encode(reinterpret_cast<const unsigned char*>(data.c_str()), data.length());
    auto time_encoding_end = std::chrono::system_clock::now();
    std::cout << encoded <<std::endl;
    auto time_decoding_begin = std::chrono::system_clock::now();
    std::string decoded = base64::base64_decode(encoded);
    auto time_decoding_end = std::chrono::system_clock::now();

    std::chrono::duration<double> duration_encoding = time_encoding_end - time_encoding_begin;
    std::chrono::duration<double> duration_decoding = time_decoding_end - time_decoding_begin;

    std::cout << "Encoding took: " << duration_encoding.count() << std::endl;
    std::cout << "Decoding took: " << duration_decoding.count() << std::endl;

    if (decoded != data) {
      std::cout << "Strings differ!" << std::endl;
      return 1;
    }
    else{
      std::cout << "Success" << std::endl;
    }
    return 0;
}