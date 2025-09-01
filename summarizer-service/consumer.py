import json
import os
import uuid

from pathlib import Path
from dotenv import load_dotenv

from model.audio_file_event import AudioFileTranslated
from summarizer import create_summary
from kafka import KafkaConsumer

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TOPIC")
DOWNLOAD_DIR = Path("resources/downloads")
SEPARATED_DIR = Path("resources/separated")

def parse_event(data: dict) -> AudioFileTranslated:
    return AudioFileTranslated(
        id=uuid.UUID(data["id"]),
    )

def start_consumer():

    print(f"Listening on topic {TOPIC}...")
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
            print(f"Received event for file: {event.id}")
            try:
                create_summary(event)
            except Exception as e:
                print("Audio already added.")
                print(e)


    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped by user.")
    finally:
        consumer.close()

