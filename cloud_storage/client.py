from google.cloud import storage
import logging

logging.basicConfig(level=logging.INFO)


class CloudStorage(object):

    def __init__(self, project_id):
        self.client = storage.Client(project_id)

    def create_bucket(self, bucket_name):
        """Creates a new bucket.

        Args:
            bucket_name (str):

        Returns:
            None
        """
        bucket = self.client.create_bucket(bucket_name)
        logging.info("Created bucket: %s", bucket.name)

    def delete_bucket(self, bucket_name):
        """Deletes a bucket.

        Args:
            bucket_name (str):

        Returns:
            None
        """
        bucket = self.client.bucket(bucket_name)
        bucket.delete(force=True)
        logging.info("Deleted bucket %s", bucket_name)

    def upload_blob_from_filename(self, bucket_name, source_filename, destination_blobname):
        """Uploads a file to cloud storage.

        Args:
            bucket_name (str):
            source_filename (str):
            destination_blobname (str):

        Returns:
            None
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_blobname)
        blob.upload_from_filename(source_filename)
        logging.info("Uploaded file %s to blob %s", source_filename, destination_blobname)

    def upload_blob_from_data(self, bucket_name, data, destination_blobname):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_blobname)
        blob.upload_from_string(data)
        logging.info("Uploaded content to blob %s", destination_blobname)
