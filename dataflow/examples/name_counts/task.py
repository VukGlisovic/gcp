"""
In order to run a dataflow using the google cloud service, you
have to specify the following parameters: project, staging_location,
temp_location and runner.
Creating the a whl file from the any package can be done with:
python setup.py bdist_wheel

Example parameters for your script to create a template:
--project=[YOUR-PROJECT]
--region=europe-west1
--runner=DataflowRunner
--setup_file=setup.py
--temp_location=gs://name_counts_example/dataflow/temp
--staging_location=gs://name_counts_example/dataflow/staging
--template_location=gs://name_counts_example/dataflow/templates/name_counts
--max-workers=2
--worker-machine-type=n1-standard-1

Example parameters for instantly running on google cloud:
--project=[YOUR-PROJECT]
--region=europe-west1
--runner=DataflowRunner
--setup_file=setup.py
--input_path=gs://name_counts_example/data/inputs/name_file_*
--output_path=gs://name_counts_example/data/outputs/output_{}.txt
--temp_location=gs://name_counts_example/dataflow/temp
--requirements_file=requirements.txt  # optional
--extra_package=additional_package-0.1-py2-none-any.whl  # optional
--max-workers=2  # optional
--worker-machine-type=n1-standard-1  # optional
--save_main_session  # optional


For local development, this would suffice:
--project=[YOUR-PROJECT]
--runner=DirectRunner
--input_path=gs://name_counts_example/data/inputs/name_file_*
--output_path=gs://name_counts_example/data/outputs/output_{}.txt
"""

import sys
import logging
import argparse
import datetime as dt

import apache_beam as beam
from apache_beam import pvalue
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.transforms.core import Create

from custom_modules.transform_functions import SplitAndFilterNames, GetFirstName, GetLastName


class NameCountOptions(PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument('--input_path',
                            help='String or regular expression pointing towards one or more files.',
                            type=str,
                            default='gs://name_counts_example/data/inputs/name_file_*')
        parser.add_argument('--output_path_template',
                            help='Blob where the outputs will be written to. It should contain two curly brackets that will be replaced.',
                            type=str,
                            default='gs://name_counts_example/data/output_{}.txt')


def run():
    parser = argparse.ArgumentParser()
    _, pipeline_args = parser.parse_known_args()

    # google cloud parameters
    pipeline_options = PipelineOptions(pipeline_args)
    google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
    if not google_cloud_options.project:
        raise ValueError("Project is a required input.")
    logging.info("Using project: %s", google_cloud_options.project)
    if not google_cloud_options.job_name:
        google_cloud_options.job_name = 'name-counts-{}'.format(dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S'))
    logging.info("Dataflow job name: %s", google_cloud_options.job_name)

    # parameters used in the pipeline
    name_count_options = pipeline_options.view_as(NameCountOptions)
    gcs_input_path = name_count_options.input_path
    gcs_output_path_first_names = name_count_options.output_path_template.format('first_names')
    gcs_output_path_last_names = name_count_options.output_path_template.format('last_names')
    logging.info("Using input path: %s", gcs_input_path)
    logging.info("Using output path for first names: %s", gcs_output_path_first_names)
    logging.info("Using output path for last names: %s", gcs_output_path_last_names)

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

    names_filtered = (pipeline_startup
                      | 'Filter Names' >> beam.ParDo(SplitAndFilterNames(), filter_letters=pvalue.AsList(filter_letters))
                      )

    first_names = (names_filtered
                   | 'Get First Names' >> beam.ParDo(GetFirstName())
                   | 'Group By First Name' >> beam.CombinePerKey(max)
                   | 'Store First Name Result' >> beam.io.WriteToText(gcs_output_path_first_names, num_shards=1)
                   )

    last_names = (names_filtered
                  | 'Get Last Names' >> beam.ParDo(GetLastName())
                  | 'Group By Last Name' >> beam.CombinePerKey(min)
                  | 'Store Last Name Result' >> beam.io.WriteToText(gcs_output_path_last_names, num_shards=1)
                  )

    result = p.run()
    # result.wait_until_finish()


if __name__ == '__main__':
    logformat = '%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)s - %(funcName)s] %(message)s'
    log_level = 'INFO'
    logging.basicConfig(format=logformat, level=log_level, stream=sys.stdout)
    run()
