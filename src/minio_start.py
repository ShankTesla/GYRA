import boto3
import os
from dotenv import load_dotenv

#load env
load_dotenv()


def make_minio_bucket():
#MINIO and mlflow config
    

    # Tell MLflow where MinIO is
    endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "mlflow")

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url = endpoint,
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key
        )

        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f'Bucket: {bucket_name} already exists')
            return True
        except:
            # Bucket doesn't exist, create it
            s3_client.create_bucket(Bucket=bucket_name)
            print(f'Bucket: {bucket_name} created')
            return True

    except Exception as e:
        print(f"Error Error => {e}")
        return
    
if __name__ == "__main__":
    make_minio_bucket()