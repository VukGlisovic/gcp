from google.cloud import pubsub
from google.api_core.exceptions import AlreadyExists, NotFound
import logging


class Publisher(object):

    def __init__(self, project_id):
        self.project_id = project_id
        self.publisher_client = pubsub.PublisherClient()
        self.subscriber_client = pubsub.SubscriberClient()

    def create_topic_path(self, topic_name):
        """Creates a meaningful topic path of the form:
        'projects/{project}/topics/{topic}'

        Args:
            topic_name (str):

        Returns:
            str
        """
        return self.publisher_client.topic_path(self.project_id, topic_name)

    def create_subscription_path(self, subscription_name):
        """Creates a meaningful subscription path of the form:
        'projects/{project}/topics/{topic}'

        Args:
            subscription_name (str):

        Returns:
            str
        """
        return self.subscriber_client.subscription_path(self.project_id, subscription_name)

    def create_topic(self, topic_name):
        """Creates a topic in the project the object has been created in.

        Args:
            topic_name (str):

        Returns:
            None
        """
        topic_path = self.create_topic_path(topic_name)
        try:
            self.publisher_client.create_topic(name=topic_path)
        except AlreadyExists:
            logging.info("Topic %s already exists", topic_name)

    def delete_topic(self, topic_name):
        """Tries to delete topic_name. If the topic_name doesn't exist,
        it will throw a NotFound 404 exception.

        Args:
            topic_name (str):

        Returns:
            None
        """
        topic_path = self.create_topic_path(topic_name)
        self.publisher_client.delete_subscription(topic_path)

    def check_topic_existence(self, topic_name):
        """Validate whether the topic exists or not. Returns True if
        topic_name exists.

        Args:
            topic_name (str):

        Returns:
            bool
        """
        topic_path = self.create_topic_path(topic_name)
        try:
            self.publisher_client.get_topic(topic_path)
            return True
        except NotFound:
            logging.info("Topic %s does not exist", topic_name)
            return False

    def create_subscription(self, subscription_name, topic_name, ack_deadline_seconds=10):
        """Creates a subscription in the project the object has been
        created in.

        Args:
            subscription_name (str):
            topic_name (str):
            ack_deadline_seconds (int):

        Returns:
            None
        """
        subscription_path = self.create_subscription_path(subscription_name)
        topic_path = self.create_topic_path(topic_name)
        self.subscriber_client.create_subscription(name=subscription_path, topic=topic_path, ack_deadline_seconds=ack_deadline_seconds)

    def publish_message(self, topic_name, data, **kwargs):
        """Python 3 expects data to be a bytestring. Therefore, you must
        convert any data you input here first to bytes. An example of how
        you can do this for a dictionary is:
        json.dumps({'message': 'Hello world!'}).encode('utf-8')

        Args:
            topic_name (str):
            data (bytes): the information you want to pass in the message
            **kwargs: additional keyword arguments will be passed on in
                the message. These can be normal python strings.

        Returns:
            None
        """
        topic_path = self.create_topic_path(topic_name)
        future = self.publisher_client.publish(topic_path, data=data, **kwargs)

    def pull_message(self, subscription_name, max_messages=1, return_immediately=True):
        """

        Args:
            subscription_name (str):
            max_messages (int):
            return_immediately (bool):

        Returns:

        """
        subscription_path = self.create_subscription_path(subscription_name)
        messages_list = self.subscriber_client.pull(subscription_path, max_messages=max_messages, return_immediately=return_immediately)
        return messages_list
