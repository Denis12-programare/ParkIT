import requests
import webbrowser
import keyboard
from modules.stt import STT
from modules.tts import TTS

stt = STT()


def send_recive():
    tts = TTS()
    text= stt.listen_button()
    print(f"Customer said: {text}")
    intent = requests.post("http://10.0.0.4:8000/get_intent", json={"input": text})
    print(intent.text)
    intent = intent.json()
    intent = intent["intent"].strip()
    print(intent)
    # tts.speak(resp)

    

    match intent:
        case "ticket_lost" : 
            tts.speak("Please state your entry time: ")
            entry_time = input("\rPlease state your entry time: ")
            text = requests.post(f"http://10.0.0.4:8000/decision", json={"intent": intent,"entry_time": entry_time}).json()
            tts.speak(text["tts_invokation"].strip())
            print(text['new_ticket'].strip())
        case "no_payment_confirmation":
            tts.speak("Please state your entry time: ")
            entry_time = input("\rPlease state your entry time: ")
            tts.speak("Please state your ticket code: ") 
            ticket_code = input("Please state your ticket code: ")
            text = requests.post(f"http://10.0.0.4:8000/decision", json={"intent": intent,"entry_time": entry_time, "ticket_code": ticket_code})
            if (text.status_code!=200):
                print(text.json()["status"])
                return
            print(text.json()["tts_invokation"].strip())
            tts.speak(text.json()["tts_invokation"].strip())

            webbrowser.open_new_tab(f"http://10.0.0.4:8000/pay?token={ticket_code}")




def main():
    while True:
            print("\nPress and hold SPACE to talk...")
            while not keyboard.is_pressed("space"):
                pass  # wait for press
            send_recive()


if __name__ == "__main__":
        main()
