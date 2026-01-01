import json
import numpy as np
import onnxruntime as rt
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import os
import time
import redis

# Use environment variable or default to kafka service
BROKER = os.getenv('KAFKA_BROKER', 'kafka:29092')
TOPIC_NAME = 'creditcard'

#REDIS environment
r = redis.Redis(
    host='redis',
    port=6379,
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

sess = rt.InferenceSession('./models/model.onnx')
input_name = sess.get_inputs()[0].name
label_name = sess.get_outputs()[0].name

# Define the exact predictors used during training
predictors = ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
              'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19',
              'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28',
              'Amount']

# Wait for Kafka to be ready
print(f"Waiting for Kafka broker at {BROKER}...")
for i in range(30):  # Try for 30 seconds
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[BROKER],
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        print(f"Successfully connected to Kafka at {BROKER}")
        break
    except NoBrokersAvailable:
        print(f"Kafka not ready, retrying... ({i+1}/30)")
        time.sleep(1)
else:
    print("Failed to connect to Kafka after 30 seconds")
    exit(1)

print("Listening for transactions on Kafka...")

for message in consumer:
    data_dict = message.value
    
    # Extract only the predictor columns in the correct order
    features = np.array([[data_dict[col] for col in predictors]]).astype(np.float32)
    
    prediction = sess.run([label_name], {input_name: features})

    if prediction[0] == 0:
        try:
            count = r.incr("non_fraud_count_now")
            r.expire("non_fraud_count_now", 3600)
        except Exception as e:
            print(f"Redis error: {e}")
    
    print(f"Transaction ID: {data_dict.get('Time')} | Prediction: {prediction[0]}")



