import unittest
from unittest.mock import Mock, patch

from processor.google_maps_response_sample import sample
from processor.processors import LogProcessor
from processor.services import LocationService


class TestLogProcessor(unittest.TestCase):

    @patch("processor.services.Client")
    @patch("processor.services.GEO_LOCATION_SERVICE_ENABLED", True)
    def test_process_log(self, mock_geo_location_client):
        mock_geolocation_service = Mock()
        mock_geolocation_service.reverse_geocode.return_value = sample

        mock_geo_location_client.return_value = mock_geolocation_service

        location_service = LocationService()
        processor = LogProcessor(location_service)

        processed_log = processor.process_log("10\t20\t30")
        self.assertEqual(processed_log["latitude"], "-30.049917")
        self.assertEqual(processed_log["longitude"], "-51.201439")
        self.assertEqual(processed_log["address"], "Rua Monsenhor Veras")
        self.assertEqual(processed_log["number"], "405")
        self.assertEqual(processed_log["neighborhood"], "Santana")
        self.assertEqual(processed_log["postal_code"], "90610-010")
        self.assertEqual(processed_log["state"], "RS")
        self.assertEqual(processed_log["country"], "Brazil")
