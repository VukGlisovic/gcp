from cloud_storage.client import CloudStorage
from google.cloud.exceptions import Conflict
import numpy as np
import argparse
import logging


LETTERS = 'abcdefghijklmnopqrstuvwxyz'
LETTERS = LETTERS.upper() + LETTERS
NR_LETTERS = len(LETTERS)
np.random.seed(1234)
parser = argparse.ArgumentParser()
parser.add_argument('--project_id',
                    help='Name of the project',
                    type=str)
parser.add_argument('--min_count_per_letter',
                    help='Minimum number of records per letter',
                    type=int,
                    default=100)
parser.add_argument('--max_count_per_letter',
                    help='Maximum number of records per letter',
                    type=int,
                    default=1000)
parser.add_argument('--file_count',
                    help='Number of files to create.',
                    type=int,
                    default=3)
parser.add_argument('--bucket_name',
                    help='Where to store the name files',
                    type=str,
                    default='letter_statistics_example')
known_args, _ = parser.parse_known_args()
project_id = known_args.project_id
min_count_per_letter = known_args.min_count_per_letter
max_count_per_letter = known_args.max_count_per_letter
file_count = known_args.file_count
bucket_name = known_args.bucket_name


def create_records_for_letter(letter_index):
    letter = LETTERS[letter_index]
    logging.info("Generating data for letter: %s", letter)
    nr_values = np.random.randint(low=min_count_per_letter, high=max_count_per_letter)
    values = np.random.normal(loc=letter_index, scale=letter_index, size=nr_values)
    return ['{},{}'.format(letter, value) for value in values]


def create_dataset():
    all_letters = []
    for index in range(NR_LETTERS):
        all_letters += create_records_for_letter(index)
    np.random.shuffle(all_letters)
    return all_letters


def store_data(data):
    cs = CloudStorage(project_id)
    try:
        cs.create_bucket(bucket_name, location='EU')
    except Conflict:
        logging.info("Bucket '%s' already exists.", bucket_name)
    chunk_size = int(np.ceil(len(data) / file_count))
    chunks = [data[i*chunk_size: (i+1)*chunk_size] for i in range(file_count)]
    for file_nr, data_chunk in enumerate(chunks):
        gcs_path = 'gs://{}/data/inputs/letter_file_{}.txt'.format(bucket_name, file_nr)
        content = "\n".join(data_chunk)
        cs.upload_blob_from_data(content, gcs_path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data = create_dataset()
    store_data(data)
