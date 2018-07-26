import json
import sys

from cacofonisk import AmiRunner, BaseReporter, EventHandler


class NoOpEventHandler(EventHandler):
    """
    NoOpEventHandler is a simple EventHandler which simply passes the events to
    the reporter without further processing. This is useful for generating
    logs, if regular event processing is not desired.
    """

    def on_event(self, event):
        self._reporter.on_event(event)


class VerboseNoOpEventHandler(NoOpEventHandler):
    """
    Like NoOpEventHandler, but dumps all the events, not just the
    interesting ones.
    """
    FILTER_EVENTS = False


class JsonReporter(BaseReporter):
    """
    Dump all AMI events as JSON to stdout.
    """

    def __init__(self):
        self._has_first_line = False

    def on_event(self, event):
        """
        Write AMI events to a file in a json format. If the file does not
        exist. Create it with one opening bracket, and start writing events in
        the form of one dictionary per event.
        """
        json_data = json.dumps(dict(event), sort_keys=True)

        if self._has_first_line:
            sys.stdout.write(',')
        else:
            sys.stdout.write('[')
            self._has_first_line = True

        sys.stdout.write('\n  {}'.format(json_data))

    def close(self):
        sys.stdout.write('\n]')


reporter = JsonReporter()
# Attach the AmiRunner to the specified Asterisk.
runner = AmiRunner([
    'tcp://cacofonisk:bard@127.0.0.1:5038',
], reporter, handler=NoOpEventHandler)
runner.run()
