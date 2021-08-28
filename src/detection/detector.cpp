#include "detector.h"
#include "retinaface.h"
#include "insightface.h"

namespace detect {

	Detecter* RetinafaceFactory::CreateDetecter() {
		return new RetinaFace();
	}
	// landmark
	Landmarker* InsightfaceLandmarkerFactory::CreateLandmarker() {
	return new InsightfaceLandmarker();
}
}