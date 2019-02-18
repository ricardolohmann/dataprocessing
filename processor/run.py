"""Consume logs that are comming thrue the broker queue."""
import logging

from functools import partial

from processor.processors import LogProcessor
from processor.services import (LocationService, MessageBrokerService,
                                StorageService)
from processor.settings import (MESSAGE_BROKER_ADDRESS, QUEUE_NAME, STORAGE_DB,
                                STORAGE_HOST, STORAGE_USER, STORAGE_PASSWORD)


def process_message(processor, storage, ch, method, properties, body):
    """Process the received message by getting the geolocation information
    then storing it.
    """
    ch.basic_ack(delivery_tag=method.delivery_tag)
    location_details = processor.process_log(str(body, "utf-8"))
    storage.save(location_details)


if __name__ == "__main__":
    logging.info('Processor being initialized...')
    location_service = LocationService()
    storage_service = StorageService(STORAGE_HOST, STORAGE_USER,
                                     STORAGE_PASSWORD, STORAGE_DB)
    processor = LogProcessor(location_service)

    # bind processor and storage to the callback, this way we can use them
    # when a message is received
    on_message_received = partial(process_message, processor, storage_service)

    message_broker = MessageBrokerService(MESSAGE_BROKER_ADDRESS, QUEUE_NAME)
    message_broker.subscribe(callback=on_message_received)

    logging.info('Waiting messages.')
