import time
import threading
from queue import Queue
import keyboard  # For keyboard input simulation
import pyttsx3  # For text-to-speech
import logging  # For logging

# Custom Modules
import OCR_Module

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[logging.StreamHandler()]  # Log to console
)

# Constants
BUTTON_A_KEY = '1'  # Key for Button A
BUTTON_B_KEY = '2'  # Key for Button B

class FeedbackSystem:
    """Handles auditory and haptic feedback."""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speech speed
        self.engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
        logging.info("FeedbackSystem initialized.")

    def provide_auditory_feedback(self, message):
        """Provide auditory feedback using text-to-speech."""
        logging.info(f"Providing auditory feedback: {message}")
        self.engine.say(message)
        self.engine.runAndWait()

    def provide_haptic_feedback(self, duration=0.1):
        """Simulate haptic feedback (print to console for testing)."""
        logging.info(f"Providing haptic feedback for {duration} seconds.")
        print(f"Haptic: Vibrating for {duration} seconds")


class Button:
    """Represents a button and detects presses."""
    def __init__(self, key, name, short_press_min=0.05, short_press_max=1.0, long_press_threshold=1.0):
        """
        Initialize a button.

        :param key: The keyboard key associated with the button.
        :param name: The name of the button (e.g., 'A' or 'B').
        :param short_press_min: Minimum duration (in seconds) for a press to count as a short press.
        :param short_press_max: Maximum duration (in seconds) for a press to count as a short press.
        :param long_press_threshold: Duration (in seconds) for a press to count as a long press.
        """
        self.key = key
        self.name = name
        self.short_press_min = short_press_min  # Minimum duration for a short press
        self.short_press_max = short_press_max  # Maximum duration for a short press
        self.long_press_threshold = long_press_threshold  # Duration for a long press
        self.press_start_time = 0
        self.press_count = 0
        self.debounce_time = 0.2  # Time to debounce button presses
        self.multiple_press_timeout = 0.5  # Timeout between multiple presses

    def detect_presses(self, input_queue):
        """Detect button presses and classify them as short, long, or multiple presses."""
        logging.info(f"Starting button detection for {self.name}.")
        while True:
            if keyboard.is_pressed(self.key):  # Simulated button is pressed
                logging.info(f"{self.name}: Key {self.key} is pressed.")
                if self.press_start_time == 0:  # First press
                    self.press_start_time = time.time()
                    logging.info(f"{self.name}: Press detected.")
                else:
                    if time.time() - self.press_start_time > 1.0:  # Long press threshold
                        logging.info(f"{self.name}: Long press detected.")
                        input_queue.put((self.name, 'long'))
                        self.press_start_time = 0
                        self.press_count = 0
                        time.sleep(self.debounce_time)  # Debounce
            else:  # Simulated button is released
                if self.press_start_time != 0:
                    press_duration = time.time() - self.press_start_time
                    if self.short_press_min <= press_duration < self.short_press_max:  # Short press
                        self.press_count += 1
                        self.press_start_time = 0
                        logging.info(f"{self.name}: Short press detected (count: {self.press_count}).")
                        time.sleep(self.debounce_time)  # Debounce
                        
                        # Check for multiple quick presses
                        time.sleep(0.3)  # Wait to see if another press occurs
                        if not keyboard.is_pressed(self.key):
                            logging.info(f"{self.name}: Multiple presses detected (count: {self.press_count}).")
                            input_queue.put((self.name, 'multiple', self.press_count))
                            self.press_count = 0


