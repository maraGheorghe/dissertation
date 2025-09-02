import torch
import os
from faster_whisper import WhisperModel

from utils.utils import now_iso

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
whisper_model: WhisperModel | None = None

device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
print(f"[{now_iso()}] Loading faster-whisper '{MODEL_SIZE}' on {device} ({compute_type})...")
whisper_model = WhisperModel(MODEL_SIZE, device=device, compute_type=compute_type)
print(f"[{now_iso()}] Model loaded.")