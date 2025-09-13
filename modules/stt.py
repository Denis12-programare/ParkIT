import whisper
import speech_recognition as sr
import numpy as np
import io
import wave
import time
import keyboard  # pip install keyboard

class STT:
    def __init__(self, model_size="base", device_index=None, energy_threshold=300, pause_threshold=1.5):
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

    def listen_button(self, button="space", fallback_lang="en-US"):
        print(f"[INFO] Hold '{button}' to record... release to stop.")

        frames = []
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio_stream = source.stream

            # Start recording while button is held
            while keyboard.is_pressed(button):
                frame = audio_stream.read(source.CHUNK)
                frames.append(frame)

        if not frames:
            print("[WARN] No audio recorded.")
            return None, None

        # Save to WAV bytes
        wav_bytes = io.BytesIO()
        with wave.open(wav_bytes, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(source.SAMPLE_WIDTH)
            wf.setframerate(source.SAMPLE_RATE)
            wf.writeframes(b"".join(frames))
        wav_bytes.seek(0)

        # Convert to numpy
        with wave.open(wav_bytes, "rb") as wf:
            sr_ = wf.getframerate()
            nframes = wf.getnframes()
            audio_bytes = wf.readframes(nframes)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # Resample if needed
        if sr_ != 16000:
            import librosa
            audio_np = librosa.resample(audio_np, orig_sr=sr_, target_sr=16000)

        # Run whisper
        start = time.time()
        result = self.model.transcribe(audio_np, fp16=False)
        text = result["text"].strip()
        print(f"[INFO] Transcribed in {time.time() - start:.2f}s")

        if text:
            # try:
            #     detected_lang = detect(text)
            # except:
            #     detected_lang = "unknown"
            return text

        return None, None


# Example usage:
if __name__ == "__main__":
    stt = STT()
    while True:
        print("\nPress and hold SPACE to talk...")
        while not keyboard.is_pressed("space"):
            pass  # wait for press
        text = stt.listen_button("space")
        if text:
            print(f"[RESULT] {text}")
