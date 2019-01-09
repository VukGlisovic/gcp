from google.cloud import pubsub
from google.api_core.exceptions import AlreadyExists, NotFound
import logging


class PubSub(object):

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
        self.publisher_client.delete_topic(topic_path)

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

    def delete_subscription(self, subscription_name):
        """Tries to delete subscription_name. If the subscription_name
        doesn't exist, it will throw a NotFound 404 exception.

        Args:
            subscription_name (str):

        Returns:
            None
        """
        subscription_path = self.create_subscription_path(subscription_name)
        self.subscriber_client.delete_subscription(subscription_path)

    def publish_message(self, topic_name, data, callback_fnc=None, **kwargs):
        """Python 3 expects data to be a bytestring. Therefore, you must
        convert any data you input here first to bytes. An example of how
        you can do this for a dictionary is:
        json.dumps({'message': 'Hello world!'}).encode('utf-8')

        Args:
            topic_name (str):
            data (bytes): the information you want to pass in the message.
            callback_fnc (function): if provided, it will be used as a callback
                for when the message is published.
            **kwargs: additional keyword arguments will be passed on in
                the message. These can be normal python strings.

        Returns:
            None
        """
        topic_path = self.create_topic_path(topic_name)
        future = self.publisher_client.publish(topic_path, data=data, **kwargs)
        if callback_fnc:
            future.add_done_callback(callback_fnc)

    def pull_message(self, subscription_name, max_messages=1, return_immediately=True):
        """Pull messages from a subscription. It returns a list of ReceivedMessage
        objects. Note that you still have to acknowledge the messages if you don't
        want the message to be republished.

        Args:
            subscription_name (str):
            max_messages (int):
            return_immediately (bool):

        Returns:
            list[google.cloud.pubsub_v1.types.ReceivedMessage]
        """
        subscription_path = self.create_subscription_path(subscription_name)
        # return a google.cloud.pubsub_v1.types.PullResponse object
        pull_response = self.subscriber_client.pull(subscription_path, max_messages=max_messages, return_immediately=return_immediately)
        messages_list = pull_response.received_messages
        return messages_list

    def subscribe(self,
                  subscription_name,
                  callback_fnc,
                  max_bytes=104857600,
                  max_messages=100,
                  resume_threshold=0.8,
                  max_requests=100,
                  max_request_batch_size=100,
                  max_request_batch_latency=0.01,
                  max_lease_duration=7200):
        """This is a streaming pull method. It triggers a background thread that
        asynchronously receives messages on a given subscription. Note that the
        callback_fnc receives google.cloud.pubsub_v1.subscriber.message.Message
        messages. You have to acknowledge the messages in the callback_fnc. You
        can do this with the message.ack(). The message object also contains the
        data attribute and the attributes (keyword arguments passed on in the publish
        method). The attributes can be turned into a python dictionary by executing
        dict(message.attributes.items()).

        Note (I believe this is happening): the background thread is started within
        the current python process. The way I see you can stop this background thread
        is by calling streaming_pull_future.cancel() or by stopping the main python
        process.

        Remark: flow_control is under testing; not sure how it exactly workes yet.

        Args:
            subscription_name (str):
            callback_fnc (function):
            max_bytes (int):
            max_messages (int): max allowed outstanding messages for a worker
            resume_threshold (float): between 0 and 1; indicates a percentage
            max_requests (int):
            max_request_batch_size (int):
            max_request_batch_latency (float): in seconds
            max_lease_duration (int): in seconds

        Returns:
            google.cloud.pubsub_v1.subscriber.futures.StreamingPullFuture
        """
        subscription_path = self.create_subscription_path(subscription_name)
        # Flow control; this can help not overhoarding the system
        flow_control = pubsub.types.FlowControl(max_bytes,
                                                max_messages,
                                                resume_threshold,
                                                max_requests,
                                                max_request_batch_size,
                                                max_request_batch_latency,
                                                max_lease_duration)
        # This will keep pulling from the subscription
        streaming_pull_future = self.subscriber_client.subscribe(subscription_path, callback=callback_fnc, flow_control=flow_control)
        return streaming_pull_future
