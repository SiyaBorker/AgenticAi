import os
from .recorder import record_until_silence
from .transcriber import WhisperTranscriber


class STTService:
    def __init__(self):
        self.transcriber = WhisperTranscriber("base")

    def listen(self):
        audio_file = record_until_silence()
        print("Audio saved at:", audio_file)
        text = self.transcriber.transcribe(audio_file)

        # Optional: delete temp file after transcription
        if os.path.exists(audio_file):
            os.remove(audio_file)

        return text
