import json
import os
import uuid

from dotenv import load_dotenv
from kafka import KafkaConsumer

from communication.audio_file_event import AudioFileTranslated
from llama_model.summarizer import create_summary

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC = os.getenv("KAFKA_TOPIC")

def parse_event(data: dict) -> AudioFileTranslated:
    return AudioFileTranslated(
        id=uuid.UUID(data["id"]),
    )

def start_consumer():

    print(f"Listening on topic {TOPIC}...")
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
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
                print("Error summarizing.")
                print(e)

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        consumer.close()