from collector.exceptions import InvalidLogLineException

FIELD_SEPARATOR = "\t"


def parse_file(file_object):
    """Parses the log file to get the following fields:
    - latitude
    - longitude
    - distance

    :param file_object: The log file object which will be parsed
    :returns: Log values in a string format separated by the value of
        `FIELD_SEPARATOR`
    """
    log_lines = extract_line(file_object)
    extractors = [extract_latitude, extract_longitude, extract_distance]

    while True:
        log_values = []
        for extractor in extractors:
            try:
                log_line = next(log_lines)
            except StopIteration:
                # Extracted all log lines
                return None
            log_values.append(extractor(log_line))

        yield FIELD_SEPARATOR.join(log_values)


def extract_line(file_object):
    """Extract log line from a file object.

    :param file_object: The log file object where logs will be extracted
    :returns: A log line generator to avoid memory usage
    """
    for line in file_object:
        line = line.strip()
        if line:
            yield line


def extract_latitude(log_line):
    """Extract latitude data from a log line.

    :param log_line: The log line
    :returns: The latitude date from the log line.
    :raises InvalidLogLineException: When the log line is not valid
    """
    if log_line.startswith("Latitude"):
        return log_line.split(" ")[-1]
    raise InvalidLogLineException


def extract_longitude(log_line):
    """Extract longitude data from a log line.

    :param log_line: The log line
    :returns: The longitude date from the log line.
    :raises InvalidLogLineException: When the log line is not valid
    """
    if log_line.startswith("Longitude"):
        return log_line.split(" ")[-1]
    raise InvalidLogLineException


def extract_distance(log_line):
    """Extract distance data from a log line.

    :param log_line: The log line
    :returns: The distance date from the log line.
    :raises InvalidLogLineException: When the log line is not valid
    """
    if log_line.startswith("Distance"):
        return log_line.split(" ")[-1]
    raise InvalidLogLineException
