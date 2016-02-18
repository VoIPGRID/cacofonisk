import sys
from datetime import datetime
from json import load
import os
from unittest import TestCase


class BaseTestCase(TestCase):
    def open_file(self, filename, *args, **kwargs):
        path = os.path.dirname(__file__)
        filename = os.path.join(path, filename)
        return open(filename, *args, **kwargs)

    def load_events_from_disk(self, filename):
        with self.open_file(filename, 'r') as f:
            events = load(f)
        return events


class SilentReporter(object):
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

