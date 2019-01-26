from googleapiclient import discovery, errors
import logging

logging.basicConfig(level=logging.INFO)


class CloudML(object):

    def __init__(self, project_id):
        self.client = discovery.build('ml', 'v1')
        self.project_id = project_id

    def create_model(self, model_name, description, regions):
        """Method for creating a new model. Note that this only creates
        a model 'template'; it does not create the actual model. To make
        an actual model for serving, you need to create a version for
        this model.

        Args:
            model_name (str):
            description (str):
            regions (list[str]): contains the regions where the model will
                be served. Currently only one region per model is supported.

        Returns:
            dict: response from executing create request
        """
        # Store your full project ID in a variable in the format the API needs.
        project_path = 'projects/{}'.format(self.project_id)

        # Create a dictionary with the fields from the request body.
        request_body = {'name': model_name,
                        'description': description,
                        'regions': regions}

        # Create a request to call projects.models.create.
        request = self.client.projects().models().create(parent=project_path, body=request_body)

        # Make the call.
        return self.execute_request(request)

    def delete_model(self, model_name):
        """Deletes a model.

        Args:
            model_name (str):

        Returns:
            dict: response from executing delete request
        """
        path = 'projects/{}/models/{}'.format(self.project_id, model_name)
        request = self.client.projects().models().delete(name=path)
        return self.execute_request(request)

    def start_training_job(self, job_id, scale_tier, package_uris, python_module, region, job_dir, runtime_version, python_version, job_arguments=[], hyperparameter_spec=None):
        """Creates a trainig job on cloud ml.

        Args:
            job_id (str):
            scale_tier (str or dict): one of BASIC, STANDARD_1, PREMIUM_1,
                BASIC_GPU, BASIC_TPU or CUSTOM (requires own configuration
                of masterType, workerCount, parameterServerType, workerCount,
                parameterServerCount and scaleTier in a dictionary).
            package_uris (list[str]): Cloud storage location where the packages
                are with the training program and any additional dependencies
                are stored.
            python_module (str): the python module name to run after installing.
            region (str):
            job_dir (str): cloud storage path where to store training outputs and
                other data needed for training.
            runtime_version (str): cloud ml runtime version for training.
            python_version (str): '2.7' or '3.5' (python3 is only supported for
                runtime_versions '1.4' and above).
            job_arguments (dict): command line arguments to pass to the programme.
            hyperparameter_spec (dict): can be used to do hyperparameter tuning.
                Have a look: https://cloud.google.com/ml-engine/reference/rest/v1/projects.jobs#hyperparameterspec

        Returns:

        """
        if isinstance(scale_tier, dict):
            required_keys = {'masterType', 'workerCount', 'parameterServerType', 'workerCount', 'parameterServerCount', 'scaleTier'}
            if not len(required_keys - scale_tier.keys()) == 0:
                raise ValueError("Not all required fields for CUSTOM scaleTier present. Expected fields: {}".format(required_keys))
        else:
            scale_tier = {'scaleTier': scale_tier}

        training_input = {"packageUris": package_uris,
                          "pythonModule": python_module,
                          "args": job_arguments,
                          "region": region,
                          "jobDir": job_dir,
                          "runtimeVersion": runtime_version,
                          "pythonVersion": python_version}
        training_input.update(scale_tier)
        if hyperparameter_spec:
            training_input['hyperparameters'] = hyperparameter_spec

        request_body = {'jobId': job_id,
                        'trainingInput': training_input}

        project_path = 'projects/{}'.format(self.project_id)
        request = self.client.projects().jobs().create(parent=project_path, body=request_body)
        return self.execute_request(request)

    @classmethod
    def execute_request(cls, request):
        """Executes the request and returns the response body unless
        an error occurred.

        Args:
            request ():

        Returns:
            dict
        """
        try:
            return request.execute()
        except errors.HttpError as err:
            # Something went wrong, print out some information.
            logging.error(err._get_reason())
