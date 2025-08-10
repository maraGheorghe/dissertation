# app.py  — faster-whisper version
import os, shutil, tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import torch
from faster_whisper import WhisperModel

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
MODEL: WhisperModel | None = None  # global

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the model once at startup, prefer GPU if available.
    - GPU: float16 for speed/accuracy
    - CPU: int8 for speed/low memory
    """
    global MODEL
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"Loading faster-whisper model '{MODEL_SIZE}' on {device} ({compute_type})...")
    MODEL = WhisperModel(MODEL_SIZE, device=device, compute_type=compute_type)
    print("Model loaded.")
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    assert MODEL is not None, "Model not loaded"
    print("Started the transcribe function.")
    suffix = Path(file.filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
        shutil.copyfileobj(file.file, tmp)
        local_path = tmp.name
    print("Done with copy of the file.")

    try:
        print("Starting the transcription.")
        # VAD skips silence; tweak params as you like
        segments_gen, info = MODEL.transcribe(
            local_path,
            language="ro",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            # You can also set beam_size, temperature, etc.
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
        print("Done with the transcription.")
        return {"segments": segments}
    finally:
        try:
            os.remove(local_path)
        except Exception:
            pass
