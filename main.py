from stt.stt_service import STTService

if __name__ == "__main__":
    stt = STTService()
    text = stt.listen()
    print("\nYou said:", text)
