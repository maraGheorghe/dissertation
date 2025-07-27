import json
import os
import uuid
from datetime import datetime
from kafka import KafkaConsumer
from pathlib import Path
from dotenv import load_dotenv

from model.audio_file_event import AudioFileUploadedEvent
from minio_client import download_audio_file
from processor.voice_transcriber import transcribe_audio

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TOPIC")
DOWNLOAD_DIR = Path("resources/downloads")
SEPARATED_DIR = Path("resources/separated")

def prepare_directories():
    for folder in [DOWNLOAD_DIR, SEPARATED_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"Directory ready: {folder}")

def parse_event(data: dict) -> AudioFileUploadedEvent:
    # Dacă JSON-ul are datetime ca listă [yyyy, MM, dd, hh, mm, ss, µs]
    microseconds = data["uploadTime"][-1] // 1000  # convert µs → ms
    return AudioFileUploadedEvent(
        id=uuid.UUID(data["id"]),
        storage_key=data["originalName"],
        upload_time=datetime(*data["uploadTime"][:-1], microsecond=microseconds)
    )

def handle_audio_uploaded_event(event: AudioFileUploadedEvent):
    local_path = DOWNLOAD_DIR / event.storage_key
    download_audio_file(
        storage_key=event.storage_key,
        destination_path=str(local_path)
    )

    output_path = SEPARATED_DIR / str(event.id)
    transcription = transcribe_audio(str(local_path))

    print(transcription)

def start_consumer():
    prepare_directories()

    print(f"🎧 Listening on topic `{TOPIC}`...")
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    try:
        for message in consumer:
            data = message.value
            event = parse_event(data)
            print(f"📥 Received event for file: {event.storage_key}")
            handle_audio_uploaded_event(event)

    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped by user.")
    finally:
        consumer.close()
