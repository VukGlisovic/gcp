from googleapiclient import discovery, errors
import logging

logging.basicConfig(level=logging.INFO)


class CloudML(object):

    def __init__(self, project_id):
        self.client = discovery.build('ml', 'v1')
        self.project_id = project_id

    def create_model(self, model_name, description):
        """Method for creating a new model. Note that this only creates
        a model 'template'; it does not create the actual model. To make
        an actual model for serving, you need to create a version for
        this model.

        Args:
            model_name (str):
            description (str):

        Returns:
            dict: response from executing create request
        """
        # Store your full project ID in a variable in the format the API needs.
        project_path = 'projects/{}'.format(self.project_id)

        # Create a dictionary with the fields from the request body.
        request_body = {'name': model_name,
                        'description': description}

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