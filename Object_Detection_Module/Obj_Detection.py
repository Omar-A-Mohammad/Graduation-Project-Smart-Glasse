import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cv2
import numpy as np
from ultralytics import YOLO
from Camera_Module.CameraModule import CameraModule
import Input_Manager.InputManager as InputManager

class YOLODetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def run_inference(self, image):
        self.results = self.model(image)
        return self.results

    def process_results(self, normalize=False):
        detections = []
        for result in self.results:
            img_w, img_h = result.orig_shape[1], result.orig_shape[0]
            for box in result.boxes:
                x_center = float(box.xywh[0][0])
                y_center = float(box.xywh[0][1])
                width = float(box.xywh[0][2])
                height = float(box.xywh[0][3])

                if normalize:
                    x_center /= img_w
                    y_center /= img_h
                    width /= img_w
                    height /= img_h

                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])

                detections.append({
                    "text": class_name,
                    "confidence": confidence,
                    "box": [  # أضفناها بدل bbox علشان تتوافق مع الكود الرئيسي
                        int(box.xyxy[0][0]),
                        int(box.xyxy[0][1]),
                        int(box.xyxy[0][2]),
                        int(box.xyxy[0][3])
                    ]
                })
        return detections

    def visualize_detections(self, image_path, detections, output_path):
        image = cv2.imread(image_path)
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = det["text"]
            confidence = det["confidence"]

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imwrite(output_path, image)


def main():
    camera = CameraModule(0)  # Use internal camera
    detector = YOLODetector("Object_Detection_Module/VOC_n100_runs/best.pt")
    input_manager = InputManager.InputManager()

    key = "KEY_MEDIA_NEXT_TRACK"  # الزر الأمامي في السماعة

    def detect_on_press(k):
        InputManager.HapticFeedback.double_pulse()
        input_manager.speak("Running object detection")

        image = camera.get_image()
        if image is None:
            input_manager.speak("Could not capture image")
            return

        detector.run_inference(image)
        detections = detector.process_results(normalize=True)

        if detections:
            for d in detections:
                input_manager.speak(f"{d['text']} detected")
        else:
            input_manager.speak("No objects detected")

    input_manager.set_action_handler("double", detect_on_press)
    input_manager.start()

    while True:
        InputManager.time.sleep(0.1)

if __name__ == "__main__":
    main()
