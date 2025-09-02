from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from storage.session import SessionLocal
from db_model import Transcript, Segment
from fastapi.middleware.cors import CORSMiddleware

from db_model.summary import Summary

app = FastAPI(title="Transcript API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
    allow_credentials=True,  # Whether to allow cookies to be sent with cross-origin requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


class SegmentOut(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[str] = None

class TranscriptOut(BaseModel):
    id: str
    status: str
    done: bool
    language: Optional[str] = None
    segments: List[SegmentOut]
    updated_at: Optional[str] = None

class SummaryOut(BaseModel):
    id: str
    text: str


@app.get("/api/transcripts/{transcript_id}", response_model=TranscriptOut)
def get_transcript(transcript_id: str):
    session = SessionLocal()
    t: Optional[Transcript] = session.get(Transcript, transcript_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transcript not found")
    seg_rows: List[Segment] = session.execute(
        select(Segment)
        .where(Segment.transcript_id == transcript_id)
        .order_by(Segment.start.asc())
    ).scalars().all()

    segments = [
        SegmentOut(
            start=float(s.start),
            end=float(s.end),
            text=(s.text or "").strip(),
            speaker=getattr(s, "speaker", None),
        )
        for s in seg_rows
    ]
    return TranscriptOut(
        id=transcript_id,
        status=t.status,
        done=t.status == "completed",
        language=getattr(t, "language", None),
        segments=segments,
        updated_at=t.created_at.isoformat() if t.created_at else None,
    )

@app.get("/api/summary/{transcript_id}", response_model=SummaryOut)
def get_transcript(transcript_id: str):
    session = SessionLocal()
    # 1) Load the transcript/event row (to read language, status, timestamps)
    s: Optional[Summary] = session.execute(
        select(Summary).where(Summary.transcript_id == transcript_id)
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Summary not found")

    print(getattr(s, "content", None))
    return SummaryOut(
        id=transcript_id,
        text=getattr(s, "content", None),
    )

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8082, reload=True)

