import os
from json import load

from .replaytest import ChannelEventsTestCase


class ExampleReplayLogCollector(type):
    """
    The ExampleReplayLogCollector is a class creator that reads all files in the examples/ subdirectory, and creates
    test methods based on *.events.json files found there.

    For example; in the examples/ directory, these files exist::

        AttnAbAcBcXferTestCase.events.json
        AttnAbAcBcXferTestCase.replay.json

    The collector will add a new method to the created calls called
    ``test_AttnAbAcBcXferTestCase()`` which -- when tested -- plays the
    replay log ``AttnAbAcBcXferTestCase.replay.json`` and compares the
    event output with the events found in
    ``AttnAbAcBcXferTestCase.events.json``.

    The replay log is formatted like a replay log should be::

        [
          {"Status": "Fully Booted", "Event": "FullyBooted",
           "Privilege": "system,all", "content": ""},
        ...

    The event log is formatted for consumption by events_from_jdictlist::

        [
          "on_b_dial: A -> B",
          {"event": "on_b_dial",
           "caller": [126680001, "", "201", true],
           "callee": [126680002, "", "202", true]},
          ...

    Usage::

        class MyExampleReplayLogsTestCase(
                ChannelEventsTestCase,
                metaclass=ExampleReplayLogCollector):
            pass
    """
    def __new__(cls, name, bases, classdict):
        class_ = type.__new__(cls, name, bases, classdict)

        for (name, method) in cls.create_tests_from_examples_dir():
            setattr(class_, name, method)

        return class_

    @classmethod
    def get_examples_dir(cls):
        return os.path.join(os.path.dirname(__file__), 'examples')

    @classmethod
    def create_tests_from_examples_dir(cls):
        suffix = '.events.json'
        path = cls.get_examples_dir()
        replay_events = [i for i in os.listdir(path) if i.endswith(suffix)]
        ret = []

        for filename in replay_events:
            prefix = filename[0:-len(suffix)]

            name = prefix
            log = os.path.join(path, prefix + '.replay.json')
            event = os.path.join(path, filename)  # .events.json

            ret.append(cls.create_test_from_replay(name, log, event))

            ret.append(cls.create_partial_tests_from_replay(name, log, event))

        return ret

    @classmethod
    def create_test_from_replay(cls, name, log, event):
        # Call it _test_closure_for_several_tests because the __name__
        # change below is not reflected in the backtrace. This name
        # should clear up any confusion.
        def _test_closure_for_several_tests(self):
            with open(event) as eventfile:
                expecteds = load(eventfile)
            expecteds = self.events_from_jdictlist(expecteds)
            events = self.run_and_get_events(log)
            self.assertEqual(events, expecteds)

        name = 'test_{}'.format(name)  # prefix name with "test_"
        _test_closure_for_several_tests.__name__ = name
        return name, _test_closure_for_several_tests

    @classmethod
    def create_partial_tests_from_replay(cls, name, log, event):
        """
        Simulate connecting to running asterisken by feeding a partial test
        """
        def _test_closure_for_partial_log(self):
            events_lists = [l for l in self.run_and_get_events_partial(log)]
        name = 'test_partial_{}'.format(name)  # prefix name with "test_partial_"
        _test_closure_for_partial_log.__name__ = name
        return name, _test_closure_for_partial_log


class TestExampleReplayLogs(
        ChannelEventsTestCase,
        metaclass=ExampleReplayLogCollector):
    """
    Tests all the *.events.json files in the examples/ subdirectory.

    You don't see it, but the ExampleReplayLogCollector creates test_*
    methods on this TestCase class, one per events file.
    """
    pass
