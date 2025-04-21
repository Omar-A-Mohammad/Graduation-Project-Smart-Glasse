from typing import Callable
import keyboard
import time
import threading
import logging
import pyttsx3
import winsound

import sys # Import sys for platform check
import queue # Import the queue module

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
    """Class to handle haptic feedback using winsound.Beep"""
    
    @staticmethod
    def short_pulse():
        """Short pulse order"""
        logger.debug("Short pulse order received")
        winsound.Beep(800, 100)
    
    @staticmethod
    def long_pulse():
        """Long pulse order"""
        logger.debug("Long pulse order received")
        winsound.Beep(600, 300)
    
    @staticmethod
    def double_pulse():
        """Double pulse order"""
        logger.debug("Double pulse order received")
        winsound.Beep(800, 100)
        time.sleep(0.1)
        winsound.Beep(800, 100)
    
    @staticmethod
    def triple_pulse():
        """Triple pulse order"""
        logger.debug("Triple pulse order received")
        winsound.Beep(800, 100)
        time.sleep(0.1)
        winsound.Beep(800, 100)
        time.sleep(0.1)
        winsound.Beep(800, 100)


class SpeechEngine:
    """
    Text-to-speech engine wrapper using pyttsx3 with a dedicated speech thread.
    Uses a queue to handle speech requests non-blockingly from the caller's perspective.
    """

    # Define a sentinel value to signal the speech thread to stop
    _stop_sentinel = object()

    def __init__(self, rate: int = 150):
        """
        Initialize the speech engine with a dedicated thread.

        Args:
            rate (int): Speech rate in words per minute.
        """
        logger.debug("Initializing pyttsx3 engine for dedicated thread...")
        try:
            self.engine = pyttsx3.init()
            logger.debug("pyttsx3 engine initialized.")

            self.engine.setProperty('rate', rate)
            logger.debug("Speech rate set to: {}".format(rate))

            # Use a thread-safe queue for communication
            self._speech_queue = queue.Queue()

            # Create and start the dedicated speech processing thread
            self._speech_thread = threading.Thread(target=self._speech_loop, daemon=True)
            self._speech_thread.start()

            logger.debug("Dedicated speech thread started.")
            logger.debug("SpeechEngine setup complete.")

        except Exception as e:
            logger.error(f"Error initializing speech engine: {e}", exc_info=True)
            self._speech_thread = None

    def _speech_loop(self):
        """
        The main loop for the dedicated speech thread.
        Gets messages from the queue and speaks them using runAndWait().
        """
        logger.debug("Speech thread started.")
        if not self.engine:
            logger.error("Speech thread cannot run, engine not initialized.")
            return

        # This loop runs indefinitely until the stop sentinel is received
        while True:
            try:
                # Get the next item from the queue. Blocks until an item is available.
                item = self._speech_queue.get()

                # Check if the item is the stop sentinel
                if item is self._stop_sentinel:
                    logger.debug("Stop sentinel received, exiting speech loop.")
                    self._speech_queue.task_done() # Indicate that the sentinel task is done
                    break # Exit the loop

                # If it's not the sentinel, it should be text to speak
                if isinstance(item, str) and item:
                    logger.debug(f"Speech thread speaking: '{item}'")
                    try:
                        # Use say() and runAndWait() in the dedicated thread.
                        # runAndWait() blocks this thread until speech is done.
                        self.engine.say(item)
                        self.engine.runAndWait()
                        logger.debug(f"Speech thread finished speaking: '{item}'")
                    except Exception as e:
                        logger.error(f"Error during speech in thread: {e}", exc_info=True)

                self._speech_queue.task_done() # Indicate that the task is done

            except Exception as e:
                 # Catch any unexpected errors within the loop to prevent thread death
                 logger.error(f"Unexpected error in speech thread loop: {e}", exc_info=True)
                 self._speech_queue.task_done() # Ensure task is marked done even on error

        logger.debug("Speech thread exiting.")
        # Clean up engine resources when the loop breaks
        try:
             self.engine.stop() # Use engine.stop() to clean up resources associated with runAndWait
             logger.debug("pyttsx3 engine resources stopped in thread.")
        except Exception as e:
             logger.error(f"Error stopping engine resources in thread: {e}", exc_info=True)


    def speak(self, text: str):
        """
        Queue text to be spoken by the dedicated speech thread.

        Args:
            text (str): Text to be spoken.
        """
        # Only add to the queue if the engine and queue were successfully initialized
        if self._speech_queue and self.engine:
            logger.debug(f"Adding text to speech queue: '{text}'")
            try:
                self._speech_queue.put(text)
            except Exception as e:
                 logger.error(f"Error putting text in speech queue: {e}", exc_info=True)
        else:
            logger.warning(f"Speech queue not available. Cannot speak: '{text}'")


    def stop(self):
        """
        Stops the speech engine and its dedicated background thread.
        Sends a stop signal to the queue and waits for the thread to finish.
        """
        if self._speech_queue and self._speech_thread and self._speech_thread.is_alive():
            logger.debug("Stopping SpeechEngine and dedicated thread...")
            try:
                # Put the stop sentinel into the queue
                self._speech_queue.put(self._stop_sentinel)

                # Wait for the speech thread to finish processing the queue and exit
                # Use a timeout to prevent the main thread from hanging indefinitely
                self._speech_thread.join(timeout=5)
                if self._speech_thread.is_alive():
                    logger.warning("Speech thread did not join within timeout. It might still be running.")
                else:
                    logger.debug("Dedicated speech thread successfully joined.")

            except Exception as e:
                logger.error(f"Error during SpeechEngine stop: {e}", exc_info=True)

        # Ensure engine reference is cleared regardless of thread join status
        self._speech_thread = None
        logger.info("SpeechEngine stopped.")


