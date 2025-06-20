import Input_Manager.InputManager as InputManager
from Object_Detection_Module.Obj_Detection import YOLODetector as ObjectDetector
from OCR_Module.OCR_Processor import OCRProcessor
from Currency_Module.curr import YOLODetector as CurrencyDetector
from Camera_Module.CameraModule import CameraModule

import cv2
import numpy

# Initialize camera
Camera = CameraModule(0)

# Setup logger
level = InputManager.logging.INFO
logger = InputManager.logging.getLogger()
logger.setLevel(level)
for handler in logger.handlers:
    handler.setLevel(level)

# Define scan codes for headset buttons
NEXT_TRACK = -176       # For Object Detection
PREV_TRACK = -177       # For OCR
PLAY_PAUSE = -179       # For Currency Detection

def main():
    try:
        input_manager = InputManager.InputManager()

        def handle_single_press(scan_code):
            if scan_code == NEXT_TRACK:
                try:
                    input_manager.speak("Running object detection")
                    InputManager.HapticFeedback.short_pulse()
                    detector = ObjectDetector("Object_Detection_Module/VOC_n100_runs/best.pt")
                    current_image = numpy.array(Camera.get_image(), dtype=numpy.uint8)
                    cv2.imwrite("Object_Detection_Module/current_image.jpg", current_image)
                    detector.run_inference(current_image)
                    detections = detector.process_results(normalize=True)
                    detector.visualize_detections("Object_Detection_Module/current_image.jpg", detections, "Object_Detection_Module/output_visualized.jpg")
                    if detections:
                        for det in detections:
                            input_manager.speak(f"{det['text']} detected")
                    else:
                        input_manager.speak("No objects detected")
                except Exception as e:
                    input_manager.speak(f"Object detection error")
                    logger.error(f"Object detection error: {e}")

            elif scan_code == PREV_TRACK:
                try:
                    input_manager.speak("Running OCR")
                    InputManager.HapticFeedback.short_pulse()
                    ocr_processor = OCRProcessor()
                    current_image = numpy.array(Camera.get_image(), dtype=numpy.uint8)
                    cv2.imwrite("OCR_Module/current_image.jpg", current_image)
                    ocr_processor.ocr_on_image("OCR_Module/current_image.jpg")
                    ocr_processor.save_annotated_image("OCR_Module/annotated_image.jpg")
                    ocr_processor.display_annotated_image("OCR_Module/annotated_image.jpg")
                except Exception as e:
                    input_manager.speak("OCR error")
                    logger.error(f"OCR error: {e}")

            elif scan_code == PLAY_PAUSE:
                try:
                    input_manager.speak("Running currency detection")
                    InputManager.HapticFeedback.short_pulse()
                    detector = CurrencyDetector("Currency_Module/cur_n100_runs/best.pt")
                    current_image = numpy.array(Camera.get_image(), dtype=numpy.uint8)
                    cv2.imwrite("Currency_Module/current_image.jpg", current_image)
                    detector.run_inference(current_image)
                    detections = detector.process_results(normalize=True)
                    detector.visualize_detections("Currency_Module/current_image.jpg", detections, "Currency_Module/output_visualized.jpg")
                    if detections:
                        for det in detections:
                            input_manager.speak(f"{det['text']} detected")
                    else:
                        input_manager.speak("No currency detected")
                except Exception as e:
                    input_manager.speak("Currency detection error")
                    logger.error(f"Currency detection error: {e}")

        # Register handler
        input_manager.set_action_handler('single', handle_single_press)

        # Start listening to headset buttons
        input_manager.start(scan_codes=[NEXT_TRACK, PREV_TRACK, PLAY_PAUSE])

        while True:
            InputManager.time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()