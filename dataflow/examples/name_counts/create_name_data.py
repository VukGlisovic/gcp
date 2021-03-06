from cloud_storage.client import CloudStorage
from google.cloud.exceptions import Conflict
import sys
import numpy as np
import argparse
import names
import logging


np.random.seed(1234)
parser = argparse.ArgumentParser()
parser.add_argument('--project_id',
                    help='Name of the project',
                    type=str)
parser.add_argument('--name_count',
                    help='Number of names to create per file.',
                    type=int,
                    default=100)
parser.add_argument('--file_count',
                    help='Number of files to create.',
                    type=int,
                    default=5)
parser.add_argument('--bucket_name',
                    help='Where to store the name files',
                    type=str,
                    default='name_counts_example_for_testing')
known_args, _ = parser.parse_known_args()
project_id = known_args.project_id
name_count = known_args.name_count
file_count = known_args.file_count
bucket_name = known_args.bucket_name


def create_content():
    """Creates a large string with full names with ages separated
    by colons.

    Returns:
        str
    """
    logging.info("Creating random data.")
    ages = np.random.randint(1, 10000, size=name_count)
    data = ["{}:{}".format(names.get_full_name(), age) for age in ages]
    data = ",".join(data)
    return data


def upload_data():
    """Uploads multiple files to cloud storage.

    Returns:
        None
    """
    cs = CloudStorage(project_id)
    try:
        location = 'EU'
        cs.create_bucket(bucket_name, location)
    except Conflict:
        logging.info("Bucket '%s' has already been created.", bucket_name)
    for i in range(file_count):
        data = create_content()
        gcs_path = 'gs://{}/data/inputs/name_file_{}.txt'.format(bucket_name, i)
        logging.info("Uploading file to: %s", gcs_path)
        cs.upload_blob_from_data(data, gcs_path)


if __name__ == '__main__':
    logformat = '%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)s - %(funcName)s] %(message)s'
    log_level = 'INFO'
    logging.basicConfig(format=logformat, level=log_level, stream=sys.stdout)
    upload_data()
