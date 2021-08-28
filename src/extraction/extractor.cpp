#include "extractor.h"
#include "mobilefacenet.h"

namespace extract {
    Extractor* MobileFacenetFactory::CreateExtractor(){
        return new MobileFaceNet();
    }
}