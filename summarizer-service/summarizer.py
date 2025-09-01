import os
import re
import json
import httpx
from sqlalchemy import asc

from db.session import SessionLocal
from model import Segment, Transcript
from model.audio_file_event import AudioFileTranslated
from model.summary import Summary

# ----------------- LLM / Ollama config -----------------
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
NUM_CTX      = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
TIMEOUT      = int(os.getenv("OLLAMA_TIMEOUT", "600"))
NUM_THREAD   = os.cpu_count() or 4

# ----------------- Chunking + generation knobs -----------------
# If the whole transcript is <= SINGLE_MAX_CHARS, we do ONE call.
SINGLE_MAX_CHARS     = int(os.getenv("SINGLE_MAX_CHARS", "3500"))
SINGLE_NUM_PREDICT   = int(os.getenv("SINGLE_NUM_PREDICT", "380"))

# If longer, we chunk to ~MAX_CHARS with small overlap, do "map" bullets, then one "reduce".
MAX_CHARS            = int(os.getenv("CHUNK_MAX_CHARS", "3200"))
OVERLAP_CHARS        = int(os.getenv("CHUNK_OVERLAP_CHARS", "120"))
MAP_NUM_PREDICT      = int(os.getenv("MAP_NUM_PREDICT", "70"))   # small, fast
REDUCE_NUM_PREDICT   = int(os.getenv("REDUCE_NUM_PREDICT", "220"))

# ----------------- Prompts -----------------
PROMPT_SINGLE = (
    "Summarize the following transcript into clean Markdown. Keep the same language as in the transcript. Include:\n"
    "- A short abstract (2–3 sentences)\n"
    "- Then 5–7 concise bullets highlighting key ideas\n\n"
    "Transcript:\n\"\"\"{text}\"\"\""
)

PROMPT_MAP = (
    "From the following transcript part, extract exactly 3 concise bullets (≤15 words each).\n"
    "Use the same language.\n"
    "No preamble, just bullets.\n\n"
    "Part:\n\"\"\"{text}\"\"\""
)

PROMPT_REDUCE = (
    "You are given many bullets extracted from a long transcript. "
    "Write a final, well-structured summary in the same language as the bullets with:\n"
    "- A short summary (≈200–300 words)\n"
    "- bullets with the most important points (≤15 words each)\n"
    "Avoid repetition, merge duplicates, keep names/dates/numbers exact.\n\n"
    "Bullets:\n\"\"\"{bullets}\"\"\""
)

# ----------------- Helpers -----------------
def _collapse_ws(s: str) -> str:
    return " ".join((s or "").replace("\r", " ").replace("\n", " ").split()).strip()

def _chunks(s: str, size=MAX_CHARS, overlap=OVERLAP_CHARS):
    s = _collapse_ws(s)
    i, n = 0, len(s)
    while i < n:
        j = min(i + size, n)
        yield s[i:j]
        i = j - overlap if j < n else j

def _ollama_generate(prompt: str, num_predict: int) -> str:
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": NUM_CTX,
                    "num_predict": num_predict,
                    "num_thread": NUM_THREAD,
                },
            },
        )
        r.raise_for_status()
        return r.json()["response"].strip()

def _bullets_only(text: str) -> list[str]:
    """Extract lines that look like bullets; fallback to splitting lines."""
    lines = [ln.strip() for ln in text.splitlines()]
    bullets = []
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("- "):
            bullets.append(ln[2:].strip())
        elif ln.startswith("* "):
            bullets.append(ln[2:].strip())
        else:
            # sometimes the model returns plain lines; treat as bullets
            bullets.append(ln)
    # keep it short
    return [b for b in bullets if b][:3]

# ----------------- Main entry -----------------
def create_summary(event: AudioFileTranslated):
    session = SessionLocal()
    try:
        # 1) Find transcript (you indicated Transcript.id == event.id)
        transcript = (
            session.query(Transcript)
            .filter(Transcript.id == str(event.id))  # if UUID(as_uuid=True), drop str()
            .one_or_none()
        )
        if transcript is None:
            print(f"No Transcript found for event_id={event.id}")
            return

        # 2) Load segments and construct full text
        segments = (
            session.query(Segment)
            .filter(Segment.transcript_id == transcript.id)
            .order_by(asc(Segment.start))
            .all()
        )
        if not segments:
            print(f"No Segments for transcript_id={transcript.id}")
            return

        full_text = _collapse_ws(" ".join((s.text or "") for s in segments))
        if not full_text:
            print("Transcript has no text.")
            return

        # Warm-up (optional, avoids first-call latency)
        try:
            _ollama_generate("OK", num_predict=1)
        except Exception:
            pass

        if len(full_text) <= SINGLE_MAX_CHARS:
            final_md = _ollama_generate(PROMPT_SINGLE.format(text=full_text), num_predict=SINGLE_NUM_PREDICT)

        else:
            all_bullets: list[str] = []
            for idx, ch in enumerate(_chunks(full_text), 1):
                mini = _ollama_generate(PROMPT_MAP.format(text=ch), num_predict=MAP_NUM_PREDICT)
                print(mini)
                all_bullets.extend(_bullets_only(mini))

            if not all_bullets:
                final_md = _ollama_generate(PROMPT_SINGLE.format(text=full_text[:SINGLE_MAX_CHARS]), num_predict=SINGLE_NUM_PREDICT)
                print(final_md)
            else:
                joined = "\n".join(f"- {b}" for b in all_bullets)
                final_md = _ollama_generate(PROMPT_REDUCE.format(bullets=joined), num_predict=REDUCE_NUM_PREDICT)
                print(final_md)

        existing = (
            session.query(Summary)
            .filter(Summary.transcript_id == transcript.id)
            .one_or_none()
        )
        if existing:
            existing.content = final_md
        else:
            session.add(Summary(
                transcript_id=transcript.id,
                content=final_md,
            ))

        session.commit()
        print(f"Saved summary (summaries.transcript_id={transcript.id})")

    except Exception as e:
        session.rollback()
        print("Failed to create/save summary:", e)
        raise
    finally:
        session.close()
