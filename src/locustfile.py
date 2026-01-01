import random
import pandas as pd
from itertools import cycle
from locust import HttpUser, task, between
import time

# load data
test_df = pd.read_csv("./data/processed/test_stream.csv")
# convert to dict records
test_records = test_df.to_dict(orient='records')
#make it into cycle iterator that can cycle through records
data_iterator = cycle(test_records)



class MLModelUser(HttpUser):
    wait_time = between(1,5)

    #standard check
    @task(9)
    def predict_endpoint(self):
        payload = next(data_iterator)

        #Send post rqst
        self.client.post("/predict", json=payload)
    
    #fraud check
    def burst_attack(self):
        for _ in range(random.randint(5,15)):
            payload = next(data_iterator)
            self.client.post("/predict", json=payload)
            #short delay
            time.sleep(0.1)