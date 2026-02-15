import sounddevice as sd
import numpy as np
import soundfile as sf
import torch
import uuid
from collections import deque

from silero_vad import load_silero_vad, VADIterator


# Load VAD model
model = load_silero_vad()

# Slightly reduce sensitivity (default=0.5)
vad_iterator = VADIterator(model, threshold=0.6)


def record_until_silence(
    sample_rate=16000,
    max_silence_chunks=120,   # ~3.8 seconds silence tolerance
    pre_buffer_chunks=25     # capture speech slightly before detection
):

    print("Listening... Speak now.")

    vad_iterator.reset_states()

    chunk_size = 512  # Required by Silero for 16kHz
    stream = sd.InputStream(samplerate=sample_rate, channels=1)
    stream.start()

    audio_chunks = []
    pre_buffer = deque(maxlen=pre_buffer_chunks)

    speech_started = False
    silent_chunks = 0

    while True:
        chunk, _ = stream.read(chunk_size)
        chunk = chunk.flatten()

        pre_buffer.append(chunk)
        audio_tensor = torch.from_numpy(chunk)

        speech_dict = vad_iterator(audio_tensor, sample_rate)

        # 🎤 SPEECH DETECTED
        if speech_dict:
            if not speech_started:
                speech_started = True
                audio_chunks.extend(pre_buffer)  # include pre-speech buffer

            silent_chunks = 0
            audio_chunks.append(chunk)

        # 🤫 SILENCE AFTER SPEECH STARTED
        elif speech_started:
            silent_chunks += 1
            audio_chunks.append(chunk)

            # Stop only after long silence AND enough audio collected
            if silent_chunks > max_silence_chunks and len(audio_chunks) > 30:
                break

    stream.stop()
    stream.close()

    if len(audio_chunks) == 0:
        print("No speech detected.")
        return None

    full_audio = np.concatenate(audio_chunks)

    filename = f"temp_{uuid.uuid4()}.wav"
    sf.write(filename, full_audio, sample_rate)

    print("Stopped recording.")
    return filename
