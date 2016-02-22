from datetime import datetime
import json
import os
import sys
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


class SilentReporter(object):
    """
    Reporter that will report absolutely nothing
    unless its silent property is set to False.
    It is meant for test cases.
    """
    def __init__(self):
        self.silent = True

    def on_event(self, event):
        pass

    def on_b_dial(self, caller, callee):
        pass

    def on_transfer(self, redirector, party1, party2):
        pass

    def trace_ami(self, event):
        pass

    def trace_msg(self, msg):
        if not self.silent:
            sys.stdout.write('{}: {}\n'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                msg))
            sys.stdout.flush()
