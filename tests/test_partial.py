import glob
import os

from tests.replaytest import ChannelEventsTestCase, TestReporter, BogoRunner


class TestPartial(ChannelEventsTestCase):

    def test_partial_events(self):
        """
        Test cacofonisk doesn't crash if it's attached to running Asterisk.
        """
        files = glob.glob(os.path.join(os.path.dirname(__file__), 'fixtures', '**', '*.json'))

        for filename in files:
            events = self.load_events_from_disk(filename)
            while len(events) != 0:
                events.pop(0)
                reporter = TestReporter()
                runner = BogoRunner(events=events, reporter=reporter)
                runner.run()
                assert len(runner.channel_managers) == 1
