import asyncio
import signal
import sys

from panoramisk import Manager

from ..channel import ChannelManager


class AmiRunner(object):
    """
    A Runner which reads Asterisk AMI events and passes them to a
    ChannelManager instance.
    """
    def __init__(self, amihosts, reporter, channel_manager=ChannelManager):
        """
        Args:
            amihosts [dict]: A list of dictionaries.
        """
        self.amihosts = amihosts
        self.reporter = reporter
        self.channel_manager = channel_manager
        self.loop = asyncio.get_event_loop()

    def attach_all(self):
        """
        attach_all attaches a channelmanager to all amihosts defined in
        self.amihosts by calling meth:`attach` on all of them.
        """
        assert not hasattr(self, 'amimgrs')
        assert not hasattr(self, 'channel_managers')
        self.amimgrs = {}

        for amihost in self.amihosts:
            self.attach(amihost)

    def attach(self, amihost):
        """
        attach amihost to a ChannelManager.

        Args:
            amihost (dict): A dictionary containing the connection settings for
                an AMI host.
        """
        # Create Panoramisk asterisk AMI manager.
        amimgr = Manager(
            loop=self.loop, host=amihost['host'], port=amihost['port'],
            username=amihost['username'], secret=amihost['password'],
            ssl=False, encoding='utf8')

        # Create our own channel manager.
        channel_manager = self.channel_manager(
            reporter=self.reporter,
        )

        # Tell Panoramisk to which events we want to listen.
        for event_name in channel_manager.INTERESTING_EVENTS:
            amimgr.register_event(event_name, self.on_event)

        # Record them for later use.
        self.amimgrs[amimgr] = channel_manager

        # Tell asyncio what to work on.
        asyncio.ensure_future(amimgr.connect())

    def on_event(self, amimanager, amievent):
        """When an event comes in, pass it to the relevant channel manager.

        Args:
            amimanager (Manager): The AMI manager from Panoramisk.
            amievent (Event): AMI event (a dict-like object with event data).
        """
        assert amimanager in self.amimgrs
        self.amimgrs[amimanager].on_event(amievent)

    def run(self):
        """
        Start the runner and run until halted.
        """
        self.attach_all()

        signal.signal(signal.SIGINT, self._close)

        self.loop.run_forever()

    def _close(self, signal, frame):
        """Clean shutdown the runner.
        """
        print('Disconnecting from Asterisk...')
        for amimgr in self.amimgrs:
            amimgr.close()
        self.reporter.close()
        sys.exit(0)
