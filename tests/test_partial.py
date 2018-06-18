import glob
import logging
import os

from tests.replaytest import BogoRunner, ChannelEventsTestCase, TestReporter


class TestPartial(ChannelEventsTestCase):

    def setUp(self):
        """
        Disable log output.

        Disable log output because missing channels/bridges create A LOT of
        log output.
        """
        logging.disable(logging.WARN)

    def tearDown(self):
        """
        Re-enable logging.
        """
        logging.disable(logging.NOTSET)

    def test_partial_events(self):
        """
        Test cacofonisk doesn't crash if it's attached to running Asterisk.
        """
        files = glob.glob(os.path.join(
            os.path.dirname(__file__),
            'fixtures', '**', '*.json'
        ))

        for filename in files:
            events = self.load_events_from_disk(filename)
            events = list(filter(lambda e: e['Event'] not in ('VarSet', 'Newexten'), events))
            while len(events) != 0:
                events.pop(0)
                reporter = TestReporter()
                runner = BogoRunner(events=events, reporter=reporter)
                runner.run()
                assert len(runner.channel_managers) == 1
