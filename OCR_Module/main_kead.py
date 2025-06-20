import Input_Manager.InputManager as InputManager
from Object_Detection_Module.Obj_Detection import YOLODetector as ObjectDetector
from OCR_Module.OCR_Processor import OCRProcessor
from Currency_Module.curr import YOLODetector as CurrencyDetector
from Camera_Module.CameraModule import CameraModule

import json
import cv2
import numpy

# Initialize the camera module with the IP address of the IPCamera
Camera = CameraModule("http://192.168.148.153:8080") # IPCamera changes the IP when you reconnect to your wifi, so you need to update it here as well.

# Set up logging
level = InputManager.logging.INFO
logger = InputManager.logging.getLogger()
logger.setLevel(level)
for handler in logger.handlers:
    handler.setLevel(level)

def main():
    try:
        input_manager = InputManager.InputManager()
        keys = list(input_manager.key_detectors.keys())
        key1 = keys[0]
        key2 = keys[1]
        logger.info(f"Listening for key presses: {key1} and {key2}")
        logger.info("Press Ctrl+C to exit.")

        # EXAMPLE: Customize action handlers
        # def custom_single_handler(key):
        #     HapticFeedback.short_pulse()
        #     input_manager.speak(f"Custom action for {key} single press")
        # input_manager.set_action_handler('single', custom_single_handler)
        

        ### Main Menu actions ###

        def MainMenu_SinglePress(key):
            """
            Handle single press actions for the main menu.
            :param key: The key that was pressed.
            """
            InputManager.HapticFeedback.short_pulse()
            input_manager.speak("Single press detected")

        def MainMenu_DoublePress(key):
            """
            Handle double press actions for the main menu.
            :param key: The key that was pressed.
            """
            InputManager.HapticFeedback.double_pulse()

            if key == key1:
                try:
                    input_manager.speak("Running object detection")
                    detector = ObjectDetector("Object_Detection_Module/VOC_n100_runs/best.pt")

                    current_image = numpy.array(Camera.get_image(),dtype=numpy.uint8)
                    cv2.imwrite("Object_Detection_Module/current_image.jpg", current_image)
                    current_image_path = "Object_Detection_Module/current_image.jpg"
                    detector.run_inference(current_image)
                    detections = detector.process_results(normalize=True)
                    detector.visualize_detections(current_image_path, detections, "Object_Detection_Module/output_visualized.jpg")
                    
                    print(detections,"\n")
                    
                    if detections:
                        for i in range(len(detections)):
                            print(f"Detection {i+1}:")
                            print(f"Class: {detections[i]['text']}")
                            input_manager.speak(f"{detections[i]['text']} detected")
                            print(f"Confidence: {detections[i]['confidence']:.2f}")
                    else:
                        print("No detections found.")

                except Exception as e:
                    input_manager.speak(f"Error running object detection: {str(e)}")
                    logger.error(f"Error running object detection: {str(e)}")

            elif key == key2:
                try:
                    input_manager.speak("Running currency detection")
                    detector = CurrencyDetector("Currency_Module/cur_n100_runs/best.pt")
                    
                    current_image = numpy.array(Camera.get_image(),dtype=numpy.uint8)
                    cv2.imwrite("Currency_Module/current_image.jpg", current_image)
                    current_image_path = "Currency_Module/current_image.jpg"
                    detector.run_inference(current_image)
                    detections = detector.process_results(normalize=True)
                    detector.visualize_detections(current_image_path, detections, "Currency_Module/output_visualized.jpg")
                    
                    print(detections,"\n")
                    
                    if detections:
                        for i in range(len(detections)):
                            print(f"Detection {i+1}:")
                            print(f"Class: {detections[i]['text']}")
                            input_manager.speak(f"{detections[i]['text']} detected")
                            print(f"Confidence: {detections[i]['confidence']:.2f}")
                    else:
                        print("No detections found.")

                except Exception as e:
                    input_manager.speak(f"Error running currency detection: {str(e)}")
                    logger.error(f"Error running currency detection: {str(e)}")

        def MainMenu_TriplePress(key):
            """
            Handle triple press actions for the main menu.
            :param key: The key that was pressed.
            """
            InputManager.HapticFeedback.triple_pulse()


            if key == key1:
                try:
                    input_manager.speak("Running object detection")
                    detector = ObjectDetector("Object_Detection_Module/VOC_n100_runs/best.pt")
                    detector.run_inference(Camera.get_image())
                    detections = detector.process_results(normalize=True)
                    detector.visualize_detections("Object_Detection_Module/cars_on_road.jpeg", detections, "Object_Detection_Module/output_visualized.jpg")
                except:
                    input_manager.speak("Error running object detection")
                    logger.error("Error running object detection")

            elif key == key2:
                try:
                    input_manager.speak("Running OCR")
                    ocr_processor = OCRProcessor()

                    current_image = numpy.array(Camera.get_image(),dtype=numpy.uint8)
                    cv2.imwrite("OCR_Module/current_image.jpg", current_image)
                    current_image_path = "OCR_Module/current_image.jpg"

                    ocr_processor.ocr_on_image(current_image_path)
                    ocr_processor.save_annotated_image("OCR_Module/annotated_image.jpg")
                    ocr_processor.display_annotated_image("OCR_Module/annotated_image.jpg")
                except Exception as e:
                    input_manager.speak(f"Error running OCR: {str(e)}")
                    logger.error(f"Error running OCR: {str(e)}")

        def MainMenu_Hold(key):
            """
            Handle hold actions for the main menu.
            :param key: The key that was pressed.
            """

            InputManager.HapticFeedback.long_pulse()
            if key == key1:
                try:
                    input_manager.speak("Running object detection")
                    detector = ObjectDetector("Object_Detection_Module/VOC_n100_runs/best.pt")
                    detector.run_inference(Camera.get_image())
                    detections = detector.process_results(normalize=True)
                    detector.visualize_detections("Object_Detection_Module/cars_on_road.jpeg", detections, "Object_Detection_Module/output_visualized.jpg")
                except Exception as e:
                    input_manager.speak(f"Error running object detection: {str(e)}")
                    logger.error(f"Error running object detection: {str(e)}")

            elif key == key2:
                try:
                    input_manager.speak("Running OCR")
                    ocr_processor = OCRProcessor()
                    ocr_processor.ocr_on_image(Camera.get_image())
                    ocr_processor.display_annotated_image("Object_Detection_Module/cars_on_road.jpeg")
                except Exception as e:
                    input_manager.speak(f"Error running OCR: {str(e)}")
                    logger.error(f"Error running OCR: {str(e)}")
    
        ### Set action handlers for the main menu ###
        input_manager.set_action_handler('single', MainMenu_SinglePress)
        input_manager.set_action_handler('double', MainMenu_DoublePress)
        input_manager.set_action_handler('triple', MainMenu_TriplePress)
        input_manager.set_action_handler('hold', MainMenu_Hold)

        input_manager.start()
        
        while True:
            InputManager.time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()