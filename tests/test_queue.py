from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestQueue(ChannelEventsTestCase):

    def test_queue_simple(self):
        """
        Test a successful call through a queue.
        """
        events = self.run_and_get_events('fixtures/queue/queue_simple.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'e83df36bebbe-1507019160.61',
                'caller': CallerId(code=0, number='+31150010002', is_public=True),
                'to_number': '+31150010004',
                'targets': [CallerId(code=150010001, number='+31150010004', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'e83df36bebbe-1507019160.61',
                'caller': CallerId(code=0, number='+31150010002', is_public=True),
                'to_number': '+31150010004',
                'callee': CallerId(code=150010001, number='+31150010004', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'e83df36bebbe-1507019160.61',
                'caller': CallerId(code=0, number='+31150010002', is_public=True),
                'to_number': '+31150010004',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_queue_group(self):
        """
        Test a call through a queue to a call group with multiple accounts.
        """
        events = self.run_and_get_events('fixtures/queue/queue_group.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'e83df36bebbe-1507022898.69',
                'caller': CallerId(code=0, number='+31150010002', is_public=True),
                'to_number': '+31150010004',
                'targets': [
                    CallerId(code=150010001, number='+31150010004', is_public=True),
                    CallerId(code=150010003, number='+31150010004', is_public=True),
                ],
            }),
            ('on_up', {
                'call_id': 'e83df36bebbe-1507022898.69',
                'caller': CallerId(code=0, number='+31150010002', is_public=True),
                'to_number': '+31150010004',
                'callee': CallerId(code=150010003, number='+31150010004', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'e83df36bebbe-1507022898.69',
                'caller': CallerId(code=0, number='+31150010002', is_public=True),
                'to_number': '+31150010004',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_a_cancel_hangup(self):
        """
        Test a call where A exits the queue before B can pick up.
        """
        events = self.run_and_get_events('fixtures/queue/queue_a_cancel_hangup.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1508767736.46',
                'caller': CallerId(code=150010003, name='Tom Kline', number='203', is_public=True),
                'to_number': '401',
                'targets': [CallerId(code=150010001, number='401', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1508767736.46',
                'caller': CallerId(code=150010003, name='Tom Kline', number='203', is_public=True),
                'to_number': '401',
                'reason': 'cancelled'
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_queue_attn_xfer(self):
        """
        Test an attended transfer with someone coming through a queue.
        """
        events = self.run_and_get_events('fixtures/queue/queue_attn_xfer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'e83df36bebbe-1507037906.116',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '+31150010004',
                'targets': [CallerId(code=150010002, number='+31150010004', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'e83df36bebbe-1507037906.116',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '+31150010004',
                'callee': CallerId(code=150010002, number='+31150010004', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': 'e83df36bebbe-1507037917.120',
                'caller': CallerId(code=150010002, number='202', name="Samantha Graham", is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'e83df36bebbe-1507037917.120',
                'caller': CallerId(code=150010002, number='202', name="Samantha Graham", is_public=True),
                'to_number': '203',
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_warm_transfer', {
                'new_id': 'e83df36bebbe-1507037917.120',
                'merged_id': 'e83df36bebbe-1507037906.116',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'callee': CallerId(code=150010003, number='203', is_public=True),
                'redirector': CallerId(code=150010002, number='202', name="Samantha Graham", is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'e83df36bebbe-1507037917.120',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '203',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_queue_blind_xfer(self):
        """
        Test a blind transfer with someone from a queue.
        """
        events = self.run_and_get_events('fixtures/queue/queue_blind_xfer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'e83df36bebbe-1507042413.128',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '+31150010004',
                'targets': [CallerId(code=150010002, number='+31150010004', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'e83df36bebbe-1507042413.128',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '+31150010004',
                'callee': CallerId(code=150010002, number='+31150010004', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': 'e83df36bebbe-1507042415.129',
                'caller': CallerId(code=150010002, number='+31150010004', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_cold_transfer', {
                'new_id': 'e83df36bebbe-1507042413.128',
                'merged_id': 'e83df36bebbe-1507042415.129',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
                'redirector': CallerId(code=150010002, number='+31150010004', name="", is_public=True),
                'to_number': '203',
            }),
            ('on_up', {
                'call_id': 'e83df36bebbe-1507042413.128',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '203',
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'e83df36bebbe-1507042413.128',
                'caller': CallerId(code=0, number='+31150010001', is_public=True),
                'to_number': '203',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)