class KeyDetector:
    """For a specified key, detects different types of key presses: single, double, triple, hold"""
    
    def __init__(self, key: str, press_callback):
        """
        Initializes the KeyDetector for a specific key.

        Args:
            key (str): The key to detect actions for (e.g., 'a', 'space').
            press_callback: A function to call when an action is detected.
                            It should accept (key: str, action_type: str) as arguments.
        """
        self.key: str = key
        self.press_callback = press_callback

        # State variables
        self.press_time: float = 0
        self.release_time: float = 0
        self.press_count: int = 0
        self.last_release_time: float = 0
        self.hold_detected: bool = False
        self.key_pressed = False

        # Configuration thresholds
        self.hold_threshold: float = 0.5  # seconds to consider as hold
        self.tap_threshold: float = 0.5  # seconds between taps to count as multi-tap
        self.debounce_time: float = 0.05  # seconds to debounce key presses
        self.max_taps: int = 3
        
        # Timers for state detection
        self.hold_check_timer: threading.Timer | None = None
        self.tap_check_timer: threading.Timer | None = None
        
        # Lock to protect state variables accessed by multiple threads
        # (keyboard hook thread and threading.Timer threads)
        self.lock = threading.Lock()

        logger.debug(f"KeyDetector initialized for key '{self.key}'")

    def on_press(self, event):
        """Handle raw key press event from the keyboard library."""
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
        """Handle raw key release event from the keyboard library."""
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
            logger.debug(f"Hold detected for key {self.key} at {time.time()}")
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
            logger.debug(f"Single tap detected on key {self.key}")
            self.press_callback(self.key, 'single')
        elif self.press_count == 2:
            logger.debug(f"Double tap detected on key {self.key}")
            self.press_callback(self.key, 'double')
        elif self.press_count == 3:
            logger.debug(f"Triple tap detected on key {self.key}")
            self.press_callback(self.key, 'triple')
            
        self.press_count = 0

class InputManager:
    """Manages input detection and feedback with customizable actions"""
    
    def __init__(self):
        """Initialize the input manager"""
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing InputManager...")
        
        try:
            self.speech_engine = SpeechEngine()
            self.logger.debug("Speech engine initialized.")
        except Exception as e:
            self.logger.error(f"Error initializing speech engine: {e}")

        self.input_active = True
        self.key_detectors: dict[str, KeyDetector] = {
            'a': KeyDetector('a', self.handle_key_action),
            'b': KeyDetector('b', self.handle_key_action)
        }
        
        # Customizable action handlers
        self.action_handlers: dict[str, Callable] = {
            'single': self.default_single_handler,
            'double': self.default_double_handler,
            'triple': self.default_triple_handler,
            'hold': self.default_hold_handler
        }
        self.logger.debug("InputManager setup complete.")
        
    def set_action_handler(self, action_type: str, handler: Callable[[str], None]):
        """Set a custom handler for a specific action type"""
        if action_type in self.action_handlers:
            self.action_handlers[action_type] = handler
        else:
            raise ValueError(f"Invalid action type: {action_type}")
            
    # Default action handlers (can be overridden)
    def default_single_handler(self, key: str):
        try:
            HapticFeedback.short_pulse()
        except Exception as e:
            logger.error(f"Error in short pulse: {e}")
        self.speak(f"Key {key.upper()} pressed once")
        
    def default_double_handler(self, key: str):
        try:
            HapticFeedback.double_pulse()
        except Exception as e:
            logger.error(f"Error in double pulse: {e}")
        self.speak(f"Key {key.upper()} pressed twice")
        
    def default_triple_handler(self, key: str):
        try:
            HapticFeedback.triple_pulse()
        except Exception as e:
            logger.error(f"Error in triple pulse: {e}")
        self.speak(f"Key {key.upper()} pressed three times")
        
    def default_hold_handler(self, key: str):
        try:
            HapticFeedback.long_pulse()
        except Exception as e:
            logger.error(f"Error in long pulse: {e}")
        self.speak(f"Key {key.upper()} held down")
        
    def handle_key_action(self, key: str, action_type: str):
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
        try:
            self.speech_engine.speak(text)
        except Exception as e:
            logger.error(f"Error in speak method: {e}")
    
    def stop(self):
        try:
            keyboard.unhook_all()
            try:
                self.speech_engine.stop()
            except Exception as e:
                logger.error(f"Error stopping speech engine: {e}")
            logger.info("Input manager stopped.")
        except Exception as e:
            logger.error(f"Error stopping input manager: {e}")

def main():
    """Main function to run the input manager"""
    logger.info("Starting Input Manager...")
    input_manager = InputManager()
    logger.info("Input Manager initialized.")
    try:
        
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