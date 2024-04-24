from typing import NamedTuple

from kfp.v2.dsl import component


@component(packages_to_install=["google-cloud-storage"])
def get_data_location(
    bucket_name: str, blob_name: str
) -> NamedTuple(
    "Outputs",
    [
        ("gcp_bucket_name", str),  # Return parameters
        ("gcp_dataset_name", str),
    ],
):
    # the import is not actually used for this simple example, but the import
    # is successful, as it was included in the `packages_to_install` list.
    import logging

    from google.cloud import storage  # noqa: F401

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    logging.info("Bucket name: {}".format(bucket.name))
    logging.info("Bucket location: {}".format(bucket.location))
    logging.info("Bucket storage class: {}".format(bucket.storage_class))
    blobs = bucket.list_blobs()
    logging.info("Blobs in {}:".format(bucket.name))
    for item in blobs:
        logging.info("\t" + item.name)

    # Source Data
    blob = bucket.get_blob(blob_name)
    logging.info("Name: {}".format(blob.id))
    logging.info("Size: {} bytes".format(blob.size))
    logging.info("Content type: {}".format(blob.content_type))
    logging.info("Public URL: {}".format(blob.public_url))
    blob.download_to_filename(blob.name)

    # Moving Source Data To Staging Area For Processing
    staging_bucket_name = bucket_name
    staging_bucket = client.get_bucket(staging_bucket_name)
    staging_bucket.blob(blob.name).upload_from_filename(blob.name)

    return (staging_bucket.name, blob.name)
