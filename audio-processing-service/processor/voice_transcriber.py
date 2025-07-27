import os
import whisper

def transcribe_audio(input_path: str, model_size: str = "small") -> str:
    """
    Rulează Whisper pe fișierul audio și returnează textul transcris.

    :param input_path: cale către fișierul audio (.wav, .mp3 etc.)
    :param model_size: dimensiunea modelului Whisper (tiny, base, small, medium, large)
    :return: textul transcris
    """
    print(f"Transcribing {input_path} using Whisper ({model_size})...")

    model = whisper.load_model(model_size)
    result = model.transcribe(input_path, language="ro")

    print("Transcription complete.")
    return result["text"]
