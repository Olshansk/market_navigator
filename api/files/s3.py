import logging
import boto3
from botocore.exceptions import ClientError

BUCKET = "cdn.olshansky.info" # https://s3.console.aws.amazon.com/s3/buckets/cdn.olshansky.info?region=us-west-2&tab=objects


def upload_file(file_name, bucket=BUCKET, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True
