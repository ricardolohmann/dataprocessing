import socket
import unittest
from unittest.mock import Mock, patch

from collector.services import MessageBrokerService


class TestMessageBrokerService(unittest.TestCase):

    @patch("collector.services.pika")
    def test_create_valid_broker(self, mock_pika):
        """Should be possible to create a message broker service."""
        # mock channel
        mock_channel = Mock()

        # mock connection
        mock_connection = Mock()
        mock_connection.channel.return_value = mock_channel

        mock_pika.BlockingConnection.return_value = mock_connection

        service = MessageBrokerService("foo.address", "queue_name")

        # test connection
        mock_pika.ConnectionParameters.assert_called_once_with("foo.address")
        self.assertEqual(service.connection, mock_connection)

        # test channel
        self.assertEqual(service.channel, mock_channel)

        # test queue is declared
        self.assertEqual(service.queue_name, "queue_name")
        mock_channel.queue_declare.assert_called_with(
            queue="queue_name", durable=True)

    def test_create_invalid_broker_address(self):
        """Should not be possible to create a broker with an invalid
        address.
        """
        with self.assertRaises(socket.gaierror):
            MessageBrokerService("foo.address", "queue_name")

    @patch("collector.services.pika")
    def test_publish_message(self, mock_pika):
        """Should be possible to send a message."""
        # mock channel
        mock_channel = Mock()

        # mock connection
        mock_connection = Mock()
        mock_connection.channel.return_value = mock_channel

        mock_pika.BlockingConnection.return_value = mock_connection

        service = MessageBrokerService("foo.address", "queue_name")
        service.send_message("my message")

        args, kwargs = mock_channel.basic_publish.call_args_list[0]
        self.assertEqual(kwargs["exchange"], "")
        self.assertEqual(kwargs["routing_key"], "queue_name")
        self.assertEqual(kwargs["body"], "my message")
