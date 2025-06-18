from pynput import keyboard

def on_press(key):
    try:
        # For special keys like media keys
        if hasattr(key, 'name'):
            print(f'Special key {key.name} pressed')
            if key == keyboard.Key.media_play_pause:
                print("ACTION: Play/Pause button pressed!")
                # --- YOUR SMART GLASSES FUNCTION HERE ---
            elif key == keyboard.Key.media_volume_up:
                print("ACTION: Volume Up button pressed!")
                # --- YOUR SMART GLASSES FUNCTION HERE ---
            elif key == keyboard.Key.media_volume_down:
                print("ACTION: Volume Down button pressed!")
                # --- YOUR SMART GLASSES FUNCTION HERE ---
            elif key == keyboard.Key.media_next:
                print("ACTION: Next Track button pressed!")
                # --- YOUR SMART GLASSES FUNCTION HERE ---
            elif key == keyboard.Key.media_previous:
                print("ACTION: Previous Track button pressed!")
                # --- YOUR SMART GLASSES FUNCTION HERE ---

    except AttributeError:
        # For regular alphanumeric keys (less relevant here)
        print(f'Alphanumeric key {key.char} pressed')

def on_release(key):
    # print(f'{key} released') # Optional: log release
    if key == keyboard.Key.esc: # Example: Stop listener with ESC
        return False

# Collect events until released
print("Listening for media key presses from headphones (or keyboard media keys)...")
print("Press ESC to stop.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()


print("Listener stopped.")