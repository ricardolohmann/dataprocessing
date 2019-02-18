"""Collect log messages and send them to the broker."""

import logging
import os

from collector.parser import parse_file
from collector.services import MessageBrokerService
from collector.settings import MESSAGE_BROKER_ADDRESS, QUEUE_NAME


if __name__ == "__main__":
    logs_folder = "{0}/logs".format(os.getcwd())
    logging.debug('Reading logs from: {0}'.format(logs_folder))

    # instantiate a message broker to send logs to processors
    message_broker = MessageBrokerService(MESSAGE_BROKER_ADDRESS, QUEUE_NAME)

    # TODO: Think about a way to scale file reading too
    for file_name in os.listdir(logs_folder):
        logging.info('Reading file {0}'.format(file_name))
        with open("logs/{0}".format(file_name), "r", encoding="utf-8") as log_file:

            # TODO: Send logs in batches and compact them
            for log in parse_file(file_object=log_file):
                message_broker.send_message(log)

        logging.info('File ended.')

    message_broker.close()
    logging.info('Finished collecting logs.')
