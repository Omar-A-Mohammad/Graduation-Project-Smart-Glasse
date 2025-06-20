from typing import Callable
import keyboard
import time
import threading
import logging
import pyttsx3
import winsound
import queue

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('Input_Manager/keypress_log.txt')
    ]
)
logger = logging.getLogger(__name__)

class HapticFeedback:
    @staticmethod
    def short_pulse(): winsound.Beep(800, 100)
    @staticmethod
    def long_pulse(): winsound.Beep(600, 300)
    @staticmethod
    def double_pulse():
        winsound.Beep(800, 100)
        time.sleep(0.1)
        winsound.Beep(800, 100)
    @staticmethod
    def triple_pulse():
        winsound.Beep(800, 100)
        time.sleep(0.1)
        winsound.Beep(800, 100)
        time.sleep(0.1)
        winsound.Beep(800, 100)

class SpeechEngine:
    _stop_sentinel = object()
    def __init__(self, rate: int = 150):
        self.rate = rate
        self._speech_queue = queue.Queue()
        self._speech_thread = None
        self._initialize_thread()

    def _initialize_thread(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.stop()
        self._speech_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self._speech_thread.start()

    def _speech_loop(self):
        while True:
            item = self._speech_queue.get()
            if item is self._stop_sentinel:
                self._speech_queue.task_done()
                break
            if isinstance(item, str):
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.rate)
                    engine.say(item)
                    engine.runAndWait()
                    engine.stop()
                except Exception as e:
                    logger.error(f"Speech error: {e}")
            self._speech_queue.task_done()

    def speak(self, text: str):
        if text.strip():
            self._speech_queue.put(text)

    def stop(self):
        if self._speech_thread and self._speech_thread.is_alive():
            self._speech_queue.put(self._stop_sentinel)
            self._speech_thread.join(timeout=3)
            self._speech_thread = None

class KeyDetector:
    def __init__(self, scan_code: int, press_callback):
        self.scan_code = scan_code
        self.press_callback = press_callback
        self.press_time = 0
        self.release_time = 0
        self.press_count = 0
        self.last_release_time = 0
        self.hold_detected = False
        self.key_pressed = False
        self.hold_threshold = 0.5
        self.tap_threshold = 0.5
        self.debounce_time = 0.05
        self.max_taps = 3
        self.hold_check_timer = None
        self.tap_check_timer = None

    def on_press(self, event):
        if event.scan_code != self.scan_code or self.key_pressed or (time.time() - self.press_time) < self.debounce_time:
            return
        self.key_pressed = True
        current_time = time.time()
        self.press_time = current_time
        self.hold_detected = False
        if self.tap_check_timer:
            self.tap_check_timer.cancel()
        self.hold_check_timer = threading.Timer(self.hold_threshold, self._trigger_hold, [current_time])
        self.hold_check_timer.start()

    def on_release(self, event):
        if event.scan_code != self.scan_code or not self.key_pressed or (time.time() - self.release_time) < self.debounce_time:
            return
        self.key_pressed = False
        current_time = time.time()
        self.release_time = current_time
        if self.hold_check_timer and not self.hold_detected:
            self.hold_check_timer.cancel()
        if self.hold_detected:
            self.hold_detected = False
            return
        if (current_time - self.last_release_time) < self.tap_threshold:
            self.press_count += 1
        else:
            self.press_count = 1
        self.last_release_time = current_time
        self.tap_check_timer = threading.Timer(self.tap_threshold, self._check_tap_count, [current_time])
        self.tap_check_timer.start()

    def _trigger_hold(self, press_time):
        if press_time == self.press_time and not self.hold_detected and self.key_pressed:
            self.hold_detected = True
            self.press_count = 0
            self.press_callback(self.scan_code, 'hold')

    def _check_tap_count(self, release_time):
        if release_time != self.last_release_time or self.hold_detected or self.key_pressed:
            return
        if self.press_count > self.max_taps:
            self.press_count = 0
            return
        if self.press_count == 1:
            self.press_callback(self.scan_code, 'single')
        elif self.press_count == 2:
            self.press_callback(self.scan_code, 'double')
        elif self.press_count == 3:
            self.press_callback(self.scan_code, 'triple')
        self.press_count = 0

class InputManager:
    def __init__(self):
        self.logger = logger
        self.logger.debug("Initializing InputManager...")
        self.speech_engine = SpeechEngine()
        self.input_active = True
        self.key_detectors: dict[int, KeyDetector] = {}
        self.action_handlers: dict[str, Callable] = {
            'single': self.default_single_handler,
            'double': self.default_double_handler,
            'triple': self.default_triple_handler,
            'hold': self.default_hold_handler
        }

    def set_action_handler(self, action_type: str, handler: Callable[[int], None]):
        if action_type in self.action_handlers:
            self.action_handlers[action_type] = handler

    def default_single_handler(self, key):
        HapticFeedback.short_pulse()
        self.speak(f"Key {key} pressed once")

    def default_double_handler(self, key):
        HapticFeedback.double_pulse()
        self.speak(f"Key {key} pressed twice")

    def default_triple_handler(self, key):
        HapticFeedback.triple_pulse()
        self.speak(f"Key {key} pressed three times")

    def default_hold_handler(self, key):
        HapticFeedback.long_pulse()
        self.speak(f"Key {key} held down")

    def handle_key_action(self, scan_code: int, action_type: str):
        if not self.input_active:
            return
        self.input_active = False
        self.logger.info(f"Detected {action_type} press on key with scan code {scan_code}")
        if action_type in self.action_handlers:
            self.action_handlers[action_type](scan_code)
        else:
            self.logger.warning(f"No handler defined for action type: {action_type}")
        self.input_active = True

    def start(self, scan_codes=None):
        if scan_codes is None:
            scan_codes = [-176, -177, -179]
        for code in scan_codes:
            detector = KeyDetector(code, self.handle_key_action)
            self.key_detectors[code] = detector
            keyboard.hook(detector.on_press)
            keyboard.hook(detector.on_release)
        logger.info(f"Listening for scan codes: {', '.join(str(c) for c in scan_codes)}")
        self.speak("System ready. Listening for headset buttons.")

    def speak(self, text):
        try:
            self.speech_engine.speak(text)
        except Exception as e:
            logger.error(f"Speak error: {e}")

    def stop(self):
        keyboard.unhook_all()
        self.speech_engine.stop()
        logger.info("InputManager stopped.")
