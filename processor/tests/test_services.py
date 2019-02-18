import socket
import unittest
from unittest.mock import Mock, patch

import pymysql.cursors

from processor.google_maps_response_sample import sample
from processor.services import (LocationService, MessageBrokerService,
                                StorageService)


class TestLocationService(unittest.TestCase):

    @patch("processor.services.Client")
    @patch("processor.services.GEO_LOCATION_SERVICE_ENABLED", True)
    def test_get_location_details(self, mock_client):
        """Should be possible to get location details."""
        mock_geolocation_service = Mock()
        mock_geolocation_service.reverse_geocode.return_value = sample

        mock_client.return_value = mock_geolocation_service

        service = LocationService()
        location_details = service.get_location_details(10, 11)

        mock_geolocation_service.reverse_geocode.assert_called_with((10, 11))

        self.assertEqual(location_details["latitude"], "-30.049917")
        self.assertEqual(location_details["longitude"], "-51.201439")
        self.assertEqual(location_details["address"], "Rua Monsenhor Veras")
        self.assertEqual(location_details["number"], "405")
        self.assertEqual(location_details["neighborhood"], "Santana")
        self.assertEqual(location_details["city"], "Porto Alegre")
        self.assertEqual(location_details["postal_code"], "90610-010")
        self.assertEqual(location_details["state"], "RS")
        self.assertEqual(location_details["country"], "Brazil")

    @patch("processor.services.Client")
    @patch("processor.services.GEO_LOCATION_SERVICE_ENABLED", False)
    def test_get_location_details_geo_service_disabled(self, mock_client):
        """Geo Location service should not be called to get location details
        when it is disabled.
        """
        mock_geolocation_service = Mock()

        mock_client.return_value = mock_geolocation_service

        service = LocationService()
        service.get_location_details(10, 11)

        self.assertFalse(mock_geolocation_service.reverse_geocode.called)

    @patch("processor.services.Client")
    def test_parse_location_info(self, mock_client):
        """Should be possible to parse location info that is returned from
        geolocation service.
        """
        service = LocationService()
        location_details = service.parse_location_info(sample)
        self.assertEqual(location_details["latitude"], "-30.049917")
        self.assertEqual(location_details["longitude"], "-51.201439")
        self.assertEqual(location_details["address"], "Rua Monsenhor Veras")
        self.assertEqual(location_details["number"], "405")
        self.assertEqual(location_details["neighborhood"], "Santana")
        self.assertEqual(location_details["city"], "Porto Alegre")
        self.assertEqual(location_details["postal_code"], "90610-010")
        self.assertEqual(location_details["state"], "RS")
        self.assertEqual(location_details["country"], "Brazil")


class TestStorageService(unittest.TestCase):

    @patch("processor.services.pymysql.connect")
    def test_create_valid_storage(self, mock_connect):
        """Should be possible to create a storage service."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        service = StorageService("foo.bar", "root", "password", "schema")
        mock_connect.assert_called_with(
            host="foo.bar", user="root", password="password", db="schema",
            cursorclass=pymysql.cursors.DictCursor)
        self.assertEqual(service.connection, mock_connection)

    def test_create_invalid_storage(self):
        """Should not be possible to create a storage service with invalid
        parameters.
        """
        with self.assertRaises(pymysql.err.OperationalError):
            StorageService("foo.bar", "root", "password", "schema")

    @patch("processor.services.pymysql.connect")
    def test_save_info(self, mock_connect):
        """Should be possible to save info in storage."""
        # mock cursor context manager
        mock_cursor = Mock()
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)

        # mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor_context
        mock_connect.return_value = mock_connection

        service = StorageService("foo.bar", "root", "password", "schema")
        info = {"latitude": "10",
                "longitude": "20",
                "address": "Avenida Ipiranga",
                "number": "400",
                "neighborhood": "Santana",
                "city": "Porto Alegre",
                "postal_code": "123456-789",
                "state": "RS",
                "country": "Brazil"}
        service.save(info)

        self.assertTrue(mock_cursor.execute.called)
        args, kwargs = mock_cursor.execute.call_args_list[0]
        self.assertEqual(args[1], info)


class TestMessageBrokerService(unittest.TestCase):

    @patch("processor.services.pika")
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

    @patch("processor.services.pika")
    def test_subscribe_messages(self, mock_pika):
        """Should be possible to subscribe the message broker."""
        def callback():
            pass

        # mock channel
        mock_channel = Mock()

        # mock connection
        mock_connection = Mock()
        mock_connection.channel.return_value = mock_channel

        mock_pika.BlockingConnection.return_value = mock_connection

        service = MessageBrokerService("foo.address", "queue_name")
        service.subscribe(callback)

        self.assertTrue(mock_channel.start_consuming.called)
        mock_channel.basic_consume.assert_called_with(
            callback, queue="queue_name")
