from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestFixed(ChannelEventsTestCase):

    def test_incoming(self):
        """Test an incomming call from outside the platform.

        +31853030900 dials +31853030904, dialplan causes 203 to be dialed.
        """
        events = self.run_and_get_events('fixtures/fixed/fixed_incomming_success.json')
        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '2087873f7e47-1509101015.24',
                'caller': CallerId(code=15001, number='+31853030900', is_public=True),
                'to_number': '+31853030904',
                'targets': [CallerId(code=150010003, number='+31853030904', is_public=True)],
            }),
            ('on_up', {
                'call_id': '2087873f7e47-1509101015.24',
                'caller': CallerId(code=15001, number='+31853030900', is_public=True),
                'to_number': '+31853030904',
                'callee': CallerId(code=150010003, number='+31853030904', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '2087873f7e47-1509101015.24',
                'caller': CallerId(code=15001, number='+31853030900', is_public=True),
                'to_number': '+31853030904',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_outbound(self):
        """
        Test a simple outbound call.
        """
        events = self.run_and_get_events('fixtures/fixed/fixed_outbound_success.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1513784375.1916',
                'caller': CallerId(code=126680010, number='+31853030900', is_public=True),
                'targets': [CallerId(number='+31508009000', is_public=True)],
                'to_number': '0508009000',
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1513784375.1916',
                'caller': CallerId(code=126680010, number='+31853030900', is_public=True),
                'callee': CallerId(number='+31508009000', is_public=True),
                'to_number': '0508009000',
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1513784375.1916',
                'caller': CallerId(code=126680010, number='+31853030900', is_public=True),
                'to_number': '0508009000',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_fixed(self):
        """Test an incomming call with fixed destination.

        +31853030900 dials +31853030904, dialplan dials fixed destiation +31613925xxx.
        """
        events = self.run_and_get_events('fixtures/fixed/fixed_both_success.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '2087873f7e47-1509103867.32',
                'caller': CallerId(code=15001, number='+31853030900', is_public=True),
                'to_number': '+31853030904',
                'targets': [CallerId(code=0, number='+31613925xxx', is_public=True)],
            }),
            ('on_up', {
                'call_id': '2087873f7e47-1509103867.32',
                'caller': CallerId(code=15001, number='+31853030900', is_public=True),
                'to_number': '+31853030904',
                'callee': CallerId(code=0, number='+31613925xxx', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '2087873f7e47-1509103867.32',
                'caller': CallerId(code=15001, number='+31853030900', is_public=True),
                'to_number': '+31853030904',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)
