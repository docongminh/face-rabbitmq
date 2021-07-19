from detection.retina_face.transforms import Compose, Resize, Normalize, Transpose

class DetectionTransform:
    """
    
    """
    def __init__(self, size, mean):
        self.transform = Compose([
            Resize(size),
            Normalize(mean),
            Transpose()
        ])
    
    def __call__(self, image):
        image = self.transform(image)

        return image
