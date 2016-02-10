import sys

from datetime import datetime

from .base_reporter import BaseReporter


class DebugReporter(BaseReporter):
    """
    Reporter that logs all trace_msg messages to stdout.
    """
    def trace_msg(self, msg):
        sys.stdout.write('{}: {}\n'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            msg))
        sys.stdout.flush()
