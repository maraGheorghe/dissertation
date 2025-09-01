from typing import Dict, Iterator, List, Optional

from model.models import whisper_model


def _pick_speaker(start: float, end: float, diarization: Optional[List[Dict]]) -> Optional[str]:
    """Pick the speaker label for the segment [start, end) from diarization list."""
    if not diarization:
        return None
    seg_mid = (start + end) / 2.0
    best = None
    best_overlap = 0.0
    for d in diarization:
        if d["end"] <= start or d["start"] >= end:
            continue
        overlap = min(end, d["end"]) - max(start, d["start"])
        if overlap > best_overlap or (overlap == best_overlap and best is None and d.get("speaker")):
            best = d.get("speaker")
            best_overlap = overlap
    if best is None:
        nearest = min(diarization, key=lambda d: abs(((d["start"] + d["end"]) / 2.0) - seg_mid))
        best = nearest.get("speaker")
    return best


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
        diarization: Optional[List[Dict]] = None,
) -> Iterator[Dict]:
    """
    Yield Whisper transcription segments as:
      {
        "start": float,
        "end": float,
        "text": str,
        "speaker": Optional[str],
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
            "text": s.text.strip(),
            "speaker": _pick_speaker(start, end, diarization),
        }
        if include_language_in_seg:
            seg["language"] = lang
        yield seg
