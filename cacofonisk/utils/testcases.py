import json
import os
from unittest import TestCase


class BaseTestCase(TestCase):
    """
    BaseTestCase that has methods to open and parse json event logs.
    """

    def open_file(self, filename, *args, **kwargs):
        """"
        Open a filename. Aditional arguments are passed to open().

        Args:
            filename (str): File to open (relative to current path).
        """
        path = os.path.dirname(__file__)
        filename = os.path.join(path, filename)
        return open(filename, *args, **kwargs)

    def load_events_from_disk(self, filename):
        """
        Load events from a json event log.

        Args:
            filename (str): File to open (relative to current path).

        Returns:
            list: list of events
        """
        with self.open_file(filename, 'r') as f:
            events = json.load(f)
        return events
