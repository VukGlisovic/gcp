from google.cloud import bigtable
from google.cloud.bigtable import enums as bt_enums
from google.api_core.exceptions import AlreadyExists
import logging


class Bigtable(object):

    def __init__(self, project_id, instance_id):
        self.project_id = project_id
        self.instance_id = instance_id
        self.client = bigtable.Client(project_id, admin=True)
        self.instance = self.client.instance(instance_id)

    def create_instance(self, create_in_production, cluster_name, location_id, nr_nodes, use_ssd_storage, timeout=100):
        """To create an instance, you also have to configure cluster parameters.

        Example configuration:
        - create_in_production=False
        - cluster_name='test_cluster'
        - location_id='us-central1-f'
        - nr_nodes=1
        - ssd_storage=False

        Args:
            create_in_production (bool): If True, then production instance is created. If False,
                a development instance will be created; note that nr_nodes will not be used as a
                parameter in that case.
            cluster_name (str): name of the cluster that will be created within the instance.
            location_id (str): the zone to create the cluster in.
            nr_nodes (int): only meaningful for production instance. Otherwise, in development
                instance, will be set to 1.
            use_ssd_storage (bool): if True, then SSD storage is used, otherwise HDD storage.
            timeout (int):

        Returns:
            None
        """
        if self.instance.exists():
            raise AlreadyExists("Instance %s already exists.", self.instance_id)
        logging.info("Creating instance %s", self.instance_id)
        # instance configurations
        production, nr_nodes = (bt_enums.Instance.Type.PRODUCTION, nr_nodes) if create_in_production else (bt_enums.Instance.Type.DEVELOPMENT, None)
        self.instance = self.client.instance(instance_id=self.instance_id, display_name=self.instance_id, instance_type=production)
        # cluster configurations
        storage_type = bt_enums.StorageType.SSD if use_ssd_storage else bt_enums.StorageType.HDD
        cluster = self.instance.cluster(
            cluster_name,
            location_id=location_id,
            serve_nodes=nr_nodes,
            default_storage_type=storage_type,
        )
        operation = self.instance.create(clusters=[cluster])
        # We want to make sure the operation completes.
        operation.result(timeout=timeout)

    def delete_instance(self):
        """Delete the instance. At the same time resets the instance attribute such
        that a new instance with the same instance_id can be created.

        Returns:
            None
        """
        logging.warning("Deleting instance %s", self.instance_id)
        self.instance.delete()
        # Reset the instance attribute
        self.instance = self.client.instance(self.instance_id)
