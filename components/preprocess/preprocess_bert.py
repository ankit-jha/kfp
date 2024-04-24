from typing import NamedTuple

from kfp.v2.dsl import component


# Preprocess Component
@component(packages_to_install=["google-cloud-storage", "pandas", "fsspec", "gcsfs"])
def preprocess(
    gcp_bucket_name: str, gcp_dataset_name: str, pre_processed_data_uri: str
) -> NamedTuple(
    "Outputs",
    [
        ("upload_bucket_name", str),  # Return parameters
        ("upload_dataset_name", str),
    ],
):
    import logging

    logging.info(f"gcp_bucket_name: {gcp_bucket_name}; gcp_dataset_name: {gcp_dataset_name}")

    import pandas as pd
    from google.cloud import storage

    # Preprocessing
    gcs_uri = f"gs://{gcp_bucket_name}/{gcp_dataset_name}"
    negative_df = pd.read_csv(gcs_uri)[["text", "negative"]]
    negative_df = negative_df.rename(columns={"negative": "labels"})
    negative_df["labels"] = negative_df.labels.astype(int)
    negative_df = negative_df[negative_df.text.map(len) >= 12]

    # Saving processed data in staging area
    client = storage.Client()
    logging.info("Client created using default project: {}".format(client.project))
    staging_bucket_name = pre_processed_data_uri.split("/")[2]
    preprocessed_dataset = "/".join(pre_processed_data_uri.split("/")[3:])
    bucket = client.get_bucket(staging_bucket_name)
    logging.info("Bucket name: {}".format(bucket.name))
    bucket.blob(preprocessed_dataset).upload_from_string(negative_df.to_csv(), "text/csv")
    logging.info("Processed data file uploaded to {}.".format(bucket.name))
    return (bucket.name, preprocessed_dataset)
