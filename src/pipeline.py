from prefect import flow
from ingest import ingest
from train import load_data, pre_process_and_split, train, save_model

@flow(name="credit card fraud")
def ml_pipeline():
    success = ingest()

    if not success:
        print("Ingestion failed please check")
        return
    
    df = load_data()
    split_data = pre_process_and_split(df)
    model = train(split_data)
    save_model(model)

if __name__ == "__main__":
    ml_pipeline()