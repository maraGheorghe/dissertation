import os
import subprocess
import tempfile
from typing import Generator
import torch
import whisper
import whisperx
from pydub import AudioSegment
from pydub.silence import split_on_silence


def extract_audio_if_needed(file_path: str) -> str:
    """
    If the input is a video file, extract the audio and return the path to the audio file.
    If already audio, return original path.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".mp4", ".mov", ".mkv", ".webm"]:  # common video formats
        tmp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_audio.close()
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-vn", tmp_audio.name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return tmp_audio.name
    return file_path

def transcribe_with_whisper_per_chunk(audio_path: str, language: str = "ro", model_size: str = "small") -> Generator[dict, None, None]:
    """
    Transcribes a video or audio file in silence-detected chunks using OpenAI Whisper.
    Yields each segment as soon as it's transcribed.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Whisper model ({model_size}) on {device}...")
    model = whisper.load_model(model_size).to(device)

    print("Checking and extracting audio if needed...")
    actual_audio_path = extract_audio_if_needed(audio_path)

    print("Splitting audio into silence-based chunks...")
    chunks = split_audio_on_silence(actual_audio_path)

    total_elapsed = 0.0

    for i, chunk in enumerate(chunks):
        print(f"🔍 Processing chunk {i+1}/{len(chunks)}")

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            chunk.export(tmp.name, format="wav")

            result = model.transcribe(tmp.name, language=language, fp16=False)

            for seg in result["segments"]:
                yield {
                    "start": seg["start"] + total_elapsed,
                    "end": seg["end"] + total_elapsed,
                    "text": seg["text"].strip(),
                    "speaker": "Unknown"
                }

        total_elapsed += chunk.duration_seconds


def split_audio_on_silence(path: str, min_silence_len=700, silence_thresh=-40, keep_silence=300) -> list[AudioSegment]:
    audio = AudioSegment.from_file(path)
    return split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )


def transcribe_with_whisperx_per_chunk(audio_path: str, language: str = "ro", model_size: str = "small") -> Generator[dict, None, None]:
    """
    Transcribes an audio file in silence-detected chunks using WhisperX.
    Yields each segment as soon as it's transcribed.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading WhisperX model ({model_size}) on {device}...")
    model = whisperx.load_model(model_size, device=device, language=language, compute_type="float32")

    print("Splitting audio into silence-based chunks...")
    chunks = split_audio_on_silence(audio_path)

    # Keep track of running timestamp offset
    total_elapsed = 0.0

    for i, chunk in enumerate(chunks):
        print(f"🔍 Processing chunk {i+1}/{len(chunks)}")

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            chunk.export(tmp.name, format="wav")

            # 1. Transcribe
            result = model.transcribe(tmp.name)

            # 2. Align for word-level timestamps
            model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
            result_aligned = whisperx.align(result["segments"], model_a, metadata, tmp.name, device)

            for seg in result_aligned["segments"]:
                yield {
                    "start": seg["start"] + total_elapsed,
                    "end": seg["end"] + total_elapsed,
                    "text": seg["text"].strip(),
                    "speaker": seg.get("speaker", "Unknown")
                }

        # Add chunk duration to offset for next segment
        total_elapsed += chunk.duration_seconds


def transcribe_audio(input_path: str, model_size: str = "small") -> list[dict]:
    """
    Transcribe audio using Whisper and return a list of segments.

    :param input_path: Path to audio file
    :param model_size: Whisper model size (tiny, base, small, medium, large)
    :return: List of dicts with start, end, text
    """
    print(f"Transcribing {input_path} using Whisper ({model_size})...")

    model = whisper.load_model(model_size)
    result = model.transcribe(input_path, language="ro")

    print("Transcription complete.")

    return [
        {
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": seg["text"].strip(),
            "speaker": "Unknown"  # optional, can replace later
        }
        for seg in result["segments"]
    ]
