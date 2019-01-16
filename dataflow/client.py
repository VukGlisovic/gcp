from googleapiclient import discovery
import logging


class DataFlow(object):

    def __init__(self, project_id, zone):
        self.project_id = project_id
        self.zone = zone
        self.client = discovery.build('dataflow', 'v1b3')

    def submit_job_from_template(self, template_path, temp_location, job_name, parameters={}):
        """Submits a dataflow batch job with optionally configured parameters.

        Args:
            template_path (str): a full cloud storage path (starting with gs://). This path
                should point to a file that contains the actual code to execute.
            temp_location (str): a full cloud storage path (starting with gs://). This path
                will be used for staging any temporary files.
            job_name (str):
            parameters (dict):

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

        request = self.client.projects().templates().launch(projectId=self.project_id,
                                                            gcsPath=template_path,
                                                            body=body)
        response = request.execute()
        return response
