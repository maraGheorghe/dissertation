from consumer import start_consumer
from model.base import Base
from db.session import engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    print("Starting audio-processing-service...")
    start_consumer()