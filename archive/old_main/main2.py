import threading
import queue
import time
import logging
import winsound
import pyttsx3
import keyboard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HapticFeedback:
    @staticmethod
    def beep(frequency=500, duration=100):
        winsound.Beep(frequency, duration)

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

class InputDetector:
    def __init__(self, button1='a', button2='b', long_press_threshold=1.0, multi_press_threshold=0.5):
        self.button1 = button1
        self.button2 = button2
        self.long_press_threshold = long_press_threshold
        self.multi_press_threshold = multi_press_threshold
        self.last_press_time = 0
        self.press_count = 0
        self.input_queue = queue.Queue()

    def detect_input(self):
        while True:
            if keyboard.is_pressed(self.button1):
                self._handle_button_press(self.button1)
            elif keyboard.is_pressed(self.button2):
                self._handle_button_press(self.button2)
            time.sleep(0.01)

    def _handle_button_press(self, button):
        start_time = time.time()
        while keyboard.is_pressed(button):
            time.sleep(0.01)
        press_duration = time.time() - start_time

        if press_duration >= self.long_press_threshold:
            self.input_queue.put((button, 'long'))
            logging.info(f"{button} long press detected")
        else:
            current_time = time.time()
            if current_time - self.last_press_time < self.multi_press_threshold:
                self.press_count += 1
            else:
                self.press_count = 1

            self.last_press_time = current_time

            if self.press_count >= 2:
                self.input_queue.put((button, f'multi_{self.press_count}'))
                logging.info(f"{button} multiple presses detected: {self.press_count}")
            else:
                self.input_queue.put((button, 'short'))
                logging.info(f"{button} short press detected")

class MainLoop:
    def __init__(self):
        self.haptic_feedback = HapticFeedback()
        self.text_to_speech = TextToSpeech()
        self.input_detector = InputDetector()
        self.running = True

    def start(self):
        input_thread = threading.Thread(target=self.input_detector.detect_input, daemon=True)
        input_thread.start()

        while self.running:
            if not self.input_detector.input_queue.empty():
                button, press_type = self.input_detector.input_queue.get()
                self._handle_input(button, press_type)
            time.sleep(0.01)

    def _handle_input(self, button, press_type):
        if press_type == 'short':
            self.haptic_feedback.beep()
            self.text_to_speech.speak(f"{button} short press")
        elif press_type == 'long':
            self.haptic_feedback.beep(frequency=700, duration=200)
            self.text_to_speech.speak(f"{button} long press")
        elif press_type.startswith('multi'):
            count = int(press_type.split('_')[1])
            self.haptic_feedback.beep(frequency=300, duration=50)
            self.text_to_speech.speak(f"{button} pressed {count} times")

if __name__ == "__main__":
    main_loop = MainLoop()
    main_loop.start()