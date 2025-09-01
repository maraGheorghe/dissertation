import os, shutil, tempfile, json
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import torch
from faster_whisper import WhisperModel

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
MODEL: WhisperModel | None = None  # global


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once at startup."""
    global MODEL
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"[{now_iso()}] Loading faster-whisper '{MODEL_SIZE}' on {device} ({compute_type})...")
    MODEL = WhisperModel(MODEL_SIZE, device=device, compute_type=compute_type)
    print(f"[{now_iso()}] Model loaded.")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)


@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    """Non-streaming: return all segments at once."""
    assert MODEL is not None, "Model not loaded"
    print(f"[{now_iso()}] Started /transcribe.")
    suffix = Path(file.filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
        shutil.copyfileobj(file.file, tmp)
        local_path = tmp.name
    print(f"[{now_iso()}] File cached at {local_path}.")

    try:
        segments_gen, info = MODEL.transcribe(
            local_path,
            language="ro",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            beam_size=1, best_of=1, temperature=0.0,
            condition_on_previous_text=False,
        )
        segments = [
            {
                "start": float(s.start),
                "end": float(s.end),
                "text": s.text.strip(),
                "speaker": "Unknown",
            }
            for s in segments_gen
        ]
        print(f"[{now_iso()}] Finished /transcribe.")
        return {"language": info.language, "segments": segments}
    finally:
        try:
            os.remove(local_path)
        except Exception:
            pass


@app.post("/transcribe_stream")
async def transcribe_stream(file: UploadFile = File(...)):
    """
    Streaming: yields newline-delimited JSON (NDJSON) for each segment as soon as it's ready.
    Each line looks like:
      {"ts":"2025-01-01T12:00:00.123Z","start":0.0,"end":1.9,"text":"...","language":"ro"}
    """
    assert MODEL is not None, "Model not loaded"
    print(f"[{now_iso()}] Started /transcribe_stream.")
    suffix = Path(file.filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
        shutil.copyfileobj(file.file, tmp)
        local_path = tmp.name
    print(f"[{now_iso()}] File cached at {local_path}.")

    def gen():
        try:
            segments_gen, info = MODEL.transcribe(
                local_path,
                language="ro",
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
                beam_size=1, best_of=1, temperature=0.0,
                condition_on_previous_text=False,
            )

            # send a header event with detected language
            header = {"ts": now_iso(), "language": info.language, "type": "header"}
            print(f"[{header['ts']}] Language: {info.language}")
            yield json.dumps(header) + "\n"

            for s in segments_gen:
                payload = {
                    "ts": now_iso(),
                    "start": float(s.start),
                    "end": float(s.end),
                    "text": s.text.strip(),
                    "language": info.language,
                    "type": "segment",
                }
                # print to server logs
                print(f"[{payload['ts']}] {payload['start']:.2f}–{payload['end']:.2f} {payload['text']}", flush=True)
                # stream to client
                yield json.dumps(payload) + "\n"

            tail = {"ts": now_iso(), "type": "done"}
            print(f"[{tail['ts']}] Finished /transcribe_stream.")
            yield json.dumps(tail) + "\n"

        finally:
            try:
                os.remove(local_path)
            except Exception:
                pass

    # NDJSON is easy to consume; if you prefer SSE, set media_type="text/event-stream"
    return StreamingResponse(gen(), media_type="application/x-ndjson")


