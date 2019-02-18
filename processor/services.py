import pika
import logging

from googlemaps import Client

import pymysql.cursors

from processor.google_maps_response_sample import sample
from processor.settings import (GEO_LOCATION_API_KEY,
                                GEO_LOCATION_SERVICE_ENABLED)


class LocationService(object):
    """Class used to request geolocation info."""

    def __init__(self):
        """Initiates the geolocation client."""
        self.service = Client(key=GEO_LOCATION_API_KEY)

    def get_location_details(self, latitude, longitude):
        """Get location details by using latitude and longitude.

        This parses the location information to only get the required data.
        It also verifies if the location service is enabled to request details
        for it.

        :param latitude: Place's latitude
        :param longitude: Place's longitude
        :returns: It gets the parsed data from the location service when it's
            enabled otherwise get from a sample data
        """
        if GEO_LOCATION_SERVICE_ENABLED:
            location_info = self.service.reverse_geocode((latitude, longitude))
        else:
            location_info = sample
        return self.parse_location_info(location_info)

    def parse_location_info(self, location_info):
        """Parse the location information to get the expected fields.

        :param location_info: The location information provided by the location
            service
        :returns: The parsed data with only required fields
        """
        info = location_info[0]
        return {"latitude": str(info['geometry']['location']['lat']),
                "longitude": str(info['geometry']['location']['lng']),
                "address": info['address_components'][1]['long_name'],
                "number": info['address_components'][0]['long_name'],
                "neighborhood": info['address_components'][2]['long_name'],
                "city": info['address_components'][3]['long_name'],
                "postal_code": info['address_components'][6]['long_name'],
                "state": info['address_components'][4]['short_name'],
                "country": info['address_components'][5]['long_name']}


class StorageService(object):
    """Implements the persistence layer."""

    def __init__(self, host, user, password, db):
        """Initialize the storage service.

        :param host: The host server
        :param user: The user used for authentication
        :param password: The user's password
        :param db: The dataabse schema name
        """
        self.connection = pymysql.connect(
            host=host, user=user, password=password, db=db,
            cursorclass=pymysql.cursors.DictCursor)

    def save(self, log_information):
        """Persists the data in the storage.

        :param log_information: The log data that needs to be stored
        """
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = """INSERT INTO `logs` (
                    `latitude`, `longitude`, `address`, `number`,
                    `neighborhood`, `city`, `postal_code`, `state`,
                    `country`
                ) VALUES (
                    %(latitude)s, %(longitude)s, %(address)s, %(number)s,
                    %(neighborhood)s, %(city)s, %(postal_code)s, %(state)s,
                    %(country)s
                )"""
            cursor.execute(sql, log_information)

        # connection is not autocommit by default. So we must commit to save
        # changes.
        self.connection.commit()


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

    def subscribe(self, callback):
        """Subscribe a callback function to the queue.

        :param callback: A callback function that will run when a message is
            received
        """
        self.channel.basic_consume(callback, queue=self.queue_name)
        self.channel.start_consuming()

    def close(self):
        """Close connection with the broker."""
        self.connection.close()
