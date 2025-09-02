from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from storage.session import SessionLocal
from db_model import Transcript, Segment
from fastapi.middleware.cors import CORSMiddleware

from db_model.summary import Summary

app = FastAPI(title="API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- DB session dependency that closes ---
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SegmentOut(BaseModel):
    start: float
    end: float
    text: str

class TranscriptOut(BaseModel):
    id: str
    status: str
    done: bool
    segments: List[SegmentOut]
    updated_at: Optional[str] = None

class SummaryOut(BaseModel):
    id: str
    text: str

@app.get("/api/transcripts/{transcript_id}", response_model=TranscriptOut)
def get_transcript(transcript_id: str, session: Session = Depends(get_session)):
    t: Optional[Transcript] = session.get(Transcript, transcript_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transcript not found")

    seg_rows: List[Segment] = (
        session.execute(
            select(Segment)
            .where(Segment.transcript_id == transcript_id)
            .order_by(Segment.start.asc())
        )
        .scalars()
        .all()
    )

    segments = [
        SegmentOut(
            start=float(s.start),
            end=float(s.end),
            text=(s.text or "").strip(),
        )
        for s in seg_rows
    ]

    return TranscriptOut(
        id=transcript_id,
        status=t.status,
        done=t.status == "completed",
        segments=segments,
        updated_at=t.created_at.isoformat() if getattr(t, "created_at", None) else None,
    )

@app.get("/api/summary/{transcript_id}", response_model=SummaryOut)
def get_summary(transcript_id: str, session: Session = Depends(get_session)):
    s: Optional[Summary] = (
        session.execute(select(Summary).where(Summary.transcript_id == transcript_id))
        .scalar_one_or_none()
    )
    if not s:
        raise HTTPException(status_code=404, detail="Summary not found")

    return SummaryOut(
        id=transcript_id,
        text=getattr(s, "content", None) or "",
    )

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8082, reload=True)