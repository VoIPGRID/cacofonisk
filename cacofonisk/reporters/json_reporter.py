import json
import sys

from .base_reporter import BaseReporter


class JsonReporter(BaseReporter):
    """
    Reporter that writes (overwrites!) all received AMI events to the file
    specified at path.

    Usage:
        reporter = JsonReporter('path/to/file.json')
    """
    def __init__(self, path='test.json', *args, **kwargs):
        self.path = path

    def trace_ami(self, event):
        """
        Write AMI events to a file in a json format. If the file does not
        exist. Create it with one opening bracket, and start writing events in
        the form of one dictionary per event.
        """
        if not hasattr(self, '_trace_ami_fp'):
            self._trace_ami_fp = open(self.path, 'w')
            self._trace_ami_fp.write('[')
            self._trace_ami_count = 0
        comma = ',' if self._trace_ami_count else ''
        self._trace_ami_fp.write('{}\n  {}'.format(
            comma, json.dumps(dict(event))))
        self._trace_ami_count += 1
        sys.stderr.write('{} written\r'.format(self._trace_ami_count))

    def finalize(self):
        """
        Close the file at ``self.path`` by writing a closing bracket ']' tothe
        end of the file.
        """
        if hasattr(self, '_trace_ami_fp'):
            self._trace_ami_fp.write('\n]\n')
            self._trace_ami_fp.close()
            print('Wrote {} AMI events to: {}'.format(
                self._trace_ami_count, self._trace_ami_fp.name))
            del self._trace_ami_count
            del self._trace_ami_fp