class StateMachine:
    """Manages the program's state and transitions."""
    def __init__(self, feedback_system):
        self.states = {
            'MAIN_MENU': 'Main Menu',
            'MODE_1': 'Mode 1',
            'MODE_2': 'Mode 2',
            'OPTIONS': 'Options',
        }
        self.current_state = self.states['MAIN_MENU']
        self.feedback_system = feedback_system
        logging.info("StateMachine initialized. Current state: MAIN_MENU.")

    def handle_input(self, button, press_type, *args):
        """Handle state transitions based on button input."""
        logging.info(f"Handling input: Button={button}, Press Type={press_type}, Args={args}.")
        if self.current_state == self.states['MAIN_MENU']:
            if button == 'A' and press_type == 'short':
                self.current_state = self.states['MODE_1']
                logging.info("Transitioning to MODE_1.")
                self.feedback_system.provide_auditory_feedback("Entering Mode 1")
                self.feedback_system.provide_haptic_feedback()
            elif button == 'B' and press_type == 'short':
                self.current_state = self.states['MODE_2']
                logging.info("Transitioning to MODE_2.")
                self.feedback_system.provide_auditory_feedback("Entering Mode 2")
                self.feedback_system.provide_haptic_feedback()
            elif press_type == 'long':
                self.current_state = self.states['OPTIONS']
                logging.info("Transitioning to OPTIONS.")
                self.feedback_system.provide_auditory_feedback("Entering Options")
                self.feedback_system.provide_haptic_feedback()

        elif self.current_state == self.states['MODE_1']:
            if button == 'A' and press_type == 'short':
                logging.info("Performing Mode 1 action.")
                self.feedback_system.provide_auditory_feedback("Mode 1 action")
                self.feedback_system.provide_haptic_feedback()
            elif button == 'B' and press_type == 'long':
                self.current_state = self.states['MAIN_MENU']
                logging.info("Returning to MAIN_MENU.")
                self.feedback_system.provide_auditory_feedback("Returning to Main Menu")
                self.feedback_system.provide_haptic_feedback()

        elif self.current_state == self.states['MODE_2']:
            if button == 'A' and press_type == 'multiple':
                logging.info(f"Performing Mode 2 action with {args[0]} presses.")
                self.feedback_system.provide_auditory_feedback(f"Mode 2 action with {args[0]} presses")
                self.feedback_system.provide_haptic_feedback()
            elif button == 'B' and press_type == 'long':
                self.current_state = self.states['MAIN_MENU']
                logging.info("Returning to MAIN_MENU.")
                self.feedback_system.provide_auditory_feedback("Returning to Main Menu")
                self.feedback_system.provide_haptic_feedback()

        elif self.current_state == self.states['OPTIONS']:
            if button == 'A' and press_type == 'short':
                logging.info("Option 1 selected.")
                self.feedback_system.provide_auditory_feedback("Option 1 selected")
                self.feedback_system.provide_haptic_feedback()
            elif button == 'B' and press_type == 'short':
                logging.info("Option 2 selected.")
                self.feedback_system.provide_auditory_feedback("Option 2 selected")
                self.feedback_system.provide_haptic_feedback()
            elif press_type == 'long':
                self.current_state = self.states['MAIN_MENU']
                logging.info("Returning to MAIN_MENU.")
                self.feedback_system.provide_auditory_feedback("Returning to Main Menu")
                self.feedback_system.provide_haptic_feedback()


class MainLoop:
    """Main program loop."""
    def __init__(self):
        self.input_queue = Queue()
        self.feedback_system = FeedbackSystem()
        self.state_machine = StateMachine(self.feedback_system)
        self.button_a = Button(BUTTON_A_KEY, 'A')
        self.button_b = Button(BUTTON_B_KEY, 'B')
        logging.info("MainLoop initialized.")

    def start(self):
        """Start the main program loop."""
        logging.info("Starting main loop.")
        try:
            # Start button detection threads
            threading.Thread(target=self.button_a.detect_presses, args=(self.input_queue,), daemon=True).start()
            threading.Thread(target=self.button_b.detect_presses, args=(self.input_queue,), daemon=True).start()
            logging.info("Button detection threads started.")

            # Handle state machine
            while True:
                if not self.input_queue.empty():
                    button, press_type, *args = self.input_queue.get()
                    logging.info(f"Processing input: Button={button}, Press Type={press_type}, Args={args}.")
                    self.state_machine.handle_input(button, press_type, *args)
                time.sleep(0.1)  # Small delay to avoid busy-waiting
        except KeyboardInterrupt:
            logging.info("Exiting program...")


if __name__ == "__main__":
    main_loop = MainLoop()
    main_loop.start()