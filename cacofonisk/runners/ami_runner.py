import asyncio
import logging
import sys
from urllib.parse import urlparse

from panoramisk import Manager
import signal

from ..handlers import EventHandler


class AmiRunner(object):
    """
    A Runner which reads Asterisk AMI events and passes them to a
    EventHandler instance.
    """
    def __init__(self, asterisk_uris, reporter, handler=EventHandler,
                 logger=None):
        """
        Create and initialize a new AmiRunner.

        Args:
            asterisk_uris (list): A list of URIs with AMI host information.
            reporter (Reporter): A reporter which should receive notifications.
            handler (class): The EventHandler class for this runner.
            logger (Logger): The log handler for the runner.
        """
        self.asterisks = asterisk_uris
        self.reporter = reporter
        self.event_handler = handler
        self.loop = asyncio.get_event_loop()
        self.logger = logger or logging.getLogger(__name__)

        self.ami_managers = {}

    def attach_all(self):
        """
        Connect to all Asterisks
        """
        for asterisk in self.asterisks:
            self.attach(asterisk)

    def attach(self, asterisk):
        """
        Set up a connection to the specified Asterisk

        Args:
            asterisk (str): A connection string
        """
        ami_host = urlparse(asterisk)

        # Create Panoramisk asterisk AMI manager.
        manager = Manager(
            loop=self.loop, host=ami_host.hostname, port=ami_host.port,
            username=ami_host.username, secret=ami_host.password,
            ssl=ami_host.scheme in ('ssl', 'tls'), encoding='utf8',
            log=self.logger)

        # Create our own channel manager.
        event_handler = self.event_handler(
            reporter=self.reporter,
            hostname=ami_host.hostname,
            logger=self.logger,
        )

        # Tell Panoramisk to which events we want to listen.
        if event_handler.FILTER_EVENTS:
            for event_name in event_handler.event_handlers().keys():
                manager.register_event(event_name, self.on_event)
        else:
            manager.register_event('*', self.on_event)

        # Record them for later use.
        self.ami_managers[manager] = event_handler

        # Tell asyncio what to work on.
        asyncio.ensure_future(manager.connect())

    def on_event(self, manager, event):
        """
        When an event comes in, pass it to the relevant channel manager.

        Args:
            manager (Manager): The AMI manager from Panoramisk.
            event (Event): AMI event (a dict-like object with event data).
        """
        assert manager in self.ami_managers
        self.ami_managers[manager].on_event(event)

    def run(self):
        """
        Start the runner and run until halted.
        """
        self.attach_all()

        signal.signal(signal.SIGINT, self._close)

        self.loop.run_forever()

    def _close(self, signal, frame):
        """
        Clean shutdown the runner.
        """
        self.logger.info('Shutting down Cacofonisk...')
        for manager in self.ami_managers:
            manager.close()
        self.reporter.close()
        sys.exit(0)
