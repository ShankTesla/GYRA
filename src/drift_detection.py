from evidently import Dataset
from evidently import DataDefinition
from evidently import Report
from evidently.metrics import ValueDrift, DriftedColumnsCount
from train import load_data
from ingest import ingest
import pandas as pd

def detect_drift():
    success = ingest()
    if success:
        train_df = load_data.fn()
        test_df = pd.read_csv('./data/processed/test_stream.csv')
        
        numerical_cols = train_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = train_df.select_dtypes(include=['object', 'category']).columns.tolist()

        definition = DataDefinition(
        numerical_columns=numerical_cols,
        categorical_columns=categorical_cols if categorical_cols else None,
    )


        train_eval_data = Dataset.from_pandas(
        train_df,
        data_definition=definition
        )
        
        test_eval_data = Dataset.from_pandas(
        test_df,
        data_definition=definition
        )


        report = Report([
        DriftedColumnsCount()
        ])

        my_eval = report.run(train_eval_data, test_eval_data)
        # Get results for programmatic use
        #result_json = data_drift_suite.json()
        result_dict = my_eval.dict()
        print(result_dict)
        return
    else:
        print("Error ingesting didnt work")
        return

if __name__ == "__main__":
    detect_drift()

