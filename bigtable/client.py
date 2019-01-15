from google.cloud import bigtable
from google.cloud.bigtable import column_family as bt_column_family
from google.cloud.bigtable import enums as bt_enums
from google.api_core.exceptions import AlreadyExists, Conflict, NotFound
import datetime as dt
import logging


class Bigtable(object):

    def __init__(self, project_id, instance_id):
        self.project_id = project_id
        self.instance_id = instance_id
        self.client = bigtable.Client(project_id, admin=True)
        self.instance = self.client.instance(instance_id)

    def create_instance(self, create_in_production, cluster_name, location_id, nr_nodes, use_ssd_storage, timeout=100):
        """To create an instance, you also have to configure cluster parameters. If the cluster
        already exists, an AlreadyExists exception is raised.

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
            raise AlreadyExists("Instance '{}' already exists.".format(self.instance_id))
        logging.info("Creating instance '%s'.", self.instance_id)
        # instance configurations
        production, nr_nodes = (bt_enums.Instance.Type.PRODUCTION, nr_nodes) if create_in_production else (bt_enums.Instance.Type.DEVELOPMENT, None)
        self.instance = self.client.instance(instance_id=self.instance_id, display_name=self.instance_id, instance_type=production)
        # cluster configurations
        cluster = self.create_cluster_config(cluster_name, location_id, nr_nodes, use_ssd_storage)
        # Create the instance with a cluster
        operation = self.instance.create(clusters=[cluster])
        # We want to make sure the operation completes.
        operation.result(timeout=timeout)

    def create_application_profile(self, app_profile_id, description, cluster_id, multi_cluster_routing, allow_transactional_writes):
        """Adds an application profile to a cluster of an instance. There's two main
        parameters to configure for an application profile:
        1) single or multi cluster routing:
            with multi-cluster routing, if for some reason a transaction fails for one
            cluster, it will automatically be rerouted to another cluster. An advantage
            for single cluster routing is that it helps isolate CPU-intensive loads.
        2) single row transactions:
            if enabled, then read-modify-write and check-and-mutate operations are
            allowed.
        You can find more info here: https://cloud.google.com/bigtable/docs/app-profiles

        Args:
            app_profile_id (str): name of the app profile
            description (str):
            cluster_id (str): name of the cluster to add the app profile to
            multi_cluster_routing (bool): whether to route data to a single cluster or
                to multiple clusters.
            allow_transactional_writes (bool): can only be true for single cluster routing.

        Returns:
            None
        """
        routing_policy_type = bt_enums.RoutingPolicyType.ANY if multi_cluster_routing else bt_enums.RoutingPolicyType.SINGLE

        app_profile = self.instance.app_profile(
            app_profile_id=app_profile_id,
            routing_policy_type=routing_policy_type,
            description=description,
            cluster_id=cluster_id,
            allow_transactional_writes=allow_transactional_writes
        )
        app_profile.create(ignore_warnings=True)

    def delete_instance(self):
        """Delete the instance. At the same time resets the instance attribute such
        that a new instance with the same instance_id can be created.

        Returns:
            None
        """
        logging.warning("Deleting instance '%s'", self.instance_id)
        self.instance.delete()
        # Reset the instance attribute
        self.instance = self.client.instance(self.instance_id)

    def create_cluster_config(self, cluster_name, location_id, nr_nodes, use_ssd_storage):
        """Create a cluster object with which you can create a cluster. If you'd like a
        development cluster, then set nr_nodes=None.

        Args:
            cluster_name (str):
            location_id (str):
            nr_nodes (int or None): if None, then development instance should be created.
            use_ssd_storage (bool): whether to use SSD or HDD storage

        Returns:
            google.cloud.bigtable.cluster.Cluster
        """
        storage_type = bt_enums.StorageType.SSD if use_ssd_storage else bt_enums.StorageType.HDD
        cluster = self.instance.cluster(
            cluster_name,
            location_id=location_id,
            serve_nodes=nr_nodes,
            default_storage_type=storage_type,
        )
        return cluster

    def create_cluster(self, cluster_name, location_id, nr_nodes, use_ssd_storage):
        """Creates a cluster for an existing Instance.

        Args:
            cluster_name (str):
            location_id (str):
            nr_nodes (int or None): if None, then development instance should be created.
            use_ssd_storage (bool): whether to use SSD or HDD storage

        Returns:
            None
        """
        cluster = self.create_cluster_config(cluster_name, location_id, nr_nodes, use_ssd_storage)
        logging.info("Creating cluster '%s'.", cluster_name)
        cluster.create()

    def create_table(self, table_name, app_profile_name=None, initial_split_rowkeys=[], column_families={}):
        """Create a table within the instance.

        Args:
            table_name (str):
            app_profile_name (str):
            initial_split_rowkeys (list):
            column_families (dict):

        Returns:
            None
        """
        table = self.instance.table(table_name, app_profile_name)
        logging.info("Creating table '%s'.", table_name)
        table.create(initial_split_keys=initial_split_rowkeys, column_families=column_families)

    def create_column_family(self, column_family_name, table_name, max_age=None, nr_max_versions=None, gc_rule_union=None):
        """Create a column family and add it to a table. Garbage collection rules
        can be included to the column family.

        Args:
            column_family_name (str):
            table_name (str):
            max_age (int): the time to live in days
            nr_max_versions (int): the number of versions that should be kept
            gc_rule_union (bool or None): if both max_age and nr_max_versions are specified,
                then this parameter should be a bool. If True, then the max age and the max
                versions rules are unified, if False, then the intersection of the rules is
                used.

        Returns:
            google.cloud.bigtable.column_family.ColumnFamily
        """
        if max_age and nr_max_versions:
            # Both rules are specified, this also means a merge method must be specified (union or intersection)
            time_to_live = dt.timedelta(days=max_age)
            max_age_rule = bt_column_family.MaxAgeGCRule(time_to_live)
            max_versions_rule = bt_column_family.MaxVersionsGCRule(nr_max_versions)
            if gc_rule_union is None:
                raise Conflict("If max_age and nr_max_versions are both specified, then gc_rule_union cannot be None.")
            elif gc_rule_union:
                gc_rule = bt_column_family.GCRuleUnion(rules=[max_age_rule, max_versions_rule])
            else:
                gc_rule = bt_column_family.GCRuleIntersection(rules=[max_age_rule, max_versions_rule])
        elif max_age:
            # only max age is specified
            time_to_live = dt.timedelta(days=max_age)
            gc_rule = bt_column_family.MaxAgeGCRule(time_to_live)
        elif nr_max_versions:
            # only max number of versions is specified
            gc_rule = bt_column_family.MaxVersionsGCRule(nr_max_versions)
        else:
            # no rule is specified
            gc_rule = None

        table = self.instance.table(table_name)
        if not table.exists():
            raise NotFound("Table name '{}' does not exist.".format(table_name))
        logging.info("Creating column family '%s' in table '%s'.", column_family_name, table_name)
        column_family = bt_column_family.ColumnFamily(column_family_name, table, gc_rule)
        column_family.create()
