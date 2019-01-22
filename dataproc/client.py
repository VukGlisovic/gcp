from googleapiclient import discovery
import time
import logging


class DataProc(object):

    def __init__(self, project_id, region, zone_letter):
        self.project_id = project_id
        self.region = region
        self.zone = region + '-' + zone_letter
        self.client = discovery.build('dataproc', 'v1')

    def create_cluster(self, cluster_name, master_machine_type='n1-standard-1', nr_masters=1, master_boot_disk_gb=200, worker_machine_type='n1-standard-1', nr_workers=2, worker_boot_disk_gb=100, metadata={}, initialization_file=None):
        """Create a dataproc cluster. You can create the cluster with one initialization
        file only. The number of local SSDs are fixed to zero.

        Args:
            cluster_name (str):
            master_machine_type (str):
            nr_masters (int):
            master_boot_disk_gb (int):
            worker_machine_type (str):
            nr_workers (int):
            worker_boot_disk_gb (int):
            metadata (dict):
            initialization_file (str):

        Returns:
            dict
        """
        logging.info("Creating cluster with name '%s'...", cluster_name)
        zone_uri = 'https://www.googleapis.com/compute/v1/projects/{}/zones/{}'.format(self.project_id, self.zone)

        cluster_configuration = {
            'projectId': self.project_id,
            'clusterName': cluster_name,
            'config': {
                'gceClusterConfig': {
                    'zoneUri': zone_uri,
                    'metadata': metadata
                },
                'masterConfig': {
                    'numInstances': nr_masters,
                    'machineTypeUri': master_machine_type,
                    'diskConfig': {
                        'bootDiskSizeGb': master_boot_disk_gb,
                        'numLocalSsds': 0
                    }
                },
                'workerConfig': {
                    'numInstances': nr_workers,
                    'machineTypeUri': worker_machine_type,
                    'diskConfig': {
                        'bootDiskSizeGb': worker_boot_disk_gb,
                        'numLocalSsds': 0
                    }
                },
                'initializationActions': []
            }
        }

        if initialization_file:
            cluster_configuration['config']['initializationActions'].append({'executableFile': initialization_file})

        result = self.client.projects().regions().clusters().create(
            projectId=self.project_id,
            region=self.region,
            body=cluster_configuration).execute()
        return result

    def delete_cluster(self, cluster_name):
        """Deletes a cluster.

        Args:
            cluster_name (str):

        Returns:
            dict
        """
        logging.info("Tearing down cluster '%s'.", cluster_name)
        result = self.client.projects().regions().clusters().delete(
            projectId=self.project_id,
            region=self.region,
            clusterName=cluster_name).execute()
        return result

    def submit_pyspark_job(self, cluster_name, main_python_file, script_parameters=[]):
        """Submits a pyspark job to your dataproc cluster. Specify the main script
        with main_python_file. You can add script parameters with the script_parameters
        parameter.

        Args:
            cluster_name (str):
            main_python_file (str):
            script_parameters (list[str]):

        Returns:
            str
        """
        job_details = {
            'projectId': self.project_id,
            'job': {
                'placement': {
                    'clusterName': cluster_name
                },
                'pysparkJob': {
                    'mainPythonFileUri': main_python_file,
                    'args': script_parameters
                }
            }
        }
        result = self.client.projects().regions().jobs().submit(
            projectId=self.project_id,
            region=self.region,
            body=job_details).execute()
        job_id = result['reference']['jobId']
        logging.info('Submitted job with ID: {}'.format(job_id))
        return job_id

    def wait_for_job(self, job_id, request_interval=0):
        """Waits for a job to finish and returns the output of the job metadata. Afterwards,
        you could download the job output from cloud storage with 'driverOutputResourceUri'.

        Args:
            job_id (str):
            request_interval (float):

        Returns:
            dict
        """
        logging.info('Waiting for job (%s) to finish...', job_id)
        while True:
            try:
                result = self.client.projects().regions().jobs().get(
                    projectId=self.project_id,
                    region=self.region,
                    jobId=job_id).execute()
                # Handle exceptions
                if result['status']['state'] == 'ERROR':
                    raise Exception(result['status']['details'])
                elif result['status']['state'] == 'DONE':
                    logging.info('Job finished.')
                    return result
                # wait for some time till the next request
                time.sleep(request_interval)
            except KeyboardInterrupt:
                logging.info('Stopping polling.')
                return


class DataProcClientManager(object):
    """Class for finding already existing DataProc instances. This makes
    sure there is no need to recreate an already existing object. This
    saves time.
    """

    _dataprocclientmanager__instance = None

    def __new__(cls, *args, **kwargs):
        if not DataProcClientManager._dataprocclientmanager__instance:
            logging.info("Creating new DataProcClientManager instance.")
            DataProcClientManager._dataprocclientmanager__instance = object.__new__(cls)
        return DataProcClientManager._dataprocclientmanager__instance

    def get_client(self, project_id, region, zone_letter):
        dataproc_client_instance_name = '__dataproc_client_' + project_id + '_' + region + '_' + zone_letter
        dataproc_client = getattr(self, dataproc_client_instance_name, None)
        if not dataproc_client:
            dataproc_client = DataProc(project_id, region, zone_letter)
            # Make sure DataProcClientManager remembers this object
            setattr(self, dataproc_client_instance_name, dataproc_client)
        return dataproc_client
