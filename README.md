# Gyra - Real-Time Credit Card Fraud Detection System

A production-grade MLOps pipeline for detecting fraudulent credit card transactions in real-time using machine learning and streaming architecture.

## Overview

Gyra is an end-to-end fraud detection system that processes credit card transactions through a streaming pipeline, makes real-time predictions using optimized machine learning models, and monitors for data drift. The system is designed to handle high-throughput transaction processing with low-latency inference.

## Architecture

The system consists of the following components:

- **Data Ingestion**: Kafka-based streaming pipeline for transaction processing
- **Model Training**: Automated training workflow using Prefect and MLflow
- **Model Serving**: FastAPI service with ONNX Runtime for optimized inference
- **Data Storage**: PostgreSQL for transaction persistence, Redis for metrics caching
- **Monitoring**: Evidently for drift detection and data quality monitoring
- **Artifact Storage**: AWS S3 for model versioning and experiment tracking

## Key Features

- Real-time transaction processing with Kafka streaming
- XGBoost-based fraud detection model achieving 0.97+ AUC
- ONNX Runtime optimization for sub-50ms inference latency
- Automated ML workflow orchestration with Prefect
- Comprehensive experiment tracking with MLflow
- Data drift detection and monitoring with Evidently
- Containerized microservices architecture with Docker Compose
- Load testing framework for performance validation

## Technology Stack

**Machine Learning**
- XGBoost for classification
- ONNX Runtime for optimized inference
- MLflow for experiment tracking
- Evidently for drift detection

**Data Processing**
- Apache Kafka for streaming
- PostgreSQL for data persistence
- Redis for caching and metrics

**Orchestration & Deployment**
- Prefect for workflow orchestration
- FastAPI for model serving
- Docker & Docker Compose for containerization
- AWS S3 for artifact storage

**Testing & Monitoring**
- Locust for load testing
- Great Expectations for data validation

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- AWS account with S3 access
- Minimum 8GB RAM recommended

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/gyra.git
cd gyra
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables

Create a `.env` file in the project root:
```bash
# PostgreSQL
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fraud_detection

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=ap-south-1

# Redis
REDIS_PASSWORD=redis

# Kafka
KAFKA_BROKER=kafka:29092
```

5. Start the infrastructure
```bash
docker-compose up -d
```

## Usage

### Training the Model

Run the training pipeline:
```bash
python src/pipeline.py
```

This will:
- Load and preprocess transaction data
- Train the XGBoost model
- Log experiments to MLflow
- Store model artifacts in AWS S3
- Export optimized ONNX model

### Starting the Prediction Service

The FastAPI service starts automatically with Docker Compose. Access the API at:
```
http://localhost:8000/docs
```

### Monitoring

Access monitoring dashboards:
- MLflow UI: http://localhost:5000
- Prefect UI: http://localhost:4200

### Load Testing

Run performance tests:
```bash
locust -f tests/load_test.py
```

Access Locust UI at http://localhost:8089

## Project Structure

```
gyra/
├── src/
│   ├── producer.py          # Kafka transaction producer
│   ├── consumer.py           # Kafka consumer for predictions
│   ├── pipeline.py           # ML training pipeline
│   ├── drift_detection.py    # Data drift monitoring
│   └── app.py                # FastAPI prediction service
├── models/
│   └── fraud_model.onnx      # Optimized ONNX model
├── data/
│   └── creditcard.csv        # Transaction dataset
├── tests/
│   └── load_test.py          # Locust load testing
├── docker-compose.yml        # Service orchestration
├── Dockerfile                # Container image
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md
```

## Performance Metrics

- Model AUC: 0.97+
- Inference Latency: <50ms (p99)
- Throughput: 100+ transactions per second
- Container Size Reduction: 40% (via ONNX optimization)

## Data Pipeline

1. **Ingestion**: Transactions are published to Kafka topics
2. **Processing**: Consumer service retrieves transactions and preprocesses features
3. **Prediction**: ONNX model performs inference via FastAPI endpoint
4. **Storage**: Results stored in PostgreSQL, metrics cached in Redis
5. **Monitoring**: Evidently tracks data drift and model performance

## Model Training Workflow

1. Data validation with Great Expectations
2. Feature engineering and preprocessing
3. Model training with XGBoost
4. Hyperparameter logging to MLflow
5. Model conversion to ONNX format
6. Artifact upload to AWS S3
7. Deployment to prediction service

## Monitoring and Observability

The system includes comprehensive monitoring:

- **Data Drift Detection**: Evidently monitors feature distributions
- **Model Performance**: MLflow tracks accuracy, precision, recall, AUC
- **System Metrics**: Redis stores prediction latencies and throughput
- **Experiment Tracking**: MLflow logs all training runs and parameters

## Configuration

Key configuration options in `.env`:

- `KAFKA_BROKER`: Kafka broker address
- `POSTGRES_*`: Database connection parameters
- `AWS_*`: S3 credentials and region
- `MLFLOW_TRACKING_URI`: MLflow server endpoint
- `REDIS_PASSWORD`: Redis authentication

## Testing

Run unit tests:
```bash
pytest tests/
```

Run load tests:
```bash
locust -f tests/load_test.py --headless -u 100 -r 10 -t 60s
```

## Deployment Considerations

For production deployment:

1. Use managed Kafka (AWS MSK, Confluent Cloud)
2. Deploy PostgreSQL with RDS or managed database
3. Use container orchestration (Kubernetes, ECS)
4. Implement API gateway and rate limiting
5. Set up alerting and logging infrastructure
6. Enable SSL/TLS for all communications

## Troubleshooting

**Issue**: Services fail to start
```bash
docker-compose down -v
docker-compose up -d
```

**Issue**: MLflow can't connect to S3
- Verify AWS credentials in `.env`
- Check S3 bucket exists and is accessible
- Ensure IAM user has S3 permissions

**Issue**: Kafka connection errors
- Wait 30-60 seconds for Kafka to initialize
- Check Zookeeper is running: `docker-compose ps zookeeper`

## Future Enhancements

- Implement A/B testing framework
- Add model explainability with SHAP
- Integrate with alerting systems (PagerDuty, Slack)
- Add multi-model ensemble predictions
- Implement automated model retraining triggers
- Add GraphQL API for advanced querying

## License

MIT License

## Contact

For questions or issues, please open an issue on GitHub.

## Acknowledgments

- Dataset: Credit Card Fraud Detection Dataset (Kaggle)
- Notebook: Credit Card Fraud Detection Notebook (Kaggle)
- Inspired by production MLOps best practices