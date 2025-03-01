import time
import threading
import logging
from pynput import keyboard
from winsound import Beep
import pyttsx3

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class HapticFeedback:
    """Class to handle haptic feedback."""
    @staticmethod
    def vibrate(duration=0.1):
        """Simulate haptic feedback by beeping (replace with actual haptic feedback hardware control)."""
        Beep(1000, int(duration * 1000))  # Beep for haptic simulation
        logging.info(f"Haptic feedback: {duration}s vibration")

class TextToSpeech:
    """Class to handle text-to-speech output."""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)  # Adjust speech rate

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()
        logging.info(f"TTS: {text}")

class ButtonInputDetector:
    """Class to detect button presses and distinguish between short, long, and consecutive presses."""
    def __init__(self, button1_key, button2_key, long_press_duration=1.0, debounce_time=0.2):
        self.button1_key = button1_key
        self.button2_key = button2_key
        self.long_press_duration = long_press_duration
        self.debounce_time = debounce_time
        self.button1_press_time = 0
        self.button2_press_time = 0
        self.button1_consecutive_presses = 0
        self.button2_consecutive_presses = 0
        self.button1_held = False
        self.button2_held = False
        self.listener = None
        self.running = True

    def on_press(self, key):
        """Handle key press events."""
        try:
            if key.char == self.button1_key and not self.button1_held:
                self.button1_held = True
                self.button1_press_time = time.time()
                self.button1_consecutive_presses += 1
                logging.info(f"Button 1 pressed ({self.button1_consecutive_presses} times)")
            elif key.char == self.button2_key and not self.button2_held:
                self.button2_held = True
                self.button2_press_time = time.time()
                self.button2_consecutive_presses += 1
                logging.info(f"Button 2 pressed ({self.button2_consecutive_presses} times)")
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle key release events."""
        try:
            if key.char == self.button1_key and self.button1_held:
                self.button1_held = False
                duration = time.time() - self.button1_press_time
                if duration >= self.long_press_duration:
                    logging.info("Button 1 long press detected")
                    self.handle_button1_long_press()
                else:
                    logging.info("Button 1 short press detected")
                    self.handle_button1_short_press()
                threading.Timer(self.debounce_time, self.reset_button1_consecutive_presses).start()
            elif key.char == self.button2_key and self.button2_held:
                self.button2_held = False
                duration = time.time() - self.button2_press_time
                if duration >= self.long_press_duration:
                    logging.info("Button 2 long press detected")
                    self.handle_button2_long_press()
                else:
                    logging.info("Button 2 short press detected")
                    self.handle_button2_short_press()
                threading.Timer(self.debounce_time, self.reset_button2_consecutive_presses).start()
        except AttributeError:
            pass

    def reset_button1_consecutive_presses(self):
        """Reset Button 1 consecutive press count after debounce time."""
        if not self.button1_held:
            self.button1_consecutive_presses = 0
            logging.info("Button 1 consecutive presses reset")

    def reset_button2_consecutive_presses(self):
        """Reset Button 2 consecutive press count after debounce time."""
        if not self.button2_held:
            self.button2_consecutive_presses = 0
            logging.info("Button 2 consecutive presses reset")

    def handle_button1_short_press(self):
        """Handle Button 1 short press."""
        tts.speak(f"Button 1 short press ({self.button1_consecutive_presses} times)")
        HapticFeedback.vibrate(0.1)

    def handle_button1_long_press(self):
        """Handle Button 1 long press."""
        tts.speak("Button 1 long press")
        HapticFeedback.vibrate(0.5)

    def handle_button2_short_press(self):
        """Handle Button 2 short press."""
        tts.speak(f"Button 2 short press ({self.button2_consecutive_presses} times)")
        HapticFeedback.vibrate(0.1)

    def handle_button2_long_press(self):
        """Handle Button 2 long press."""
        tts.speak("Button 2 long press")
        HapticFeedback.vibrate(0.5)

    def start_listening(self):
        """Start listening for button presses."""
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def stop_listening(self):
        """Stop listening for button presses."""
        self.running = False
        if self.listener:
            self.listener.stop()

class MainProgram:
    """Main program class to handle modes and user interactions."""
    def __init__(self):
        self.current_mode = "main_menu"
        self.running = True
        self.button_detector = ButtonInputDetector(button1_key='a', button2_key='b')
        self.button_detector.start_listening()

    def run(self):
        """Main program loop."""
        tts.speak("Program started. Main menu.")
        while self.running:
            time.sleep(0.1)  # Reduce CPU usage

    def change_mode(self, new_mode):
        """Change the current mode of the program."""
        self.current_mode = new_mode
        tts.speak(f"Entering {new_mode} mode")
        logging.info(f"Mode changed to: {new_mode}")

    def shutdown(self):
        """Shutdown the program."""
        self.running = False
        self.button_detector.stop_listening()
        tts.speak("Program shutting down")
        logging.info("Program shutdown")

# Initialize components
tts = TextToSpeech()
haptic = HapticFeedback()

# Start the program
if __name__ == "__main__":
    program = MainProgram()
    try:
        program.run()
    except KeyboardInterrupt:
        program.shutdown()