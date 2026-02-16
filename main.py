from stt.stt_service import STTService
from intent_parser import parse_intent

if __name__ == "__main__":
    stt = STTService()
    text = stt.listen()
    print("\nYou said:", text)
    
    # Parse the extracted text through intent parser
    if text:
        intent = parse_intent(text)
        print("\n✅ Parsed Intent:", intent)
