
class InvalidLogLineException(Exception):
    """Exception which happens when the log line is invalid.

    e.g. We need to extract data from three log lines (latitude, longitude and
    distance). If one of the lines is missing, this exception is thrown.
    """
