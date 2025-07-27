import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    region_name='eu-west-1',
)

def download_audio_file(storage_key: str, destination_path: str):
    bucket = os.getenv("MINIO_BUCKET_NAME")
    s3.download_file(bucket, storage_key, destination_path)
    print(f"Downloaded: {storage_key} → {destination_path}")
