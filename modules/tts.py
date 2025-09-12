import pyttsx3
import re

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")

    def speak(self, message, language="en"):
        selected_voice = None
        lang = language.lower()

        for voice in self.voices:
            voice_id = voice.id.lower()
            voice_name = voice.name.lower()

            # Normalize (remove paths, split by \ or . or _ or -)
            tokens = re.split(r"[\\._\-]", voice_id) + re.split(r"[\\._\-]", voice_name)

            if lang in tokens or voice.languages and any(lang in str(l).lower() for l in voice.languages):
                selected_voice = voice.id
                break

        if selected_voice:
            self.engine.setProperty("voice", selected_voice)
            print(f"[INFO] Selected voice: {selected_voice} for '{language}'")
        else:
            print(f"[WARN] No voice found for '{language}', using default voice.")

        self.engine.say(message)
        self.engine.runAndWait()


# Example usage
if __name__ == "__main__":
    tts = TTS()
    tts.speak("", "fr")

