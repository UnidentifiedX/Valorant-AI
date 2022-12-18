import cv2
import dxcam
import math
import keyboard
import numpy as np
from numpy import ndarray
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, QRunnable, QObject
from signals import DetectorSignals
import time
import torch
import win32gui

from utils.datasets import LoadImages, letterbox
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import TracedModel, time_synchronized

class Detector(QRunnable):
    def __init__(self):
        # QtCore.QThread.__init__(self)
        super(Detector, self).__init__()

        # initialise signals
        self.signals = DetectorSignals()

        self.device = torch.device('cuda:0')
        weights = "yolov7_custom2.pt"
        self.conf_thres = 0.5 # default 0.25
        self.iou_thres = 0.2 # default 0.45

        # Load model
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        imgsz = check_img_size(img_size=640, s=self.stride)  # check img_size

        self.model = TracedModel(self.model, self.device, img_size=640)
        self.model.half()  # to FP16

        # Set Dataloader
        self.dataset = LoadImages("", img_size=imgsz, stride=self.stride)

        # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[np.random.randint(0, 255) for _ in range(3)] for _ in self.names]

        # Run inference
        self.model(torch.zeros(1, 3, imgsz, imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once

    def run(self):
        camera = dxcam.create()
        camera.start(target_fps=200, video_mode=True)

        while True:
            loop_time = time.time()

            # Read image
            img0 = camera.get_latest_frame()

            # Padded resize
            img = letterbox(img0, 640, self.stride)[0]

            # Convert
            img = img.transpose(2, 0, 1) # to 3x416x416
            img = np.ascontiguousarray(img)

            t0 = time.time()
            img = torch.from_numpy(img).to(self.device)
            img = img.half() # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
                pred = self.model(img)[0]
            t2 = time_synchronized()

            # Apply NMS
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres)
            t3 = time_synchronized()

            # Process detections
            for i, det in enumerate(pred):  # detections per image
                s, im0, frame = '', img0, getattr(self.dataset, 'frame', 0)
                # gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh

            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    label = f'{self.names[int(cls)]} {conf:.2f}'
                    if self.names[int(cls)] == "enemy":
                        x_avg = int((int(xyxy[0]) + int(xyxy[2]))/2)
                        y_avg = int((int(xyxy[3]) + int(xyxy[1]))/2)

                        # pydirectinput.moveTo(x_avg, y_avg)
                        # pydirectinput.leftClick()

                    plot_one_box(xyxy, im0, label=label, color=self.colors[int(cls)], line_thickness=1)

            # Print time (inference + NMS)
            # print(f'{s}Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')

            # self.frame.emit(im0)
            # self.fps.emit(int(1/(time.time() - loop_time)))
            self.signals.frame.emit(im0)
            self.signals.fps.emit(int(1/(time.time() - loop_time)))