"""
#     Add a wake word system
def is_wake_word(command, wake_words=["glasses", "assistant", "hey"]):
    return any(word in command for word in wake_words)

# Continuous listening
def continuous_listener(callback):
    r = sr.Recognizer()
    with get_audio_source() as source:
        r.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = r.listen(source, timeout=3)
                text = r.recognize_google(audio)
                callback(text.lower())
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Error: {e}")
"""