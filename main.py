from Input_Manager.InputManager import *
from Object_Detection_Module.Obj_Detection import YOLODetector as ObjectDetector
from OCR_Module.OCR_Processor import OCRProcessor
from Currency_Module.curr import YOLODetector as CurrencyDetector

# Set up logging
level = logging.INFO
logger = logging.getLogger()
logger.setLevel(level)
for handler in logger.handlers:
    handler.setLevel(level)

def main():
    try:
        input_manager = InputManager()
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
        
        # Main Menu actions
        def MainMenu_DoublePress(key):
            HapticFeedback.short_pulse()
            if key == key1:
                input_manager.speak("Running object detection")
                detector = ObjectDetector("Object_Detection_Module/VOC_n100_runs/best.pt")
                #detector.run_inference()
            elif key == key2:
                input_manager.speak("Running currency detection")
                detector = CurrencyDetector("Currency_Module/currency_model.pt")
                #detector.run_inference()
            else:
                input_manager.speak(f"Unknown key: {key}")   
            input_manager.speak(f"{key} double press detected, running object detection")
        input_manager.set_action_handler('double', MainMenu_DoublePress)
        

        input_manager.start()
        
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        input_manager.stop()

if __name__ == "__main__":
    main()