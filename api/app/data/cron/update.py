import fire
import app.files.s3 as s3

from app.data.writer import append_to_daily_data_hdf
from app.data.processor import compute_new_data
from app.files.s3 import download_file, upload_file

def download_and_update_hdf_store():
    key = 'daily_data.h5'
    filename = f'/tmp/{key}'
    download_file(key, filename, bucket=s3.BUCKET_PRIVATE)
    append_to_daily_data_hdf(filename)
    upload_file(filename, bucket=s3.BUCKET_PRIVATE, key='daily_data.h5')


if __name__ == '__main__':
    fire.Fire({
        'update_store': download_and_update_hdf_store
    })