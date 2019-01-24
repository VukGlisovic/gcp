"""
Note that apache-beam doesn't have full support for python 3 yet.
Therefore it could be a good idea to use python 2.7 for google
dataflow, since you can then use the latest apache-beam version.
"""
from googleapiclient import discovery
import logging


class DataFlow(object):

    def __init__(self, project_id, region, zone_letter):
        self.project_id = project_id
        self.region = region
        self.zone = region + '-' + zone_letter
        self.client = discovery.build('dataflow', 'v1b3')

    def submit_job_from_template(self, template_path, temp_location, job_name, parameters={}, max_workers=None, machine_type=None):
        """Submits a dataflow batch job with optionally configured parameters.

        Args:
            template_path (str): a full cloud storage path (starting with gs://). This path
                should point to a file that contains the actual code to execute.
            temp_location (str): a full cloud storage path (starting with gs://). This path
                will be used for staging any temporary files.
            job_name (str):
            parameters (dict): regular key value pairs. No need to prefix with double hyphen.

        Returns:
            dict
        """
        logging.info("Starting dataflow batch job with name: %s", job_name)
        body = {
            "jobName": job_name,
            "parameters": parameters,
            "environment": {
                "tempLocation": temp_location,
                "zone": self.zone
            }
        }
        if max_workers:
            body['environment']['maxWorkers'] = max_workers
        if machine_type:
            body['environment']['machineType'] = machine_type

        request = self.client.projects().locations().templates().launch(projectId=self.project_id,
                                                                        location=self.region,
                                                                        gcsPath=template_path,
                                                                        body=body)
        response = request.execute()
        return response
