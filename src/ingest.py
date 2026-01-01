import pandas as pd
from sqlalchemy import create_engine
import os 
from dotenv import load_dotenv
import sys
from prefect import task
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


@task(retries=3, retry_delay_seconds=60)
def ingest():
    load_dotenv()

    
    file_name = 'creditcard'
    file_path = DATA_DIR / f"{file_name}.csv"
    df = pd.read_csv(file_path)

    #environment
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB', 'postgres')

    conn_string = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(conn_string)

    df.to_sql('credit_card_fraud', engine, if_exists='replace', index=False)

    print(f"Success! Data uploaded to {db_name} on port {port}.")
    return True

if __name__ == "__main__":
    ingest()
