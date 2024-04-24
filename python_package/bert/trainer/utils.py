import os

import pandas as pd
from datasets import Dataset
from google.cloud import storage
from sklearn.model_selection import train_test_split
from trainer import metadata
from transformers import AutoTokenizer


def preprocess_function(examples):
    """Unused function"""
    tokenizer = AutoTokenizer.from_pretrained(
        metadata.PRETRAINED_MODEL_NAME,
        use_fast=True,
    )

    # Tokenize the texts
    tokenizer_args = (examples["text"],)
    result = tokenizer(
        *tokenizer_args,
        padding="max_length",
        max_length=metadata.MAX_SEQ_LENGTH,
        truncation=True,
    )

    # TEMP: We can extract this automatically but Unique method of the dataset
    # is not reporting the labels -1 which shows up in the pre-processing
    # Hence the additional -1 term in the dictionary
    label_to_id = metadata.TARGET_LABELS

    # Map labels to IDs (not necessary for GLUE tasks)
    if label_to_id is not None and "labels" in examples:
        result["labels"] = [label_to_id[l] for l in examples["labels"]]

    return result


def load_data(args):
    """Loads the data into two different data loaders. (Train, Test)

    Args:
        args: arguments passed to the python script
    """
    gcp_bucket_name = args.gcs_uri.split("/")[2]
    gcp_dataset_name = "/".join(args.gcs_uri.split("/")[3:])

    client = storage.Client()
    bucket = client.get_bucket(gcp_bucket_name)
    blob = bucket.get_blob(gcp_dataset_name)
    blob.download_to_filename(gcp_dataset_name)
    negative_df = pd.read_csv(gcp_dataset_name)

    # TODO Read directly from gcs_uri
    # negative_df = pd.read_csv(args.gcs_uri)

    sentiment_dataset_train, sentiment_dataset_test = train_test_split(
        negative_df[["text", "labels"]], test_size=0.0125
    )

    # sub sample sentiment TRAINING set, level test set at the same ratio
    sentiment_dataset_train = sentiment_dataset_train[sentiment_dataset_train.labels == 1].append(
        sentiment_dataset_train[sentiment_dataset_train.labels == 0].sample(
            sentiment_dataset_train.labels.sum() * 9
        )
    )

    sentiment_dataset_train = Dataset.from_pandas(sentiment_dataset_train[["labels", "text"]])
    sentiment_dataset_test = Dataset.from_pandas(sentiment_dataset_test[["labels", "text"]])

    train_dataset, test_dataset = sentiment_dataset_train, sentiment_dataset_test

    return train_dataset, test_dataset


def save_model(args):
    """Saves the model to Google Cloud Storage or local file system

    Args:
      args: contains name for saved model.
    """
    scheme = "gs://"
    if args.job_dir.startswith(scheme):
        job_dir = args.job_dir.split("/")
        bucket_name = job_dir[2]
        object_prefix = "/".join(job_dir[3:]).rstrip("/")

        if object_prefix:
            model_path = "{}/{}".format(object_prefix, args.model_name)
        else:
            model_path = "{}".format(args.model_name)

        bucket = storage.Client().bucket(bucket_name)
        local_path = os.path.join("/tmp", args.model_name)
        files = [f for f in os.listdir(local_path) if os.path.isfile(os.path.join(local_path, f))]
        for file in files:
            local_file = os.path.join(local_path, file)
            blob = bucket.blob("/".join([model_path, file]))
            blob.upload_from_filename(local_file)
        print(f"Saved model files in gs://{bucket_name}/{model_path}")
    else:
        print(f"Saved model files at {os.path.join('/tmp', args.model_name)}")
        print(f"To save model files in GCS bucket, please specify job_dir starting with gs://")
