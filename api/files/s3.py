import logging
import boto3
from botocore.exceptions import ClientError
import datetime

BUCKET = "cdn.olshansky.info" # https://s3.console.aws.amazon.com/s3/buckets/cdn.olshansky.info?region=us-west-2&tab=objects
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

s3_client = boto3.client('s3')



# Returns last modified date if exists or None otherwise
def file_exists(key):
    try:
        res = s3_client.head_object(Bucket=BUCKET, Key=key)
        logging.debug(res)
        date = datetime.datetime.strptime(res['ResponseMetadata']['HTTPHeaders']['last-modified'], DATE_FORMAT)
        return date
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            logging.debug(f'The object does not exist. {key}')
        else:
            logging.error(f'Errored while checking if th eobject exists. {key}')
    return None

def upload_file(file_name, bucket=BUCKET, key=None):
    if key is None:
        key = file_name
    try:
        response = s3_client.upload_file(file_name, bucket, key)
        logging.debug(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True
