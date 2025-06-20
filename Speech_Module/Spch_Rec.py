import time
import speech_recognition as sr

def get_audio_source():
    for i in range(3):  # Try 3 times
        try:
            return sr.Microphone()
        except Exception as e:
            print(f"Microphone error: {e}")
            time.sleep(1)
    return None

def listen_for_command():
    r = sr.Recognizer()
    
    # Adjust for ambient noise and set timeout
    with sr.Microphone() as source:
        print("Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("No speech detected")
            return ""
            
    try:
        command = r.recognize_google(audio).lower() # type: ignore
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""
    
# Test it
if __name__ == "__main__":
    while True:
        get_audio_source()
        command = listen_for_command()
        if command:
            print(f"Processing command: {command}")
            if "exit" in command:
                break
