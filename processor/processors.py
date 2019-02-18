"""Module that defines methods used to process logs."""
import logging

FIELD_SEPARATOR = "\t"


class LogProcessor(object):
    """Process log messages."""

    def __init__(self, location_service):
        """Initialize a log processor instance.

        :param location_service: The location service used to request places'
            details by its coordinates.
        """
        self.location_service = location_service

    def process_log(self, log_message):
        """Process log messages to request its location details.

        :param log_message: The log message. It comes on the following format:
            `LATITUDE_VALUE\tLONGITUDE_VALUE\tDISTANCE_VALUE`
        :returns: The location details that were provided by location service.
        """
        logging.debug('Message received: {0}'.format(log_message))

        # get required fields
        latitude, longitude, _ = log_message.split(FIELD_SEPARATOR)

        # request location details
        return self.location_service.get_location_details(latitude, longitude)
