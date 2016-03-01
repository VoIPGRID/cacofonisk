"""
Implement a Runner which reads files, instatiates a ChannelManager and calls
the ChannelManager accordingly.

If the main application desires to replay previously stored events (an
event replay log), the FileRunner is the runner to use.

Events are loaded from a ``.json`` file which holds a list of
dictionaries.
"""
from json import load

from ..channel import ChannelManager


class FileRunner(object):
    def __init__(self, files, reporter, channel_manager_class=ChannelManager):
        """
        FileRunner is a Runner that reads from one or more files.

        Args:
            files [str]: A list of strings containing filenames or, a string
                        containing a filename.
            reporter (Reporter): The reporter to use for this Runner.
            channel_manager_class: The ChannelManager to instantiate for this
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

    def load_events_from_disk(self, filename):
        with open(filename, 'r') as f:
            events = load(f)
        return events

    def run(self):
        for filename in self.files:
            events = self.load_events_from_disk(filename)
            channel_manager = self.channel_manager_class(reporter=self.reporter)

            for event in events:
                if (
                        '*' in channel_manager.INTERESTING_EVENTS or
                        event['Event'] in channel_manager.INTERESTING_EVENTS
                   ):
                    channel_manager.on_event(event)

            self.channel_managers.append(channel_manager)
