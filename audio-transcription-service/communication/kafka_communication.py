import json
import os
import uuid
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from pathlib import Path
from dotenv import load_dotenv

from communication.audio_file_event import AudioFileUploadedEvent
from storage.minio_client import download_audio_file
from processor.voice_transcriber import transcribe_with_whisper_per_chunk
from storage.session import SessionLocal
from db_model.transcript import Transcript
from db_model.segment import Segment

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TOPIC")
TOPIC_PRODUCER = os.getenv("KAFKA_TOPIC_PRODUCER")
DOWNLOAD_DIR = Path("resources/downloads")

def prepare_directories():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Directory ready: {DOWNLOAD_DIR}")

def parse_event(data: dict) -> AudioFileUploadedEvent:
    microseconds = data["uploadTime"][-1] // 1000  # convert NANOS → MICROSECONDS pentru datetime()
    return AudioFileUploadedEvent(
        id=uuid.UUID(data["id"]),
        storage_key=data["originalName"],
        upload_time=datetime(*data["uploadTime"][:-1], microsecond=microseconds)
    )

def handle_audio_uploaded_event(event: AudioFileUploadedEvent):
    session = SessionLocal()

    # 1) creează transcript entry in_progress
    transcript = Transcript(id=event.id)
    session.add(transcript)
    session.commit()

    # 2) descarcă fișierul din MinIO pentru transcriere
    local_path = DOWNLOAD_DIR / event.storage_key
    download_audio_file(
        storage_key=event.storage_key,
        destination_path=str(local_path)
    )

    for seg in transcribe_with_whisper_per_chunk(str(local_path)):
        print(seg)
        s = Segment(
            transcript_id=event.id,
            start=seg["start"],
            end=seg["end"],
            text=seg["text"]
        )
        session.add(s)
        session.commit()

    # 4) marchează transcriptul ca finalizat
    transcript.status = "completed"
    session.commit()
    session.close()

    print(f"Transcript salvat în DB: {event.id}")

def start_kafka():
    prepare_directories()

    print(f"Listening on topic `{TOPIC}`...")
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        for message in consumer:
            data = message.value
            event = parse_event(data)
            print(f"Received event for file: {event.storage_key}")
            try:
                handle_audio_uploaded_event(event)

                produced_data = {
                    "id": str(event.id),
                }
                producer.send(TOPIC_PRODUCER, value=produced_data)
                producer.flush()
                print(f"Event sent to producer: {produced_data}")
            except Exception as e:
                print("Audio already added.")
                print(e)

    except KeyboardInterrupt:
        print("\n Consumer stopped by user.")
    finally:
        consumer.close()