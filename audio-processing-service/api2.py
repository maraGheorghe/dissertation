# app.py
import os, shutil, uuid, tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import whisper  # or: from faster_whisper import WhisperModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
MODEL = None  # global

@app.on_event("startup")
def load_model_once():
    global MODEL
    # CPU OpenAI whisper:
    MODEL = whisper.load_model(MODEL_SIZE)
    # If switching to faster-whisper CPU:
    # MODEL = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    # save to /tmp (ephemeral, fast)
    suffix = Path(file.filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
        shutil.copyfileobj(file.file, tmp)
        local_path = tmp.name

    try:
        # OpenAI whisper:
        result = MODEL.transcribe(local_path, language="ro")
        segments = [
            {"start": float(s["start"]), "end": float(s["end"]),
             "text": s["text"].strip(), "speaker": "Unknown"}
            for s in result["segments"]
        ]
        # faster-whisper alternative:
        # segments_list, _ = MODEL.transcribe(local_path, vad_filter=True)
        # segments = [{"start": float(s.start), "end": float(s.end),
        #              "text": s.text.strip(), "speaker": "Unknown"} for s in segments_list]
        return {"segments": segments}
    except Exception as e:
        print(e)
        return {"error": str(e)}
    finally:
        try: os.remove(local_path)
        except Exception: pass
