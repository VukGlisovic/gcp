"""

"""

from cloud_storage.client import CloudStorage
import pytz
import logging
import pyspark
import argparse
import pandas as pd
import datetime as dt

logging.basicConfig(level=logging.INFO)


logging.info("Initializing spark context.")
sc = pyspark.SparkContext()


_YEAR_1970 = dt.datetime(1970, 1, 1, tzinfo=pytz.UTC)
_YEAR_3000 = dt.datetime(3000, 1, 1, tzinfo=pytz.UTC)
_YEAR_3000_TIMESTAMP = int((_YEAR_3000 - _YEAR_1970).total_seconds())


parser = argparse.ArgumentParser()
parser.add_argument('--project_id',
                    help='Project to use.',
                    type=str)
parser.add_argument('--input_file_glob',
                    help='Channel classifier to aggregate.',
                    type=str,
                    default='gs://letter_statistics_calculations/letter_files/inputs/*')
parser.add_argument('--output_path',
                    help='Where to store the aggregated result',
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
    def wrapper(*args, **kwargs):
        start = dt.datetime.utcnow()
        result = func(*args, **kwargs)
        end = dt.datetime.utcnow()
        logging.info("Function %s took: %s", func.__name__, (end - start))
        return result
    return wrapper


@time_function
def calculate_letter_statistics(file_glob):
    lines = sc.textFile(file_glob)
    # data_read = (sc
    #              .parallelize(flow_ids, numSlices=4)
    #              .flatMap(read_flow_data)
    #              .mapValues(lambda value: (value, value, value, 1))
    #              .reduceByKey(lambda x, y: (x[0]+y[0], max(x[1],y[1]), min(x[2],y[2]), x[3]+y[3]))
    #              )
    result = lines.collect()
    print(result)
    return result


# @time_function
# def result_to_dataframe(data):
#     timestamps, aggregated_usage = zip(*data)
#     dataframe = pd.DataFrame(data=list(aggregated_usage), index=timestamps, columns=['SUM', 'MAX', 'MIN', 'COUNT']).sort_index()
#     dataframe['MEAN'] = dataframe['SUM'] / dataframe['COUNT']
#     logging.info("Total datapoints read: {}.".format(dataframe['COUNT'].sum()))
#     return dataframe


@time_function
def store_result(dataframe, filepath):
    if not filepath.startswith('gs://'):
        logging.info("Storing result locally in: {}".format(filepath))
        dataframe.to_csv(filepath, index=True)
    else:
        logging.info("Storing result in cloud storage in path: {}".format(filepath))
        cs = CloudStorage(project_id)

        content = dataframe.to_csv()
        cs.upload_blob_from_data(content, filepath)


def main():
    result = calculate_letter_statistics(input_file_glob)
    # df = result_to_dataframe(result)
    # store_result(df, output_path)
    logging.info("Stopping spark context.")
    sc.stop()


if __name__ == '__main__':
    main()
