import keyboard
import time
import threading
import logging
import pyttsx3
import winsound
from collections import deque

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('Input_Manager/keypress_log.txt')
    ]
)
logger = logging.getLogger(__name__)

class HapticFeedback:
    """Class to handle haptic feedback using winsound.Beep"""
    
    @staticmethod
    def short_pulse():
        winsound.Beep(800, 100)
    
    @staticmethod
    def long_pulse():
        winsound.Beep(600, 300)
    
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
    """Text-to-speech engine wrapper with queue management"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.startLoop(False)
        self.current_text = ""
        self.is_speaking = False
        self.lock = threading.Lock()
        
    def speak(self, text):
        with self.lock:
            self.current_text = text
            if not self.is_speaking:
                self._start_speaking()
    
    def _start_speaking(self):
        self.is_speaking = True
        self.engine.say(self.current_text)
        self.engine.iterate()
        
    def on_end(self):
        with self.lock:
            self.is_speaking = False
            if self.current_text:
                self._start_speaking()
    
    def stop(self):
        self.engine.endLoop()

class KeyDetector:
    """For a specified key, detects different types of key presses: single, double, triple, hold"""
    
    def __init__(self, key, press_callback):
        self.key = key
        self.press_callback = press_callback
        self.press_time = 0
        self.release_time = 0
        self.press_count = 0
        self.last_release_time = 0
        self.hold_detected = False
        self.hold_threshold = 0.5  # seconds to consider as hold
        self.tap_threshold = 0.5  # seconds between taps to count as multi-tap
        self.debounce_time = 0.05  # seconds to debounce key presses
        self.max_taps = 3
        self.hold_check_timer = None
        self.tap_check_timer = None
        self.key_pressed = False
        
    def on_press(self, event):
        """Handle key press event"""
        if event.name != self.key or self.key_pressed or (time.time() - self.press_time) < self.debounce_time:
            return
        
        self.key_pressed = True
        current_time = time.time()
        self.press_time = current_time
        self.hold_detected = False
        
        # Cancel any pending tap checks
        if self.tap_check_timer:
            self.tap_check_timer.cancel()
            self.tap_check_timer = None
        
        # Schedule hold detection
        self.hold_check_timer = threading.Timer(
            self.hold_threshold, 
            self._trigger_hold, 
            [current_time]
        )
        self.hold_check_timer.start()
        
        logger.debug(f"Key {self.key} pressed at {current_time}")
        
    def on_release(self, event):
        """Handle key release event"""
        if event.name != self.key or not self.key_pressed or (time.time() - self.release_time) < self.debounce_time:
            return
            
        self.key_pressed = False
        current_time = time.time()
        self.release_time = current_time
        
        # Cancel hold detection if it hasn't triggered yet
        if self.hold_check_timer and not self.hold_detected:
            self.hold_check_timer.cancel()
            self.hold_check_timer = None
        
        # If hold was already detected, reset and return
        if self.hold_detected:
            self.hold_detected = False
            return
            
        press_duration = current_time - self.press_time
        
        # Check for multi-tap
        if (current_time - self.last_release_time) < self.tap_threshold:
            self.press_count += 1
        else:
            self.press_count = 1
            
        self.last_release_time = current_time
        
        # Schedule a check for the tap count
        self.tap_check_timer = threading.Timer(
            self.tap_threshold, 
            self._check_tap_count, 
            [current_time]
        )
        self.tap_check_timer.start()
        
        logger.debug(f"Key {self.key} released at {current_time}, duration {press_duration:.3f}s, count {self.press_count}")
    
    def _trigger_hold(self, press_time):
        """Trigger hold action immediately when threshold is reached"""
        if press_time == self.press_time and not self.hold_detected and self.key_pressed:
            self.hold_detected = True
            self.press_count = 0
            self.press_callback(self.key, 'hold')
            logger.debug(f"Key {self.key} hold triggered at {time.time()}")
    
    def _check_tap_count(self, release_time):
        """Check tap count after threshold period"""
        if release_time != self.last_release_time or self.hold_detected or self.key_pressed:
            return
            
        if self.press_count > self.max_taps:
            logger.debug(f"Ignored {self.press_count} taps on key {self.key}")
            self.press_count = 0
            return
            
        if self.press_count == 1:
            self.press_callback(self.key, 'single')
        elif self.press_count == 2:
            self.press_callback(self.key, 'double')
        elif self.press_count == 3:
            self.press_callback(self.key, 'triple')
            
        self.press_count = 0

class InputManager:
    """Manages input detection and feedback with customizable actions"""
    
    def __init__(self):
        self.speech_engine = SpeechEngine()
        self.speech_engine.engine.connect('finished-utterance', self.speech_engine.on_end)
        self.input_active = True
        self.key_detectors = {
            'a': KeyDetector('a', self.handle_key_action),
            'b': KeyDetector('b', self.handle_key_action)
        }
        
        # Customizable action handlers
        self.action_handlers = {
            'single': self.default_single_handler,
            'double': self.default_double_handler,
            'triple': self.default_triple_handler,
            'hold': self.default_hold_handler
        }
        
    def set_action_handler(self, action_type, handler):
        """Set a custom handler for a specific action type"""
        if action_type in self.action_handlers:
            self.action_handlers[action_type] = handler
        else:
            raise ValueError(f"Invalid action type: {action_type}")
            
    # Default action handlers (can be overridden)
    def default_single_handler(self, key):
        HapticFeedback.short_pulse()
        self.speak(f"Key {key.upper()} pressed once")
        
    def default_double_handler(self, key):
        HapticFeedback.double_pulse()
        self.speak(f"Key {key.upper()} pressed twice")
        
    def default_triple_handler(self, key):
        HapticFeedback.triple_pulse()
        self.speak(f"Key {key.upper()} pressed three times")
        
    def default_hold_handler(self, key):
        HapticFeedback.long_pulse()
        self.speak(f"Key {key.upper()} held down")
        
    def handle_key_action(self, key, action_type):
        if not self.input_active:
            return
            
        self.input_active = False
        
        logger.info(f"Detected {action_type} press on key {key.upper()}")
        
        # Call the appropriate handler
        if action_type in self.action_handlers:
            self.action_handlers[action_type](key)
        else:
            logger.warning(f"No handler defined for action type: {action_type}")
        
        self.input_active = True
    
    def start(self):
        for key, detector in self.key_detectors.items():
            keyboard.on_press_key(key, detector.on_press)
            keyboard.on_release_key(key, detector.on_release)
        
        logger.info("Input manager started. Listening for key presses on A and B.")
        self.speak("System ready. Listening for input on keys A and B.")
    
    def speak(self, text):
        self.speech_engine.speak(text)
    
    def stop(self):
        keyboard.unhook_all()
        self.speech_engine.stop()
        logger.info("Input manager stopped.")

def main():
    try:
        input_manager = InputManager()
        
        keys = list(input_manager.key_detectors.keys())
        key1, key2= keys[0], keys[1]
        logger.info(f"Listening for key presses: {key1} and {key2}")

        print(f"\nPress '{key1}' or '{key2}' to test the input manager. Press Ctrl+C to exit. \n")

        # EXAMPLE: Customize action handlers
        # def custom_single_handler(key):
        #     HapticFeedback.short_pulse()
        #     input_manager.speak(f"Custom action for {key} single press")
        # input_manager.set_action_handler('single', custom_single_handler)
        
        input_manager.start()
        
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        input_manager.stop()

if __name__ == "__main__":
    main()