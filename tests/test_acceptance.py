from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestCallAcceptance(ChannelEventsTestCase):

    def test_accepted(self):
        """Test an accepted call via callgroup.

        +315080xxxxx dials calls +31853xxxxxx,
        +31612345678 is the configured fixed destination,
        +31612345678 picks up, accepts the call by pressing 1,
        Later the call is disconnected.
        """
        events = self.run_and_get_events('fixtures/acceptance/accept_accepted.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1506952916.1769',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'targets': [CallerId(code=0, number='+31612345678', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1506952916.1769',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'callee': CallerId(code=12668, number='+31612345678', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1506952916.1769',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_multiple_accepted(self):
        """Test an accepted call via callgroup with two fixed destinations.

        +315080xxxxx dials +31853xxxxxx,
        callgroup containing +31613925xxx and +31508012345 is called,
        +31508012345 picks up and accepts the call.
        Later the call is disconnected.
        """
        events = self.run_and_get_events('fixtures/acceptance/accept_multiple_accepted.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1507798662.2063',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'targets': [
                    CallerId(code=0, number='+31508012345', is_public=True),
                    CallerId(code=0, number='+31613925xxx', is_public=True),
                ],
            }),
            # +31508012345 picks up, +31613925xxx keeps ringing until 1 is pressed.
            ('on_up', {
                'call_id': 'ua0-acc-1507798662.2063',
                'to_number': '+31853xxxxxx',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'callee': CallerId(code=12668, number='+31508012345', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1507798662.2063',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_multiple_complexaccepted(self):
        """Test an accepted call via callgroup with two fixed destinations.

        +315080xxxxx dials +31853xxxxxx,
        callgroup containing +31613925xxx and +31508012345 is called,
        +31613925xxx picks up but does not press 1 to accept,
        +31508012345 picks up and accepts the call,
        Later the call is disconnected.
        """
        events = self.run_and_get_events('fixtures/acceptance/accept_multiple_complexaccepted.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1507800454.2085',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'targets': [
                    CallerId(code=0, number='+31508012345', is_public=True),
                    CallerId(code=0, number='+31613925xxx', is_public=True),
                ],
            }),
            # +31613925xxx also picks up, and does accept
            ('on_up', {
                'call_id': 'ua0-acc-1507800454.2085',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'callee': CallerId(code=12668, number='+31613925xxx', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1507800454.2085',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_notaccepted(self):
        """Test a not accepted but answered call.

        +31613925xxx picks up, does NOT accept the call, and hangs up.
        """
        events = self.run_and_get_events('fixtures/acceptance/accept_notaccepted.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1507621393.1940',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'targets': [CallerId(code=0, number='+31613925xxx', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1507621393.1940',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'reason': 'no-answer',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_deny(self):
        """Test a denied call.

        +315080xxxxx calls +31613925xxx and +31613925xxx refuses the call.
        """
        events = self.run_and_get_events('fixtures/acceptance/accept_deny.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1507624765.2057',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'targets': [CallerId(code=0, number='+31613925xxx', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1507624765.2057',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'reason': 'no-answer',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_timeout(self):
        """Test a callgroup with acceptance, nobody picks up.

        +315080xxxxx calls +31613925xxx and does not pick up within the time.
        """
        events = self.run_and_get_events('fixtures/acceptance/accept_timeout.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1507624058.2045',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'targets': [CallerId(code=0, number='+31613925xxx', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1507624058.2045',
                'caller': CallerId(code=12668, number='+315080xxxxx', is_public=True),
                'to_number': '+31853xxxxxx',
                'reason': 'no-answer',
            }),
        ))

        self.assertEqual(expected_events, events)
