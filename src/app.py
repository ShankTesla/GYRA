import json
import pandas as pd
import numpy as np
import os
import sys
import onnxruntime as rt
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
from contextlib import asynccontextmanager


class Data(BaseModel):
    Time: float = Field(alias='Time')
    V1: float = Field(alias='V1')
    V2: float = Field(alias='V2')
    V3: float = Field(alias='V3')
    V4: float = Field(alias='V4')
    V5: float = Field(alias='V5')
    V6: float = Field(alias='V6')
    V7: float = Field(alias='V7')
    V8: float = Field(alias='V8')
    V9: float = Field(alias='V9')
    V10: float = Field(alias='V10')
    V11: float = Field(alias='V11')
    V12: float = Field(alias='V12')
    V13: float = Field(alias='V13')
    V14: float = Field(alias='V14')
    V15: float = Field(alias='V15')
    V16: float = Field(alias='V16')
    V17: float = Field(alias='V17')
    V18: float = Field(alias='V18')
    V19: float = Field(alias='V19')
    V20: float = Field(alias='V20')
    V21: float = Field(alias='V21')
    V22: float = Field(alias='V22')
    V23: float = Field(alias='V23')
    V24: float = Field(alias='V24')
    V25: float = Field(alias='V25')
    V26: float = Field(alias='V26')
    V27: float = Field(alias='V27')
    V28: float = Field(alias='V28')
    Amount: float = Field(alias='Amount')

    model_config = ConfigDict(
        populate_by_name= True # Allows Instantiation properly
    )


ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    #this is how to get onnx session model imported
    ml_models["onnx_session"] = rt.InferenceSession('./models/model.onnx')
    yield
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.post('/predict')
async def predict(input_data: Data):
    sess = ml_models["onnx_session"]

    input_dict = input_data.model_dump(by_alias=True)
    df = pd.DataFrame([input_dict])

    # Converting data to ONNX acceptable format
    raw_data = df.values.astype(np.float32)

    # ONNX inference is below
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    prediction = sess.run([label_name], {input_name: raw_data})

    return {'prediction': int(prediction[0])}
