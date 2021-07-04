import datetime
import logging

import boto3
from typing import Optional
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError

BUCKET = "cdn.olshansky.info"  # https://s3.console.aws.amazon.com/s3/buckets/cdn.olshansky.info?region=us-west-2&tab=objects
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"

credentials = {
    "aws_access_key_id": "AKIAQE3OIS3UUOIHOFHR",
    "aws_secret_access_key": "0xSv/VFXPYQpxAhyM2r4YM7M8nO56ItUzoNGkaT9aws_secret_access_key",
}

s3_client = boto3.client("s3", "us-west-2", **credentials)
s3_client = boto3.client("s3")
transfer = S3Transfer(s3_client)


def file_last_modified_timestamp(key):
    """Returns last modified date if exists or None otherwise."""
    try:
        res = s3_client.head_object(Bucket=BUCKET, Key=key)
        logging.debug(res)
        date = datetime.datetime.strptime(
            res["ResponseMetadata"]["HTTPHeaders"]["last-modified"], DATE_FORMAT
        )
        return date
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logging.debug(f"The object does not exist. {key}")
        else:
            logging.error(f"Errored while checking if the object exists. {key}", e)
    return None


def get_url(key, bucket=BUCKET):
    return "%s/%s/%s" % (s3_client.meta.endpoint_url, bucket, key)


def upload_file(file_name, bucket=BUCKET, key=None) -> Optional[str]:
    if key is None:
        key = file_name
    try:
        response = s3_client.upload_file(file_name, bucket, key)
        logging.debug(response)
        return get_url(key)
    except ClientError as e:
        logging.error(e)
        return None

def download_file(key: str, filename: str, bucket: str = BUCKET) -> None:
    s3_client.download_file(bucket, key, filename)