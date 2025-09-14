import pyttsx3
import re
import time

class TTS:
    def __init__(self):
        # Temporarily initialize to fetch available voices
        temp_engine = pyttsx3.init()
        self.voices = temp_engine.getProperty("voices")
        temp_engine.stop()  # Clean up

    def speak(self, message, language="en"):
        # Initialize a new engine instance for each speak call to avoid state issues
        engine = pyttsx3.init()
        selected_voice = None
        lang = language.lower()
        
        # Select appropriate voice using the pre-fetched voices list
        for voice in self.voices:
            # Tokenize id and name for language matching
            tokens = re.split(r"[\\._\-]", voice.id.lower()) + re.split(r"[\\._\-]", voice.name.lower())
            if lang in tokens or (voice.languages and any(lang in str(l).lower() for l in voice.languages)):
                selected_voice = voice.id
                break

        if selected_voice:
            engine.setProperty("voice", selected_voice)
        else:
            print(f"[WARN] No voice found for '{language}', using default.")

        # Speak the message
        engine.say(message)
        engine.runAndWait()
        time.sleep(1.5)

