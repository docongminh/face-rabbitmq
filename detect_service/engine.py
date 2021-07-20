import numpy as np
import mxnet as mx
import cv2
from detect_service.detection.mtcnn.mtcnn_detector import MtcnnDetector
from detect_service.alignment.st_align import preprocess

class MtcnnEngine:
    def __init__(self, config):
        self.ctx = mx.cpu()
        self.config = config
        self.detector = MtcnnDetector(model_folder=self.config["mtcnn_path"],
                                    ctx=self.ctx,
                                    num_worker=1,
                                    accurate_landmark = True,
                                    threshold=self.config["det_threshold"])


    def get_faces(self, face_img):
        """
            Input: Image type numpy array
            Output: List of faces aligned
                    List of faces bouding box
                    Number of face in Input Image
        """
        bbox, landmark = self.detector.detect_face(face_img, det_type = 0)
        if bbox is None or landmark is None:
            return None
        if bbox.shape[0]==0:
            return None, 0
        num_face = bbox.shape[0]
        faces_aligned = []
        bboxs = []
        # align face
        for i in range(0, num_face):
            bbox = bbox[i,0:4]
            # landmarks format: [point1_x, point2_x,... point5_x, point1_y, ..., point5_y]
            # reshape (2, 5): [[point1_x, ..., point5_x,]
            #                   [point1_y, ..., point5_y]
            points = landmark[i,:].reshape((2,5)).T
            nimg = preprocess(face_img, bbox, points, self.config["image_size"])
            nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            aligned = np.transpose(nimg, (2,0,1)) # output (3, 112, 112)
            faces_aligned.append(aligned)
            bboxs.append(bbox)

        return faces_aligned, bboxs, num_face