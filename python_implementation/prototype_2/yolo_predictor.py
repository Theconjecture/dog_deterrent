import cv2
import numpy as np
import yaml
from yaml.loader import SafeLoader

class YOLODetector:
    def __init__(self, model_path, data_yaml):
        with open(data_yaml, mode='r') as f:
            data = yaml.load(f, Loader=SafeLoader)
        self.labels = data['names']
        self.model = cv2.dnn.readNetFromONNX(model_path)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1/255, (640, 640), swapRB=True, crop=False)
        self.model.setInput(blob)
        outputs = self.model.forward()[0]
        
        # Process detections
        boxes = []
        confidences = []
        for detection in outputs:
            confidence = detection[4]
            if confidence > 0.6:
                class_id = np.argmax(detection[5:])
                if self.labels[class_id] == "Dog":
                    # Extract box coordinates (x1,y1,x2,y2)
                    #x1, y1, w, h = detection[:4] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                    #boxes.append([int(x1-w/2), int(y1-h/2), int(x1+w/2), int(y1+h/2)])
                    # Convert [center_x, center_y, width, height] -> [x1, y1, x2, y2]
                    cx, cy, w, h = detection[:4]
                    frame_h, frame_w = frame.shape[:2]

                    x1 = int((cx - w / 2) * frame_w)
                    y1 = int((cy - h / 2) * frame_h)
                    x2 = int((cx + w / 2) * frame_w)
                    y2 = int((cy + h / 2) * frame_h)

                    boxes.append([x1, y1, x2, y2])

                    confidences.append(float(confidence))
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.6, 0.4)
        return boxes, indices  # Return detection data for visualization 
