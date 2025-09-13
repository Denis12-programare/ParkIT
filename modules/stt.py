# import speech_recognition as sr
# from langdetect import detect, DetectorFactory

# DetectorFactory.seed = 0  # consistent langdetect

# class STT:
#     def __init__(self, device_index=None, energy_threshold=300, pause_threshold=0.8):
#         self.recognizer = sr.Recognizer()
#         self.recognizer.energy_threshold = energy_threshold  # how loud mic must be to count as speech
#         self.recognizer.pause_threshold = pause_threshold    # seconds of silence before phrase ends
#         self.microphone = sr.Microphone(device_index=device_index)

#         # Calibrate once at startup
#         with self.microphone as source:
#             print("[INFO] Calibrating mic for ambient noise... Please wait.")
#             self.recognizer.adjust_for_ambient_noise(source, duration=1)
#             print(f"[INFO] Mic calibrated with threshold: {self.recognizer.energy_threshold}")

#     def listen(self, fallback_lang="en-US", phrase_time_limit=10, timeout=1):
#         with self.microphone as source:
#             print("[INFO] Listening...")
#             audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

#         try:
#             # Rough transcript
#             text = self.recognizer.recognize_google(audio, language=fallback_lang)
#             print(f"[INFO] Raw transcript: {text}")

#             # Detect language
#             try:
#                 detected_lang = detect(text)
#             except:
#                 detected_lang = fallback_lang.split("-")[0]  # fallback if detection fails

#             print(f"[INFO] Detected language: {detected_lang}")
#             return text, detected_lang

#         except sr.UnknownValueError:
#             print("[WARN] Could not understand audio.")
#             return None, None
#         except sr.RequestError as e:
#             print(f"[ERROR] API request failed: {e}")
#             return None, None
        
import whisper
import speech_recognition as sr
import numpy as np
import io
import wave
from langdetect import detect
import time

class STT:
    def __init__(self, model_size="base", device_index=None, energy_threshold=300, pause_threshold=0.8):
        self.model = whisper.load_model(model_size)  # load Whisper model
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.microphone = sr.Microphone(device_index=device_index)

        # Calibrate mic
        with self.microphone as source:
            print("[INFO] Calibrating mic for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"[INFO] Mic calibrated with threshold: {self.recognizer.energy_threshold}")

    def listen(self, fallback_lang="en-US", phrase_time_limit=10, timeout=1):
        with self.microphone as source:
            print("[INFO] Listening...")
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        # Convert sr.AudioData → WAV bytes
        wav_bytes = io.BytesIO(audio.get_wav_data())

        # Open as wave for numpy conversion
        with wave.open(wav_bytes, "rb") as wf:
            sr_ = wf.getframerate()
            nframes = wf.getnframes()
            audio_bytes = wf.readframes(nframes)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # Resample if not 16kHz (whisper expects 16000Hz)
        if sr_ != 16000:
            import librosa
            audio_np = librosa.resample(audio_np, orig_sr=sr_, target_sr=16000)

        # Run whisper
        start = time.time()
        result = self.model.transcribe(audio_np, fp16=False)
        text = result["text"].strip()
        print(time.time() - start)

        if text:
            try:
                detected_lang = detect(text)
            except:
                detected_lang = "unknown"
            return text, detected_lang
        return None, None
