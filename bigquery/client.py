import logging
from google.cloud import bigquery
from google.api_core.exceptions import Conflict, BadRequest

logging.basicConfig(level=logging.INFO)


class Bigquery(object):

    def __init__(self, project_id, location, dataset_id):
        """Will instantiate a Bigquery class with which you can create datasets,
        tables, insert data, etc. Note that you have to provide a dataset_id
        which will be viewed as the default dataset to use for all actions.

        Args:
            project_id (str):
            dataset_id (str):
        """
        self.client = bigquery.Client(project_id)
        self.dataset_id = dataset_id
        self.location = location

    def create_dataset(self):
        """Create a bigquery Dataset. The dataset will be created in the
        project that the client has been created in.

        Returns:
            None
        """
        dataset_ref = self.client.dataset(self.dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = self.location
        try:
            self.client.create_dataset(dataset)
            logging.info("Successfully created dataset %s", self.dataset_id)
        except Conflict:
            logging.info("Dataset %s already exists", self.dataset_id)

    def delete_dataset(self, delete_contents=True):
        """Deletes a bigquery Dataset. The dataset will be deleted from the
        project that the client has been created in.

        Args:
            delete_contents (bool): whether to delete tables from the Dataset

        Returns:
            None
        """
        dataset_ref = self.client.dataset(self.dataset_id)
        self.client.delete_dataset(dataset_ref, delete_contents)
        logging.info("Deleted dataset %s", self.dataset_id)

    def create_table(self, table_name, schema):
        """Creates a table in dataset_id with the specified schema.

        Args:
            table_name (str):
            schema (list[bigquery.SchemaField]):

        Returns:
            None
        """
        dataset_ref = self.client.dataset(self.dataset_id)
        table_ref = dataset_ref.table(table_name)
        table = bigquery.Table(table_ref, schema=schema)
        try:
            table = self.client.create_table(table)  # API request
        except Conflict:
            logging.info("Table with name %s already exists for dataset %s", table.table_id, self.dataset_id)

    def streaming_insert(self, data, table_id):
        """Does a streaming insert into a bigquery table. This means it can
        keep an open connection with bigquery and therefore the 1000 inserts
        per day limit can be handled with.

        Args:
            data (list[tuple]):
            table_id (str):

        Returns:
            None
        """
        dataset_ref = self.client.dataset(self.dataset_id)
        table_ref = dataset_ref.table(table_id)
        table = self.client.get_table(table_ref)
        return self.client.insert_rows(table, data)

    def execute_query(self, query, validate_query=False):
        """Executes bigquery query. Optionally, you can first let it validate
        your query to see if the query is valid. If not, then no query will be
        executed and therefore no costs will be incurred.

        Args:
            query (str):
            validate_query (bool):

        Returns:
            list
        """
        if validate_query:
            try:
                self.dry_run_query(query)
            except BadRequest as br:
                logging.error("%s Not executing query.", br.message.split('/jobs: ')[-1])
                return
        query_job = self.client.query(query)  # API request
        rows = query_job.result()  # Waits for query to finish
        return rows

    def dry_run_query(self, query):
        """Validates the query and let's you know how much data will be
        processed. The amount of data processed will be used by google to
        price the query. 1TB of data processing costs 5 dollars.
        The method works as follows; basically, if it doesn't raise a
        BadRequest error, it means the query is valid.

        Args:
            query (str):

        Returns:
            bool
        """
        job_config = bigquery.QueryJobConfig()
        job_config.dry_run = True
        job_config.use_query_cache = False
        query_job = self.client.query(query, job_config=job_config, location=self.location)
        # A dry run query completes immediately.
        assert query_job.state == 'DONE'
        assert query_job.dry_run
        logging.info("This query will process {:.4f}MB.".format(query_job.total_bytes_processed / 1024. / 1024.))
        return True
