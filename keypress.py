import threading
import time
import keyboard

# Function to detect keypresses
def detect_keypresses():
    def on_key_press(event):
        print(f"Key {event.name} was pressed")

    # Hook the key press event
    keyboard.on_press(on_key_press)

    # Keep the keypress detection running
    print("Keypress detection started. Press any key...")
    keyboard.wait('esc')  # Exit on 'esc' key

# Function to print a statement every second
def print_statement():
    while True:
        print("This statement prints every 1 second")
        time.sleep(1)

# Create threads for each task
keypress_thread = threading.Thread(target=detect_keypresses)
print_thread = threading.Thread(target=print_statement)

# Start the threads
keypress_thread.start()
print_thread.start()

# Wait for both threads to finish (though they run indefinitely)
keypress_thread.join()
print_thread.join()