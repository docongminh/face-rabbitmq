import torch
import numpy as np
from detection.retina_face.utils.box_utils import decode, decode_landm
from detection.retina_face.utils.nms import py_cpu_nms
from detection.retina_face.utils.timer import Timer 
from detection.retina_face.utils.prior_box import PriorBox
from detection.retina_face.config.net_config import net_dict
from detection.retina_face.base_utils import check_keys, remove_prefix
from detection.retina_face.preprocessing import DetectionTransform
from detection.retina_face.nets.retinaface import RetinaFace
from detection.retina_face.nets.slim import Slim
from detection.retina_face.nets.rfb import RFB


class DetectBase:
    """
        Raw base inference face detection
    """
    def __init__(self, net_type,
            weight_path,
            device,
            size,
            mean,
            phase,
            confidence_threshold,
            nms_threshold,
            keep_top_k,
            top_k
        ):
        self.transform = DetectionTransform(size, mean)
        self.config = net_dict[net_type]
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.keep_top_k = keep_top_k
        self.top_k = top_k
        self.size = size
        self.phase = phase
        self.net_type = net_type
        self.weight_path = weight_path
        self.device = device
        self.loader()
        self.load_model()

    def loader(self):
        """
            select network for model
        """
        if self.net_type == "mobile0.25":
            self.model = RetinaFace(cfg = self.config, phase = self.phase)
        elif self.net_type == "slim":
            self.model = Slim(cfg = self.config, phase = self.phase)
        elif self.net_type == "rfb":
            self.model = RFB(cfg = self.config, phase = self.phase)
        else:
            print("Don't support network!")
            exit(0)

        # load prior box
        priorbox = PriorBox(self.config, image_size=(self.size[0], self.size[1]))
        priors = priorbox.forward()
        priors = priors.to(self.device)

        self.prior_data = priors.data


    def load_model(self):
        """
            load model
        """
        print('Loading pretrained model from {}'.format(self.weight_path))
        if self.device == "cpu":
            weight_dict = torch.load(self.weight_path, map_location=lambda storage, loc: storage)
        elif self.device == "gpu":
            device = torch.cuda.current_device()
            weight_dict = torch.load(self.weight_path, map_location=lambda storage, loc: storage.cuda(device))
        # remove prefix
        if "state_dict" in weight_dict.keys():
            weight_dict = remove_prefix(weight_dict['state_dict'], 'module.')
        else:
            weight_dict = remove_prefix(weight_dict, 'module.')
        # check keys
        check_keys(self.model, weight_dict)
        # load weight
        self.model.load_state_dict(weight_dict, strict=False)
        # use for inference
        self.model.eval()
        if self.device == "cpu":
            self.model.to(torch.device("cpu"))
        elif self.device == "gpu":
            self.model.to(torch.device("cuda"))
    def get_ratio(self, image):
        """
            Get scale resize for heigh & width of image
            formula: h_ratio = new_h / old_h
                    w_ratio = new_w / old_w
            target : new_image = cv2.resize(image, None, None, fx=w_ratio, fy=h_ratio)
        """
        h, w, _ = image.shape
        h_ratio = float(self.size[0]) / float(h)
        w_ratio = float(self.size[1]) / float(w)

        return h_ratio, w_ratio

    def detect(self, image):
        """
            Execute detect face
        """
        h, w = self.size[0], self.size[1]
        h_ratio, w_ratio = self.get_ratio(image)
        # scale for top_left and bottom_right respectively
        # scale = torch.Tensor([w, h, w, h]) 
        box_scale = torch.Tensor([w/w_ratio, h/h_ratio, w/w_ratio, h/h_ratio])
        box_scale.to(self.device)
        # transform
        image = self.transform(image)

        image = torch.from_numpy(image).unsqueeze(0)
        image = image.to(self.device)
        # forward detect
        with torch.no_grad():
            loc, conf, landms = self.model(image)
        # boxes
        # boxes type [top_left_x, top_left_y, bottom_right_x, bottom_right_y]
        boxes = decode(loc.data.squeeze(0), self.prior_data, self.config['variance'])
        boxes = boxes * box_scale
        boxes = boxes.cpu().numpy()
        # scores
        scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
        # decode landmarks, point (x, y) center coordinate
        landms = decode_landm(landms.data.squeeze(0), self.prior_data, self.config['variance'])
        # scale for 5 points landmarks
        landms_scale = torch.Tensor([w/w_ratio, h/h_ratio, w/w_ratio, h/h_ratio,
                               w/w_ratio, h/h_ratio, w/w_ratio, h/h_ratio,
                               w/w_ratio, h/h_ratio])
        landms_scale.to(self.device)
        landms = landms * landms_scale
        landms = landms.cpu().numpy()

        # ignore low scores
        inds = np.where(scores > self.confidence_threshold)[0]
        boxes = boxes[inds]
        landms = landms[inds]
        scores = scores[inds]

        # keep top-K before NMS
        order = scores.argsort()[::-1][:self.top_k]
        boxes = boxes[order]
        landms = landms[order]
        scores = scores[order]

        # do NMS
        dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
        keep = py_cpu_nms(dets, self.nms_threshold)
        dets = dets[keep, :]
        landms = landms[keep]

        # keep top-K faster NMS
        dets = dets[:self.keep_top_k, :]
        landms = landms[:self.keep_top_k, :] 
        # dets = np.concatenate((dets, landms), axis=1)
        return dets, landms
        
        
        

        


        


