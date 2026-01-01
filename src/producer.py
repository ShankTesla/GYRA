import json 
import csv 
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import time
import os

#configs
BROKER = os.getenv('KAFKA_BROKER', 'kafka:29092')
TOPIC_NAME = 'creditcard'
CSV_FILE_PATH = './data/processed/test_stream.csv'

# Wait for Kafka to be ready
print(f"Waiting for Kafka broker at {BROKER}...")
for i in range(30):  # Try for 30 seconds
    try:
        producer = KafkaProducer(
            bootstrap_servers=[BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Successfully connected to Kafka at {BROKER}")
        break
    except NoBrokersAvailable:
        print(f"Kafka not ready, retrying... ({i+1}/30)")
        time.sleep(1)
else:
    print("Failed to connect to Kafka after 30 seconds")
    exit(1)

def produce_message_to_broker(filepath, topic):
    try:
        with open(filepath, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                producer.send(topic, value=row)
                time.sleep(0.1)
            print("all rows sent")
        producer.flush()
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
    except Exception as e:
        print(f"Encountered Error: {e}")
    finally:
        producer.close()
        print("Producer connection closed.")

if __name__ == "__main__":
    produce_message_to_broker(CSV_FILE_PATH, TOPIC_NAME)