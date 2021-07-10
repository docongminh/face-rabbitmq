import cv2
import numpy as np
from numpy import random

class Compose:
    """
    Composes several augmentations together. For inference.
    Args:
        transforms (List[Transform]): list of transforms to compose.
    Example:
        augmentations.Compose([
            transforms.CenterCrop(10),
            transforms.ToTensor(),
        ])
    source: idea come from : https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/blob/f0578bcb789a81f9e03d6c8aa999b71872f0d1a3/paddle/vision/transforms/transforms.py#L59
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        for trans in self.transforms:
            img = trans(img)
        return img

class Resize:
    """
        resize image to size[heigh, weight]
        return: image resized
    """
    def __init__(self, size):
        self.height = size[0]
        self.width = size[1]

    def __call__(self, image):
        
        h, w, _ = image.shape
        h_ratio = float(self.height) / float(h)
        w_ratio = float(self.width) / float(w)
        # image = cv2.resize(image, (self.width, self.height)) 
        image = cv2.resize(image, None, None, fx=w_ratio, fy=h_ratio, interpolation=cv2.INTER_LINEAR)
        return image

class Normalize:
    def __init__(self, mean):
        self.mean = np.array(mean, dtype=np.float32)
    
    def __call__(self, image):
        image = image.astype(np.float32)
        image -= self.mean
        
        return image.astype(np.float32)

class Transpose:
    def __call__(self, image):
        return image.transpose(2, 0, 1)


