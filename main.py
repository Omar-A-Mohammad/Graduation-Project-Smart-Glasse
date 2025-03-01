import threading
import time
import logging
import winsound
import pyttsx3
import queue
from pynput import keyboard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FeedbackManager:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self.speech_thread.start()
        
    def speak(self, text):
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        self.speech_queue.put(text)
    
    def _speech_loop(self):
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                if text:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
            except queue.Empty:
                pass  # Continue looping even if the queue is empty
    
    def haptic_feedback(self, frequency=1000, duration=200):
        winsound.Beep(frequency, duration)

class KeyListener:
    SHORT_PRESS_THRESHOLD = 0.3  # Seconds
    LONG_PRESS_THRESHOLD = 1.0   # Seconds
    MULTIPLE_PRESS_WINDOW = 0.5  # Seconds

    def __init__(self, feedback_manager, keys=['a', 's']):
        self.feedback_manager = feedback_manager
        self.keys = keys
        self.pressed_times = {}
        self.press_sequences = {key: [] for key in keys}  # Store multiple press timestamps
        self.input_lock = threading.Lock()
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.running = threading.Event()  # Graceful stop
        self.running.set()

    def start(self):
        self.listener.start()

    def stop(self):
        logging.info("Stopping KeyListener...")
        self.running.clear()
        self.listener.stop()

    def _on_press(self, key):
        with self.input_lock:
            try:
                key_char = key.char.lower()
                if key_char in self.keys and key_char not in self.pressed_times:
                    self.pressed_times[key_char] = time.time()
            except AttributeError:
                pass

    def _on_release(self, key):
        if not self.running.is_set():
            return  # Exit if the listener is stopping

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
        current_time = time.time()

        # Remove timestamps that are too old
        self.press_sequences[key] = [t for t in self.press_sequences[key] if current_time - t <= self.MULTIPLE_PRESS_WINDOW]
        self.press_sequences[key].append(current_time)

        press_count = len(self.press_sequences[key])
        logging.info(f"Press sequence for '{key}': {self.press_sequences[key]} (Count: {press_count})")

        if press_count > 1:
            logging.info(f"{press_count} presses detected for '{key}'")
            self.feedback_manager.speak(f"{press_count} presses of {key}")
            self.feedback_manager.haptic_feedback(1200, 200)
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
        self.running = threading.Event()
        self.running.set()

    def run(self):
        logging.info("Starting main loop...")
        self.key_listener.start()

        try:
            while self.running.is_set():
                time.sleep(1)  # Keep the main thread alive
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, shutting down gracefully...")
            self.stop()

    def stop(self):
        logging.info("Stopping main loop...")
        self.running.clear()
        self.key_listener.stop()

if __name__ == "__main__":
    main_loop = MainLoop()
    main_loop.run()
