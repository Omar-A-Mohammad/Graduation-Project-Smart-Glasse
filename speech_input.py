import speech_recognition as sr

def listen_for_search_query(prompt="What are you looking for?"):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print(prompt)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)

    try:
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        print("Speech Recognition service is unavailable.")
        return None
