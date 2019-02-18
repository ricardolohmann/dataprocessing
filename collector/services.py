import logging

import pika


class MessageBrokerService(object):
    """Service used to handle broker connection."""

    def __init__(self, address, queue_name):
        """Connect to the message broker and creates the queue.

        :param address: The message broker server address
        :param queue_name: The name that will for used for the queue
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(address))
        self.queue_name = queue_name

        # create the channel
        self.channel = self.connection.channel()

        # declare the queue
        self.channel.queue_declare(queue=queue_name, durable=True)

        logging.info("Message Broker connected to {0}".format(address))

    def send_message(self, message):
        """Send a message to the queue.

        :param message: The message that will be sent
        """
        self.channel.basic_publish(exchange="",
                                   routing_key=self.queue_name,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2
                                   ))

    def close(self):
        """Close connection with the broker."""
        self.connection.close()
