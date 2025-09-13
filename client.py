import requests
import keyboard
from modules.stt import STT
from modules.tts import TTS

stt = STT()


def send_recive():
    tts = TTS()
    text= stt.listen_button()
    print(f"Customer said: {text}")
    resp = requests.post("http://10.0.0.4:8000/decision", json={"input": text}).json()["resp"].strip()
    print(resp)
    tts.speak(resp)

def main():
    while True:
        try:
            print("\nPress and hold SPACE to talk...")
            while not keyboard.is_pressed("space"):
                pass  # wait for press
            send_recive()
        except:
            pass


if __name__ == "__main__":
    try:
        main()
    except:
        pass
