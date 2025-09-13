import requests
from modules.stt import STT
from modules.tts import TTS

stt = STT()
tts = TTS()

# ---------------------
# Define scenarios
# ---------------------
SCENARIOS = {
    "not_paid": {
        "description": "Customer did not pay or cannot pay at exit",
        "frequency": "Sometimes",
        "system_action": "Screen displays payment due message upon customer arrival",
        "operator_actions": [
            "Instruct the customer to back out of the exit lane and make payment at a machine",
            "If they cannot back out: tell them they must make payment at a machine or ask others to move",
            "If stuck: instruct them to stand by, an attendant will respond",
            "If urgent: raise the barrier via 'Allow Crossing'"
        ]
    },
    "payment_not_registered": {
        "description": "Customer payment not registered at exit",
        "frequency": "Often",
        "system_action": "Screen displays payment due message upon customer arrival",
        "operator_actions": [
            "Verify VRN via ANPR camera or ticketID via IP camera",
            "Search VRN/ticketID in Multipark and review payment record",
            "Verify session info with customer (entry time, payment amount)",
            "If no payment: instruct to make payment",
            "If payment confirmed: raise barrier via 'Allow Crossing'"
        ]
    },
    "ticket_lost": {
        "description": "Customer lost parking ticket",
        "frequency": "Sometimes",
        "system_action": "Prompts customer to scan ticket",
        "operator_actions": [
            "Ask customer for entry time, entry location, VRN if available",
            "Search session in Multipark",
            "Issue lost ticket to exit terminal"
        ]
    },
    "vrn_mismatch": {
        "description": "Customer VRN mismatch at exit",
        "frequency": "Often",
        "system_action": "Screen displays VRN not found message",
        "operator_actions": [
            "Verify VRN via ANPR",
            "Search manually for VRN or close matches",
            "Confirm session details with customer (entry time, payment amount)",
            "Correct VRN in system if needed",
            "If possible: ask customer to back out & re-enter",
            "If not possible: raise barrier via 'Allow Crossing'"
        ]
    }
}

# ---------------------
# Classification helper
# ---------------------
def classify_issue(text: str) -> str:
    """Naive keyword-based classifier. Replace with AI model later."""
    text = text.lower()
    if "lost" in text and "ticket" in text:
        return "ticket_lost"
    if "not paid" in text or "forgot" in text or "cannot pay" in text:
        return "not_paid"
    if "payment not" in text or "not registered" in text:
        return "payment_not_registered"
    if "vrn" in text or "license plate" in text or "mismatch" in text:
        return "vrn_mismatch"
    return "unknown"

# ---------------------
# Main flow
# ---------------------
def main():
    text, lang = stt.listen(timeout=3)
    # text = "I seem to have lost my ticket and I don't know what"
    print(f"Customer said: {text}")

    # classify via Ollama (or fallback to local classifier)
    try:
        response = requests.post(
            "http://10.0.0.4:11434/api/generate",
            json={"model": "parking_assistant", "prompt": text, "stream": False}
        ).json()
        issue = response.get("response", "").strip()
    except Exception:
        issue = classify_issue(text)

    # If Ollama fails or returns unknown → fallback
    if issue not in SCENARIOS:
        issue = classify_issue(text)

    print(f"Detected issue: {issue}")

    if issue in SCENARIOS:
        scenario = SCENARIOS[issue]
        print(f"\nScenario: {scenario['description']}")
        print("System action:", scenario["system_action"])
        print("Operator actions:")
        for act in scenario["operator_actions"]:
            print(f" - {act}")
        # TTS feedback
        tts.speak(f"I detected {scenario['description']}.")
    else:
        print("\nCould not classify issue. Please escalate to human operator.")
        tts.speak("I could not identify the issue. Please contact the operator.")

if __name__ == "__main__":
    try:
        main()
    except:
        pass
