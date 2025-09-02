from communication.kafka_communication import start_kafka
from db_model.base import Base
from storage.session import engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    print("Starting audio-transcription-service...")
    start_kafka()
