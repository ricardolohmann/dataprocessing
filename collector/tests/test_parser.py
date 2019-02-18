from io import StringIO
import unittest

from collector.exceptions import InvalidLogLineException
from collector.parser import parse_file


class TestParser(unittest.TestCase):
    """Test parser behaviors."""

    def test_parse_correct_file(self):
        """Should be possible to parse the file if it follows the expected
        strcture.
        """
        file_content = """Latitude: 30°02′59″S   -30.04982864
        Longitude: 51°12′05″W   -51.20150245
        Distance: 2.2959 km  Bearing: 137.352°
        Latitude: 30°04′03″S   -30.06761588
        Longitude: 51°14′23″W   -51.23976111
        Distance: 4.2397 km  Bearing: 210.121°
        """
        log_file = StringIO(file_content)
        log_values = list(parse_file(log_file))

        self.assertEqual(len(log_values), 2)
        self.assertEqual(log_values[0], "-30.04982864\t-51.20150245\t137.352°")
        self.assertEqual(log_values[1], "-30.06761588\t-51.23976111\t210.121°")

    def test_blank_lines(self):
        """Should be possible to parse file with blank lines, they must be
        ignored.
        """
        file_content = """
        Latitude: 30°02′59″S   -30.04982864


        Longitude: 51°12′05″W   -51.20150245

        Distance: 2.2959 km  Bearing: 137.352°

        """
        log_file = StringIO(file_content)
        log_values = list(parse_file(log_file))

        self.assertEqual(len(log_values), 1)
        self.assertEqual(log_values[0], "-30.04982864\t-51.20150245\t137.352°")

    def test_missing_line(self):
        """Should not be possible to parse file with lines out of order."""
        file_content = """Latitude: 30°02′59″S   -30.04982864
        Distance: 2.2959 km  Bearing: 137.352°
        Longitude: 51°14′23″W   -51.23976111
        Distance: 4.2397 km  Bearing: 210.121°
        """
        log_file = StringIO(file_content)
        with self.assertRaises(InvalidLogLineException):
            list(parse_file(log_file))

    def test_wrong_log_line_format(self):
        """Should not be possible to parse a line which is not on the expected
        format.
        """
        file_content = """Latitude: 30°02′59″S   -30.04982864
        Distance: 2.2959 km  Bearing: 137.352°
        Longitude: 51°14′23″W   -51.23976111
        Distance: 4.2397 km  Bearing: 210.121°
        """
        log_file = StringIO(file_content)
        with self.assertRaises(InvalidLogLineException):
            list(parse_file(log_file))
