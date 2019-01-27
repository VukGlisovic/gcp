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

    def get_model(self, model_name):
        """Retrieves model information including name, description and the
        default version (if at least one version has been deployed).

        Args:
            model_name (str):

        Returns:
            dict
        """
        path = 'projects/{}/models/{}'.format(self.project_id, model_name)
        request = self.client.projects().models().get(name=path)
        return self.execute_request(request)

    def create_model_version(self, model_name, version_name, deployment_uri, description=None, runtime_version='1.12', machine_type=None, labels=None, framework='TENSORFLOW', python_version='3.5', min_nodes=0):
        """Creates a version for a model. If you want this version to be the default
        version. Use the set_default_version method.

        Args:
            model_name (str):
            version_name (str): this must be unique within the model it is created in.
            deployment_uri (str): cloud storage location of the model to be used for
                creating a version.
            description (str):
            runtime_version (str): cloud ml engine runtime version to use. Options are
                '1.0', '1.2', '1.4'-'1.12'. This usually depends on the runtime version
                that was used while training the model. If python version '3.5' is used,
                then you must use a runtime version of at least '1.4'.
            machine_type (str): there's only a handful supported machine types. Checkout
                the cloud ml engine to see what is supported.
            labels (dict):
            framework (str): options are TENSORFLOW, SCIKIT_LEARN and XGBOOST.
            python_version (str): '2.7' or '3.5'.
            min_nodes (int): number of nodes that will always be up and running. If the
                traffic gets too high and the node(s) can't keep up, additional nodes
                will be added. If min_nodes=0, then it will completely scale down if
                there is no traffic and cost will be zero.

        Returns:
            dict
        """
        path = 'projects/{}/models/{}'.format(self.project_id, model_name)

        auto_scaling = {"minNodes": min_nodes}

        request_body = {"name": version_name,
                        "deploymentUri": deployment_uri,
                        "runtimeVersion": runtime_version,
                        "framework": framework,
                        "pythonVersion": python_version,
                        "autoScaling": auto_scaling}

        if description:
            request_body['description'] = description
        if machine_type:
            request_body['machineType'] = machine_type
        if labels:
            request_body['labels'] = labels

        request = self.client.projects().models().versions().create(parent=path, body=request_body)
        return self.execute_request(request)

    def set_default_version(self, model_name, version_name):
        """Sets the default version of a model.

        Args:
            model_name (str): model to adjust the default version for.
            version_name (str): this version will be used as the default version
                for predictions.

        Returns:
            dict
        """
        path = 'projects/{}/models/{}/versions/{}'.format(self.project_id, model_name, version_name)
        request = self.client.projects().models().versions().setDefault(name=path)
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

    def get_job(self, job_id):
        """Method for retrieving a job. This contains information about the
        input parameters for starting a job and the status of the job (whether
        it's running, succeeded, failed, etc).

        Args:
            job_id (str):

        Returns:
            dict
        """
        path = 'projects/{}/jobs/{}'.format(self.project_id, job_id)
        request = self.client.projects().jobs().get(name=path)
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
