import cv2
import os
# import torch
import time
import numpy as np
from detection.retina_face.base_detection import DetectBase
from alignment.align import *


detector = DetectBase(
    net_type = 'slim',
    weight_path = './model_storage/retina_weights/slim_Final.pth',
    device='cpu',
    size=(480, 640),
    mean=[104, 117, 123],
    phase='test',
    confidence_threshold=0.6,
    nms_threshold=0.4,
    keep_top_k=750,
    top_k=5000
)
reference = get_reference_facial_points(default_square=True)


def get_faces(image):
    """
    Input : image 
    return list [(face_1_cropped, [x, y, xx, yy, confidence])]
    """
    img = np.float32(image)
    dets, landms = detector.detect(img)
    print(len(dets))
    print(len(landms))
    faces = []
    for idx, land in enumerate(landms):
        points = [[land[i], land[i+1]] for i in range(0, 10, 2)]
        warped_face = warp_and_crop_face(image, points, reference, crop_size=(112,112))
        faces.append((warped_face, dets[idx]))
        cv2.imwrite("test_{}.jpg".format(idx), warped_face)
    return faces

import glob
i = 0
for path in glob.glob("./imgs/*.jpg"):
    img_raw = cv2.imread(path)
    img = np.float32(img_raw)
    t1 = time.time()
    det, landms = detector.detect(img)
    dets = np.concatenate((det, landms), axis=1)
    print("Total time: ", time.time() - t1)
    for b in dets:
        text = "{:.4f}".format(b[4])
        b = list(map(int, b))
        cv2.rectangle(img_raw, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
        cx = b[0]
        cy = b[1] + 12
        cv2.putText(img_raw, text, (cx, cy),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

        # landms
        cv2.circle(img_raw, (b[5], b[6]), 1, (0, 0, 255), 4)
        cv2.circle(img_raw, (b[7], b[8]), 1, (0, 255, 255), 4)
        cv2.circle(img_raw, (b[9], b[10]), 1, (255, 0, 255), 4)
        cv2.circle(img_raw, (b[11], b[12]), 1, (0, 255, 0), 4)
        cv2.circle(img_raw, (b[13], b[14]), 1, (255, 0, 0), 4)
    # save image

    name = "imgs/{}_test.jpg".format(i)
    i+=1
    cv2.imwrite(name, img_raw)

#test