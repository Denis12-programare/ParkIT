import speech_recognition as sr
from langdetect import detect, DetectorFactory

# Make langdetect consistent
DetectorFactory.seed = 0

class STT:
    def __init__(self, device_index=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=device_index)

    def listen(self, fallback_lang="en-US"):
        """
        Listen and detect language automatically.
        If detection fails, fall back to given language.
        """
        with self.microphone as source:
            print("[INFO] Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            # First, get rough transcript in fallback language
            text = self.recognizer.recognize_google(audio, language=fallback_lang)
            print(f"[INFO] Raw transcript: {text}")

            # Detect language of the transcript
            detected_lang = detect(text)
            print(f"[INFO] Detected language: {detected_lang}")

            return text, detected_lang

        except sr.UnknownValueError:
            print("[WARN] Could not understand audio.")
            return None, None
        except sr.RequestError as e:
            print(f"[ERROR] Could not request results; {e}")
            return None, None


# Example usage
if __name__ == "__main__":
    stt = STT()

    print("🎤 Say something in any language...")
    text, lang = stt.listen()

    if text:
        print(f"\n✅ You said: {text}")
        print(f"🌍 Language detected: {lang}")
