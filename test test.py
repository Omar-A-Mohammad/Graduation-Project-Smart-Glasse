from Camera_Module.LabCameraModule import LabCameraModule
import Input_Manager.InputManager as InputManager
from Object_Detection_Module.Obj_Detection import YOLODetector as ObjectDetector
from OCR_Module.OCR_Processor import OCRProcessor
from Currency_Module.curr import YOLODetector as CurrencyDetector

from pynput import keyboard
from typing import Optional
import numpy
import cv2
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
input_manager = InputManager.InputManager()
Camera = LabCameraModule(source=0)

# Load object detection model once
detector = ObjectDetector("Object_Detection_Module/VOC_n100_runs/best.pt")

def on_press(key: keyboard.Key) -> None:
    print(f"[DEBUG] Key pressed: {key}")
    if isinstance(key, keyboard.Key):
        if key == keyboard.Key.media_play_pause:
            print("ACTION: Play/Pause button pressed!")
            input_manager.speak("Object detection is not estimated")

        elif key == keyboard.Key.media_next:
            print("ACTION: Next Track button pressed!")
            try:
                input_manager.speak("Running currency detection")
                detector = CurrencyDetector("Currency_Module/cur_n100_runs/best.pt")
                current_image = numpy.array(Camera.get_image(), dtype=numpy.uint8)
                cv2.imwrite("Currency_Module/current_image.jpg", current_image)
                current_image_path = "Currency_Module/current_image.jpg"

                detector.run_inference(current_image)
                detections = detector.process_results(normalize=True)
                detector.visualize_detections(current_image_path, detections, "Currency_Module/output_visualized.jpg")

                print(detections, "\n")

                if detections:
                    for i in range(len(detections)):
                        print(f"Detection {i+1}:")
                        print(f"Class: {detections[i]['text']}")
                        input_manager.speak(f"{detections[i]['text']} detected")
                        print(f"Confidence: {detections[i]['confidence']:.2f}")
                else:
                    print("No detections found.")
                    input_manager.speak("No currency detected")

            except Exception as e:
                input_manager.speak(f"Error running currency detection: {str(e)}")
                logger.error(f"Error running currency detection: {str(e)}")

        elif key == keyboard.Key.media_previous:
            print("ACTION: Previous Track button pressed!")
            input_manager.speak("OCR reading not yet implemented.")

        else:
            print(f'Special key {key} pressed')

    elif hasattr(key, 'char'):
        print(f'Alphanumeric key {key.char} pressed')
    else:
        print(f'Unknown key: {key}')

def on_release(key: keyboard.Key) -> Optional[bool]:
    print(f"[DEBUG] Key released: {key}")
    if key == keyboard.Key.esc:
        print("ESC pressed. Exiting listener...")
        return False

print("Listening for media key presses...")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("Listener stopped.")
