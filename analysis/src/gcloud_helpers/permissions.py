import os

from google.cloud import storage


def _make_blob_public(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.make_public()


def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        print("APPLICATION_CREDENTIALS not defined. Not making blob public.")
        return

    if not blob_name.startswith("/"):
        print("Blob name must be an absolute path")
        return

    try:
        blob = _make_blob_public(bucket_name, blob_name)
        print("Blob {} is publicly accessible at {}".format(blob.name, blob.public_url))
    except:
        print("Error making {} public".format(blob_name))
