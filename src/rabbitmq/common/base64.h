#ifndef BASE64_H
#define BASE64_H
#include <string>

namespace base64 {
    /**
     *  Base 64 field
     */
    

    std::string base64_encode     (std::string const& s, bool url = false);
    std::string base64_encode_pem (std::string const& s);
    std::string base64_encode_mime(std::string const& s);

    std::string base64_decode(std::string const& s, bool remove_linebreaks = false);
    std::string base64_encode(unsigned char const*, size_t len, bool url = false);

    /**
     *  end namespace
     */
}

#endif /* BASE64_H */