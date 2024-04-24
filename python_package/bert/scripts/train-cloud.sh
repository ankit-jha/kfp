#!/bin/bash
# This script performs cloud training for a PyTorch model.

echo "Submitting Custom Job to Vertex AI to train PyTorch model"

# MODEL PARAMETERS
MODEL_NAME="finetuned-bert-classifier"
GCS_TRAINING_DATA_URI="[your-training-data-gs-uri]"

# WORKER POOL SPECS
# https://cloud.google.com/vertex-ai/docs/training/configure-compute#gpu-compatibility-table
MACHINE_TYPE="n1-standard-4"
REPLICA_COUNT="1"
ACCELERATOR_TYPE="NVIDIA_TESLA_T4"
ACCELERATOR_COUNT="1"

# GCP PARAMETERS: the name of the bucket used for staging and storing results
BUCKET_NAME="[your-bucket-name]" # <-- CHANGE TO YOUR BUCKET NAME

# The PyTorch image provided by Vertex AI Training.
IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-7:latest"

# JOB_NAME: the name of your job running on Vertex AI.
JOB_PREFIX="finetuned-bert-classifier-pytorch-py-pkg"
JOB_NAME=${JOB_PREFIX}-$(date +%Y%m%d%H%M%S)-custom-job

# REGION: select a region from https://cloud.google.com/vertex-ai/docs/general/locations#available_regions
# or use the default '`us-central1`'. The region is where the job will be run.
REGION="us-central1"

# JOB_DIR: Where to store prepared package and upload output model.
JOB_DIR=gs://${BUCKET_NAME}/${JOB_PREFIX}/model/${JOB_NAME}

# worker pool spec
worker_pool_spec="\
replica-count=${REPLICA_COUNT},\
machine-type=${MACHINE_TYPE},\
accelerator-type=${ACCELERATOR_TYPE},\
accelerator-count=${ACCELERATOR_COUNT},\
executor-image-uri=${IMAGE_URI},\
python-module=trainer.task,\
local-package-path=../bert/"

# Submit Custom Job to Vertex AI
gcloud beta ai custom-jobs create \
    --display-name=${JOB_NAME} \
    --region ${REGION} \
    --worker-pool-spec="${worker_pool_spec}" \
    --args="--model-name",${MODEL_NAME},"--job-dir",${JOB_DIR},"--gcs-uri",${GCS_TRAINING_DATA_URI}

echo "After the job is completed successfully, model files will be saved at $JOB_DIR/"

# uncomment following lines to monitor the job progress by streaming logs

# Stream the logs from the job
# gcloud ai custom-jobs stream-logs $(gcloud ai custom-jobs list --region=$REGION --filter="displayName:"$JOB_NAME --format="get(name)")

# # Verify the model was exported
# echo "Verify the model was exported:"
# gsutil ls ${JOB_DIR}/
