import numpy as np
import mxnet as mx
import cv2
from detect_service.detection.mtcnn.mtcnn_detector import MtcnnDetector
from detect_service.alignment.st_align import preprocess

class MtcnnEngine:

    def __init__(self, model_path):
        self.ctx = mx.cpu()
        self.image_size = [112, 112]
        self.det_threshold = [0.6,0.7,0.8]
        self.mtcnn_path = model_path
        detector = MtcnnDetector(model_folder=self.mtcnn_path, ctx=self.ctx, num_worker=1, accurate_landmark = True, threshold=self.det_threshold)
        self.detector = detector


    def get_faces(self, face_img):
        """

        """
        bbox, landmark = self.detector.detect_face(face_img, det_type = 0)
        if ret is None:
            return None
        if bbox.shape[0]==0:
            return None, 0
        num_face = bbox.shape[0]
        faces_aligned = []
        bboxs = []
        for i in range(0, num_face):
            bbox = bbox[i,0:4]
            points = landmark[i,:].reshape((2,5)).T
            nimg = preprocess(face_img, bbox, points, self.image_size)
            nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            aligned = np.transpose(nimg, (2,0,1))
            faces_aligned.append(aligned)
            bboxs.append(bbox)
        return faces_aligned, bboxs, num_face