import threading
import time
import logging
import winsound
import pyttsx3
from pynput import keyboard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FeedbackManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.lock = threading.Lock()
        self.latest_text = None
        
    def speak(self, text):
        with self.lock:
            self.latest_text = text
            threading.Thread(target=self._process_speech, daemon=True).start()
    
    def _process_speech(self):
        with self.lock:
            if self.latest_text:
                self.engine.stop()  # Discard previous requests
                self.engine.startLoop(False)
                self.engine.say(self.latest_text)
                self.engine.endLoop()
                self.latest_text = None
    
    def haptic_feedback(self, frequency=1000, duration=200):
        winsound.Beep(frequency, duration)

class KeyListener:
    SHORT_PRESS_THRESHOLD = 0.1  # Seconds
    LONG_PRESS_THRESHOLD = 1.0   # Seconds
    MULTIPLE_PRESS_WINDOW = 0.5  # Seconds

    def __init__(self, feedback_manager, keys=['a', 's']):
        self.feedback_manager = feedback_manager
        self.keys = keys
        self.pressed_times = {}
        self.press_sequences = {}
        self.input_lock = threading.Lock()
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        
    def start(self):
        self.listener.start()
    
    def _on_press(self, key):
        with self.input_lock:
            try:
                key_char = key.char.lower()
                if key_char in self.keys and key_char not in self.pressed_times:
                    self.pressed_times[key_char] = time.time()
            except AttributeError:
                pass
    
    def _on_release(self, key):
        with self.input_lock:
            try:
                key_char = key.char.lower()
                if key_char in self.keys and key_char in self.pressed_times:
                    press_duration = time.time() - self.pressed_times[key_char]
                    self._process_keypress(key_char, press_duration)
                    del self.pressed_times[key_char]
            except AttributeError:
                pass
    
    def _process_keypress(self, key, duration):
        if key not in self.press_sequences:
            self.press_sequences[key] = []
        
        self.press_sequences[key].append(time.time())
        self.press_sequences[key] = [t for t in self.press_sequences[key] if time.time() - t <= self.MULTIPLE_PRESS_WINDOW]
        
        if len(self.press_sequences[key]) > 1:
            logging.info(f"Multiple presses detected for '{key}'")
            self.feedback_manager.speak(f"Multiple presses of {key}")
            self.feedback_manager.haptic_feedback(1200, 200)
            self.press_sequences[key] = []  # Reset sequence
        elif duration >= self.LONG_PRESS_THRESHOLD:
            logging.info(f"Long press detected for '{key}'")
            self.feedback_manager.speak(f"Long press of {key}")
            self.feedback_manager.haptic_feedback(600, 400)
        elif duration >= self.SHORT_PRESS_THRESHOLD:
            logging.info(f"Short press detected for '{key}'")
            self.feedback_manager.speak(f"Short press of {key}")
            self.feedback_manager.haptic_feedback(1000, 200)

class MainLoop:
    def __init__(self):
        self.feedback_manager = FeedbackManager()
        self.key_listener = KeyListener(self.feedback_manager)
        
    def run(self):
        logging.info("Starting main loop...")
        self.key_listener.start()
        while True:
            time.sleep(1)  # Keep the main thread alive

if __name__ == "__main__":
    main_loop = MainLoop()
    main_loop.run()
