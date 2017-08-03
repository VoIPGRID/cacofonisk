import os

from cacofonisk.channel import CallerId, ChannelManager
from cacofonisk.runners.file_runner import FileRunner
from cacofonisk.utils.testcases import BaseTestCase, SilentReporter


class MockChannelManager(ChannelManager):
    """
    Behave like the ChannelManager, but collect the on_b_dial and
    on_transfer events so they can be checked when the run is complete.

    Example::

        manager = MockChannelManager(reporter=some_reporter)
        for event in self.events:
            if ('*' in channelmgr.INTERESTING_EVENTS or
                    event['Event'] in channelmgr.INTERESTING_EVENTS):
                manager.on_event(event)

        received_events = manager.get_events()
        assert received_events == expected_events
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._events = []

    def get_events(self):
        return tuple(self._events)

    def on_b_dial(self, caller_channel, callee_channel, call_id):
        self._events.append({
            'event': 'on_b_dial',
            'call_id': call_id,
            'caller': caller_channel,
            'callee': callee_channel,
        })

    def on_transfer(self, redirector, party1, party2, new_id, merged_id):
        self._events.append({
            'event': 'on_transfer',
            'redirector': redirector,
            'party1': party1,
            'party2': party2,
            'new_id': new_id,
            'merged_id': merged_id,
        })

    def on_up(self, caller_channel, callee_channel, call_id):
        self._events.append({
            'event': 'on_up',
            'caller': caller_channel,
            'callee': callee_channel,
            'call_id': call_id,
        })

    def on_hangup(self, caller_channel, callee_channel, reason, call_id):
        self._events.append({
            'event': 'on_hangup',
            'caller': caller_channel,
            'callee': callee_channel,
            'reason': reason,
            'call_id': call_id,
        })


class BogoRunner(object):
    def __init__(self, events, reporter):
        self.events = events
        self.reporter = reporter
        self.channel_managers = []

    def run(self):
        channelmgr = MockChannelManager(reporter=self.reporter)
        for event in self.events:
            if ('*' in channelmgr.INTERESTING_EVENTS or
                    event['Event'] in channelmgr.INTERESTING_EVENTS):
                channelmgr.on_event(event)

        self.channel_managers.append(channelmgr)


class ChannelEventsTestCase(BaseTestCase):
    """
    Run event tests based on the JSON sample data.
    """
    maxDiff = 8192

    def events_from_tuples(cls, tuples):
        """
        Convert a list of tuples to the expected event list.

        Example::

            events = events_from_tuples((
                ('on_b_dial', (126680001, '', '201', True),
                              (126680003, '', '203', True)),
                ('on_transfer', (126680001, '', '201', True),
                                (126680002, '', '202', True),
                                (126680003, '', '203', True)),
            ))
            events == tuple([
                {'event': 'on_b_dial',
                 'caller': CallerId(126680001, '', '201', True),
                 'callee': CallerId(126680003, '', '203', True)},
                {'event': 'on_transfer',
                 'redirector': CallerId(126680001, '', '201', True),
                 'party1': CallerId(126680002, '', '202', True),
                 'party2': CallerId(126680003, '', '203', True)},
            ])

        Args:
            tuples: An iterable with iterables, see example.

        Returns:
            tuple: A tuple of dictionaries, see example.
        """
        results = []

        for data in tuples:
            event_name, event_data = data
            event_data['event'] = event_name
            results.append(event_data)

        return tuple(results)

    def events_from_jdictlist(cls, jdictlist):
        """
        Convert a list of dictionaries to the expected event list.

        The dictionaries are expected to be passed from a json file.
        This method ensures that the caller/callee/etc parameters are
        converted to CallerId objects.

        Example::

            events = events_from_jdictlist([
                "A few comments are allowed",
                "here and there",
                {'event': 'on_b_dial',
                 'caller': [126680001, '', '201', True],
                 'callee': [126680003, '', '203', True]},

                "And a few more comments",
                {'event': 'on_transfer',
                 'redirector': [126680001, '', '201', True],
                 'party1': [126680002, '', '202', True],
                 'party2': [126680003, '', '203', True]},
            ])
            events == tuple([
                {'event': 'on_b_dial',
                 'caller': CallerId(126680001, '', '201', True),
                 'callee': CallerId(126680003, '', '203', True)},
                {'event': 'on_transfer',
                 'redirector': CallerId(126680001, '', '201', True),
                 'party1': CallerId(126680002, '', '202', True),
                 'party2': CallerId(126680003, '', '203', True)},
            ])

        Args:
            jdictlist: A list of dictionaries, see example.

        Returns:
            tuple: A tuple of dictionaries, see example.
        """
        ret = []

        for event_dict in jdictlist:
            if isinstance(event_dict, str):
                pass  # ignore comment-strings
            elif isinstance(event_dict, dict):
                new_dict = event_dict.copy()
                for key, value in new_dict.items():
                    if isinstance(value, list):
                        new_dict[key] = CallerId(*value)
                ret.append(new_dict)
            else:
                raise NotImplementedError()

        return tuple(ret)

    def run_and_get_events(self, filename, channel_manager_class=MockChannelManager):
        absolute_path =os.path.join(os.path.dirname(__file__), filename)
        reporter = SilentReporter()
        runner = FileRunner([absolute_path],
                            reporter=reporter,
                            channel_manager_class=channel_manager_class)
        runner.run()
        assert len(runner.channel_managers) == 1
        channelmgr = runner.channel_managers[0]
        return tuple(channelmgr.get_events())

    def run_and_get_events_partial(self, filename):
        """
        Run and get the events with one line less, each time it is run.

        Args:
            filename (str): File with events in json format.
        Yields:
            A tuple of the channelmanager's output of the partial log.
        """
        reporter = SilentReporter()
        events = self.load_events_from_disk(filename)
        while len(events) != 0:
            events.pop(0)
            runner = BogoRunner(events=events, reporter=reporter)
            runner.run()
            assert len(runner.channel_managers) == 1
            channelmgr = runner.channel_managers[0]
            yield tuple(channelmgr.get_events())
