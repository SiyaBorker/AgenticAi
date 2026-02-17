from stt.stt_service import STTService
from intent.intent_parser import parse_intent
from pathresolve.persistent_folder_indexer import get_or_initialize_index, resolve_folder

if __name__ == "__main__":

    # Initialize persistent folder index
    folder_index = get_or_initialize_index()

    # Initialize voice system
    stt = STTService()

    print("Voice Agent Ready...\n")

    while True:

        # Voice → Text
        text = stt.listen()

        if not text:
            continue

        print("\nYou said:", text)

        # Text → Intent
        intent = parse_intent(text)

        if not intent:
            print("Could not parse intent.\n")
            continue

        print("\nParsed Intent:", intent)

        # Resolve folder path
        if intent.get("source"):
            resolved_path = resolve_folder(intent["source"], folder_index)

            if resolved_path:
                intent["resolved_source_path"] = resolved_path
                print(f"\nResolved Path: {resolved_path}")
            else:
                intent["resolved_source_path"] = None
                print("\n⚠ Could not resolve source folder.")

        print("\nFinal Intent Ready For Controller:")
        print(intent)
