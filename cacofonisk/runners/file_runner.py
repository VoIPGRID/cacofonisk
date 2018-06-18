"""
Implement a Runner which reads files, instatiates a EventHandler and calls
the EventHandler accordingly.

If the main application desires to replay previously stored events (an
event replay log), the FileRunner is the runner to use.

Events are loaded from a ``.json`` file which holds a list of
dictionaries.
"""
from json import load

from ..handlers import EventHandler


class FileRunner(object):
    def __init__(self, files, reporter, channel_manager_class=EventHandler):
        """
        FileRunner is a Runner that reads from one or more files.

        Args:
            files (list): A list of strings containing filenames or,
            a string containing a filename.
            reporter (Reporter): The reporter to use for this Runner.
            channel_manager_class: The EventHandler to instantiate for this
                Runner.
        """
        if type(files) == str:
            self.files = [files]
        elif type(files) == list:
            self.files = files
        else:
            raise TypeError('Expected string or list for files argument')
        self.reporter = reporter
        self.channel_manager_class = channel_manager_class
        self.channel_managers = []

    def _load_events_from_disk(self, filename):
        """
        Read the file with the given file name and return the JSON contents.

        Args:
            filename (str): The name of the file to read.

        Returns:
            A JSON object.
        """
        with open(filename, 'r') as f:
            events = load(f)
        return events

    def run(self):
        """
        Read all the events from the files and pass them to channel_manager.
        """
        for filename in self.files:
            events = self._load_events_from_disk(filename)
            channel_manager = self.channel_manager_class(
                reporter=self.reporter)
            interesting_events = channel_manager.event_handlers().keys()

            for event in events:
                if (
                        not channel_manager.FILTER_EVENTS or
                        event['Event'] in interesting_events
                   ):
                    channel_manager.on_event(event)

            self.channel_managers.append(channel_manager)
