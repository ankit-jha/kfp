import os
from datetime import datetime

# GCP PARAMETERS
BASE_IMAGE = 'python:3.8'
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_URI = f"gs://{BUCKET_NAME}"
SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT")

# API service endpoint
API_ENDPOINT = f"{REGION}-aiplatform.googleapis.com"

# Model parameters
MODEL_NAME = "finetuned-bert-classifier"
VERSION = datetime.now().strftime("%Y%m%d%H%M%S")
MODEL_DISPLAY_NAME = f"{MODEL_NAME}-{VERSION}"

PIPELINE_NAME = f"pipeline-{MODEL_NAME}"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root/{MODEL_NAME}"

# BERT PARAMETERS
BERT_TRAINING_DATA_BUCKET = os.getenv("BERT_TRAINING_DATA_BUCKET")
BERT_TRAINING_DATA = os.getenv("BERT_TRAINING_DATA")
BERT_PIPELINE_NAME = "bert-pipeline"
BERT_PIPELINE_DESCRIPTION = "BERT pipeline"
BERT_PROCESSED_DATA = "processed_data.csv"
IMAGE_URI = "us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-7:latest"
TRAIN_IMAGE_URI = f"gcr.io/{PROJECT_ID}/pytorch_gpu_train_{MODEL_NAME}"
JOB_PREFIX = "finetuned-bert-classifier-pytorch"

# WORKER POOL SPECS
# https://cloud.google.com/vertex-ai/docs/training/configure-compute#gpu-compatibility-table
MACHINE_TYPE = "n1-standard-4"
REPLICA_COUNT = "1"
ACCELERATOR_TYPE = "NVIDIA_TESLA_T4"
ACCELERATOR_COUNT = "1"

# SERVING PARAMETERS
# https://cloud.google.com/compute/docs/machine-types#recommendations_for_machine_types
SERVING_IMAGE_URI = f"gcr.io/{PROJECT_ID}/pytorch_cpu_predict_{MODEL_NAME}"
SERVING_HEALTH_ROUTE = "/ping"
SERVING_PREDICT_ROUTE = f"/predictions/{MODEL_NAME}"
SERVING_CONTAINER_PORT = [{"containerPort": 7080}]
SERVING_MACHINE_TYPE = "n1-standard-2"
SERVING_MIN_REPLICA_COUNT = 1
SERVING_MAX_REPLICA_COUNT = 1
SERVING_TRAFFIC_SPLIT = '{"0": 100}'
