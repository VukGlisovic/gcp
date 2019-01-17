"""
In order to run a dataflow using the google cloud service, you
have to specify the following parameters: project, staging_location,
temp_location and runner.
Creating the a whl file from the any package can be done with:
python setup.py bdist_wheel

Example parameters for your script to run on google cloud:
--project=test-project
--runner=DataflowRunner
--input_path=gs://test_bucket/sub_folder/name_file_*
--output_path=gs://test_bucket/sub_folder/output.txt
--temp_location=gs://test_bucket/dataflow/temp
--staging_location=gs://test_bucket/dataflow/templates/insert_weather_data
--requirements_file=requirements.txt
--extra_package=additional_package-0.1-py2-none-any.whl
--save_main_session


For local development, this would suffice:
--project=test-project
--runner=DirectRunner
--input_path=gs://test_bucket/sub_folder/name_file_*
"""

import sys
import logging
import argparse
import datetime as dt

import apache_beam as beam
from apache_beam import pvalue
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.transforms.core import Create

from transform_functions import SplitAndFilterNames


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path',
                        default='gs://name_counts_example/name_files/inputs/name_file_*',
                        help='String or regular expression pointing towards one or more files.')
    parser.add_argument('--output_path',
                        default='gs://name_counts_example/output.txt',
                        help='Blob where the outputs will be written to.')

    known_args, pipeline_args = parser.parse_known_args()
    # parameters used in the pipeline
    gcs_input_path = known_args.input_path
    gcs_output_path = known_args.output_path
    logging.info("Using input path: %s", gcs_input_path)
    logging.info("Using output path: %s (for writing counts)", gcs_output_path)
    # google cloud parameters
    pipeline_options = PipelineOptions(pipeline_args)
    google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
    if not google_cloud_options.project:
        raise ValueError("Project is a required input.")
    logging.info("Using project: %s", google_cloud_options.project)
    if not google_cloud_options.job_name:
        google_cloud_options.job_name = 'name-counts-{}'.format(dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S'))
    logging.info("Dataflow job name: %s", google_cloud_options.job_name)

    p = beam.Pipeline(options=pipeline_options)

    # Setup pipeline
    pipeline_startup = (p
                        | 'Create File Glob' >> Create([gcs_input_path])
                        | 'Read All Files' >> beam.io.ReadAllFromText()
                        | 'Split Into Names' >> beam.Map(lambda string: string.split(','))
                        )

    filter_letters = (p
                      | 'Letters Side Input' >> Create(['A', 'B', 'C', 'X', 'Y', 'Z'])
                      )

    # Read files from cloud storage part of the pipeline
    read_jsons = (pipeline_startup
                  | 'Filter Names' >> beam.ParDo(SplitAndFilterNames(), filter_letters=pvalue.AsList(filter_letters))
                  )
    #
    # # Transform and ingest part of the pipeline
    # ingest_content = (read_jsons
    #                   | 'Transform Content' >> beam.ParDo(TransformContent(), dict=info_side_input)
    #                   | 'Insert In Bigtable' >> beam.ParDo(InsertInBigtable())
    #                   )
    #
    # # Calculate number of files read per  (sanity check) part of the pipeline
    # counts = (read_jsons | 'Extract ID' >> beam.Map(lambda dct: dct.get(''))
    #           | 'Add Ones' >> beam.Map(lambda ds_id: (ds_id, 1))
    #           | 'Group IDs' >> beam.GroupByKey()
    #           | 'Get Group Size' >> beam.ParDo(CalculateNumberOfFiles())
    #           | 'Write Counts' >> beam.io.WriteToText(gcs_output_path, num_shards=1)
    #           )

    result = p.run()
    # result.wait_until_finish()


if __name__ == '__main__':
    logformat = '%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)s - %(funcName)s] %(message)s'
    log_level = 'INFO'
    logging.basicConfig(format=logformat, level=log_level, stream=sys.stdout)
    run()
