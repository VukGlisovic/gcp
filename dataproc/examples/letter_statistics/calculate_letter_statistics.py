import logging
import pyspark
import argparse
import pandas as pd
import datetime as dt
from google.cloud import storage


logging.info("Initializing spark context.")
sc = pyspark.SparkContext()


parser = argparse.ArgumentParser()
parser.add_argument('--project_id',
                    help='Project to use.',
                    type=str)
parser.add_argument('--input_file_glob',
                    help='A local or google storage file glob specifying what files should be read.',
                    type=str,
                    default='gs://letter_statistics_calculations/letter_files/inputs/*')
parser.add_argument('--output_path',
                    help='Where to store the statistics.',
                    type=str,
                    default='/aggregate_result.csv')
known_args, _ = parser.parse_known_args()
project_id = known_args.project_id
input_file_glob = known_args.input_file_glob
output_path = known_args.output_path
logging.info("Project: {}".format(project_id))
logging.info("Input file glob: {}".format(input_file_glob))
logging.info("Output path: {}".format(output_path))


def time_function(func):
    """ Simple wrapper that times the duration of a function.

    Args:
        func (Callable):

    Returns:
        Callable
    """
    def wrapper(*args, **kwargs):
        start = dt.datetime.utcnow()
        result = func(*args, **kwargs)
        end = dt.datetime.utcnow()
        logging.info("Function %s took: %s", func.__name__, (end - start))
        return result
    return wrapper


@time_function
def calculate_letter_statistics(file_glob):
    """Reads data from cloud storage and calculates the sum, sum of
    squares, max, min and count.
    Note that dataproc clusters automatically have a google storage
    connector. This means file_glob can be a path starting with gs
    and dataproc will understand it should look at cloud storage. For
    local development, you either have to install the cloud storage
    connector, or simply have some data in a local directory.

    Args:
        file_glob (str):

    Returns:
        list
    """
    lines = sc.textFile(file_glob, minPartitions=8)
    statistics = (lines.map(lambda record: record.split(','))
                  .mapValues(lambda x: float(x))
                  .mapValues(lambda value: (value, value**2, value, value, 1))
                  .reduceByKey(lambda x, y: (x[0]+y[0], x[1]+y[1], max(x[2],y[2]), min(x[3],y[3]), x[4]+y[4]))
                  )
    result = statistics.collect()
    return result


@time_function
def result_to_dataframe(data):
    """Converts data to a pandas dataframe.

    Args:
        data (list):

    Returns:
        pd.DataFrame
    """
    letters, statistics = zip(*data)
    dataframe = pd.DataFrame(data=list(statistics), index=letters, columns=['SUM', 'SUM_OF_SQUARES', 'MAX', 'MIN', 'COUNT']).sort_index()
    dataframe['MEAN'] = dataframe['SUM'] / dataframe['COUNT']
    dataframe['VARIANCE'] = dataframe['SUM_OF_SQUARES'] / dataframe['COUNT'] - dataframe['MEAN']**2
    dataframe['STANDARD_DEVIATION'] = dataframe['VARIANCE']**0.5
    logging.info("Total datapoints read: {}.".format(dataframe['COUNT'].sum()))
    return dataframe


@time_function
def store_result(dataframe, filepath):
    """Stores the dataframe. Either in a local path, or on cloud
    storage.

    Args:
        dataframe (pd.DataFrame):
        filepath (str):

    Returns:
        None
    """
    if not filepath.startswith('gs://'):
        logging.info("Storing result locally in: {}".format(filepath))
        dataframe.to_csv(filepath, index=True)
    else:
        logging.info("Storing result in cloud storage in path: {}".format(filepath))
        # Content to write
        content = dataframe.to_csv(index=True)
        # Client to write with
        cs = storage.Client(project_id)
        bucket_name, blob_path = filepath[5:].split('/', 1)
        bucket = cs.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_string(content)


def main():
    result = calculate_letter_statistics(input_file_glob)
    df = result_to_dataframe(result)
    store_result(df, output_path)
    logging.info("Finished job.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
