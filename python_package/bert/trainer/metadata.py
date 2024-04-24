#!/usr/bin/env python
# Task type can be either 'classification', 'regression', or 'custom'.
# This is based on the target feature in the dataset.
TASK_TYPE = "classification"

# Dataset name
DATASET_NAME = "processed_data.csv"

# pre-trained model name
PRETRAINED_MODEL_NAME = "bert-base-uncased"

# List of the class values (labels) in a classification dataset.
TARGET_LABELS = {1: 1, 0: 0}

# maximum sequence length
MAX_SEQ_LENGTH = 128
