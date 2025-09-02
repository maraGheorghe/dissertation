from typing import Dict, Iterator, Optional

from processor.models import whisper_model

def transcribe_with_whisper_per_chunk(
        local_path: str,
        *,
        language: str = "ro",
        vad_filter: bool = True,
        vad_parameters: Optional[Dict] = None,
        beam_size: int = 1,
        best_of: int = 1,
        temperature: float = 0.0,
        condition_on_previous_text: bool = False,
        include_language_in_seg: bool = False,
) -> Iterator[Dict]:
    """
    Yield Whisper transcription segments as:
      {
        "start": float,
        "end": float,
        "text": str,
        ["language": str]
      }
    """
    assert whisper_model is not None, "Model not loaded"

    segments_gen, info = whisper_model.transcribe(
        local_path,
        vad_filter=vad_filter,
        vad_parameters=vad_parameters or {"min_silence_duration_ms": 500},
        beam_size=beam_size,
        best_of=best_of,
        temperature=temperature,
        condition_on_previous_text=condition_on_previous_text,
    )

    lang = getattr(info, "language", language)

    for s in segments_gen:
        start = float(s.start)
        end = float(s.end)
        seg = {
            "start": start,
            "end": end,
            "text": s.text.strip()
        }
        if include_language_in_seg:
            seg["language"] = lang
        yield seg
