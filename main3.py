from pynput import keyboard 
import time

def on_key_release(key: keyboard.Key | keyboard.KeyCode | None): #what to do on key-release
    time_taken = round(time.time() - t, 2) #rounding the long decimal float
    print("The key",key," is pressed for",time_taken,'seconds')
    return False #stop detecting more key-releases

def on_key_press(key: keyboard.Key | keyboard.KeyCode | None): #what to do on key-press
    return False #stop detecting more key-presses

with keyboard.Listener(on_press = on_key_press) as press_listener: #setting code for listening key-press
    press_listener.join()

t = time.time() #reading time in sec

with keyboard.Listener(on_release = on_key_release) as release_listener: #setting code for listening key-release
    release_listener.join()