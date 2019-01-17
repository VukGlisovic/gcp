from google.cloud import storage
import logging

logging.basicConfig(level=logging.INFO)


class CloudStorage(object):

    def __init__(self, project_id):
        self.client = storage.Client(project_id)

    def create_bucket(self, bucket_name, location=None):
        """Creates a new bucket.

        Args:
            bucket_name (str):
            location (str): for example US, EU, ASIA

        Returns:
            None
        """
        bucket = self.client.bucket(bucket_name)
        bucket.create(location=location.upper())
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
        logging.info("Deleted bucket '%s'.", bucket_name)

    def upload_blob_from_filename(self, source_filename, destination_gcs_path):
        """Uploads a file to cloud storage.

        Args:
            source_filename (str): a local path pointing to the file to upload.
            destination_gcs_path (str): a full cloud storage path (starting with gs://).

        Returns:
            None
        """
        bucket_name, filepath = self.parse_gcs_path(destination_gcs_path)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(filepath)
        blob.upload_from_filename(source_filename)
        logging.info("Uploaded file %s to filepath %s in bucket %s", source_filename, filepath, bucket_name)

    def upload_blob_from_data(self, data, destination_gcs_path):
        """Uploads data to cloud storage.

        Args:
            data (str): the content to upload.
            destination_gcs_path (str): a full cloud storage path (starting with gs://).

        Returns:
            None
        """
        bucket_name, filepath = self.parse_gcs_path(destination_gcs_path)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(filepath)
        blob.upload_from_string(data)
        logging.info("Uploaded content to filepath %s in bucket %s.", filepath, bucket_name)

    def delete_blob(self, gcs_path):
        """Deletes a blob from cloud storage.

        Args:
            gcs_path (str):  a full cloud storage path (starting with gs://).

        Returns:
            None
        """
        bucket_name, filepath = self.parse_gcs_path(gcs_path)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(filepath)
        blob.delete()
        logging.info("Deleted file '%s' from bucket '%s'.", filepath, bucket_name)

    def get_blob_content(self, gcs_path):
        """Downloads content from the specified cloud storage path.

        Args:
            gcs_path (str): a full cloud storage path (starting with gs://).

        Returns:
            str
        """
        bucket_name, filepath = self.parse_gcs_path(gcs_path)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(filepath)
        content = blob.download_as_string().decode('utf-8')
        return content

    @classmethod
    def parse_gcs_path(cls, gcs_path):
        """Parses a google cloud storage path. For example:
        gs://test_bucket/test_sub_folder/data.txt is split up into
        bucket_name='test_bucket' and filepath='test_sub_folder/data.txt'

        Args:
            gcs_path (str): a full cloud storage path (starting with gs://)

        Returns:
            tuple[str, str]
        """
        if not gcs_path.startswith('gs://'):
            raise ValueError("Cannot download file from cloud storage when gcs_path doesn't start with 'gs://'.")
        return gcs_path[5:].split('/', 1)
