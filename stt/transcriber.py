import whisper

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)
        print("Model loaded.")

    import whisper

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)
        print("Model loaded.")

    def transcribe(self, audio_path):
        result = self.model.transcribe(
            audio_path,
            language="en",      # Force English
            task="transcribe"   # (default, but explicit is cleaner)
        )
        return result["text"]

