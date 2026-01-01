import pandas as pd 
import numpy as np
import os 
import sys
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pickle
import onnxmltools
# CHANGE THIS LINE:
from onnxmltools.convert.common.data_types import FloatTensorType
import pickle
from prefect import task 
from prefect.artifacts import create_markdown_artifact
#MLFLOW and minio
import mlflow
import mlflow.onnx
import boto3

import gc
from datetime import datetime 
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score
import xgboost as xgb
import os



pd.set_option('display.max_columns', 100)

#S3 config
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION', 'ap-south-1')


RFC_METRIC = 'gini'  #metric used for RandomForrestClassifier
NUM_ESTIMATORS = 100 #number of estimators used for RandomForrestClassifier
NO_JOBS = 4 #number of parallel jobs used for RandomForrestClassifier


#TRAIN/VALIDATION/TEST SPLIT
#VALIDATION
VALID_SIZE = 0.20 # simple validation using train_test_split
TEST_SIZE = 0.20 # test size using_train_test_split

#CROSS-VALIDATION
NUMBER_KFOLDS = 5 #number of KFolds for cross-validation



RANDOM_STATE = 2018

MAX_ROUNDS = 1000 #lgb iterations
EARLY_STOP = 50 #lgb early stop 
OPT_ROUNDS = 1000  #To be adjusted based on best validation rounds
VERBOSE_EVAL = 50 #Print out metric result

IS_LOCAL = False

@task(retries=3, retry_delay_seconds=60)
def load_data():
    load_dotenv()
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB', 'postgres')
    conn_string = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(conn_string)

    try:
        query = "SELECT * FROM public.credit_card_fraud"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        return False

@task(retries=3, retry_delay_seconds=60)
def pre_process_and_split(data_df):
    data_df['Hour'] = data_df['Time'].apply(lambda x: np.floor(x / 3600))

    target = 'Class'
    predictors = ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',\
        'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19',\
        'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28',\
        'Amount']
    #split dataframe
    train_df, test_df = train_test_split(data_df, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=True )
    train_df, valid_df = train_test_split(train_df, test_size=VALID_SIZE, random_state=RANDOM_STATE, shuffle=True )

    test_data_path = "./data/processed/test_stream.csv"
    test_df.to_csv(test_data_path, index=False)

    return [train_df, test_df, valid_df, target, predictors]

@task(retries=3, retry_delay_seconds=60)
def train(dfs):

    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    print(f"MLflow tracking URI: {mlflow_uri}")
    print(f"MLflow S3 endpoint: {os.getenv('MLFLOW_S3_ENDPOINT_URL')}")
    
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("credit-card-fraud")  # ✅ Fixed typo "fraid" → "fraud"

    train_df, test_df, valid_df, target, predictors = dfs
    num_features = len(predictors)
    
    dtrain = xgb.DMatrix(train_df[predictors], train_df[target].values)
    dvalid = xgb.DMatrix(valid_df[predictors], valid_df[target].values)
    dtest = xgb.DMatrix(test_df[predictors], test_df[target].values)

    watchlist = [(dtrain, 'train'), (dvalid, 'valid')]

    params = {
        'objective': 'binary:logistic',
        'eta': 0.039,
        'silent': True,
        'max_depth': 2,
        'subsample': 0.8,
        'colsample_bytree': 0.9,
        'eval_metric': 'auc',
        'random_state': RANDOM_STATE
    }

    results = {}
    with mlflow.start_run():
        model = xgb.train(
            params, 
            dtrain, 
            MAX_ROUNDS, 
            watchlist, 
            evals_result=results,
            early_stopping_rounds=EARLY_STOP, 
            maximize=True, 
            verbose_eval=VERBOSE_EVAL
        )
    
        # Get final AUC scores
        final_train_auc = results['train']['auc'][-1]
        final_valid_auc = results['valid']['auc'][-1]
        
        # Create markdown artifact
        create_markdown_artifact(
            key="model-performance",
            markdown=f'## Model Training Complete\n- **Train AUC**: {final_train_auc:.4f}\n- **Valid AUC**: {final_valid_auc:.4f}\n',
            description="XGBoost Fraud-Detection Model Metrics"
        )
        
        # Log metrics and params to MLflow
        mlflow.log_metric("train_auc", final_train_auc)
        mlflow.log_metric("valid_auc", final_valid_auc)
        #mlflow.log_params(params)

        # Convert to ONNX
        model.feature_names = None
        initial_types = [('float_input', FloatTensorType([None, num_features]))]
        onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_types)
        
        # Log ONNX model to MLflow
        mlflow.log_params(params)
        mlflow.onnx.log_model(
            onnx_model,
            artifact_path="model"
            # Remove registered_model_name - causing the 404 error
)
    
    return [model, num_features, onnx_model]

@task(retries=3, retry_delay_seconds=60)
def save_model(models):
    os.makedirs('./models', exist_ok=True)
    _, _, onnx_model = models

    with open('./models/model.onnx', 'wb') as f:
        f.write(onnx_model.SerializeToString())
    print('ONNX Model saved locally')
    return

if __name__ == "__main__":
    data_df = load_data()
    dfs = pre_process_and_split(data_df)
    model = train(dfs)
    save_model(model)
    