from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestSimpleOrig(ChannelEventsTestCase):

    def test_ab_success(self):
        """Test a simple, successful call.

        202 calls 203, 203 picks up and later the call is disconnected.
        """
        events = self.run_and_get_events('fixtures/simple/ab_success.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '203',
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '203',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_ab_busy(self):
        """Test a simple call where B is busy.
        """
        events = self.run_and_get_events('fixtures/simple/ab_busy.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501851519.239',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '201',
                'targets': [CallerId(code=150010001, number='201', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501851519.239',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '201',
                'reason': 'busy'
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_ab_success_twoaccounts(self):
        """Test a simple, successful call.

        Account 260010001 using +31260010001 as outdialing number, dials
        +31150010001 which is connected to account 150010001 with internal number 201
        the call is picked up and completed successfully.
        """
        events = self.run_and_get_events('fixtures/simple/ab_success_twoclients.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '2087873f7e47-1508940720.14',
                'caller': CallerId(code=15001, number='+31260010001', is_public=True),
                'to_number': '+31150010001',
                'targets': [CallerId(code=150010001, number='+31150010001', is_public=True)],
            }),
            ('on_up', {
                'call_id': '2087873f7e47-1508940720.14',
                'caller': CallerId(code=15001, number='+31260010001', is_public=True),
                'to_number': '+31150010001',
                'callee': CallerId(code=150010001, number='+31150010001', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '2087873f7e47-1508940720.14',
                'caller': CallerId(code=15001, number='+31260010001', is_public=True),
                'to_number': '+31150010001',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expected_events)

    def test_ab_callgroup(self):
        """
        Test a simple call to a group where one phone is picked up.
        """
        events = self.run_and_get_events('fixtures/simple/ab_callgroup.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '401',
                'targets': [
                    CallerId(code=150010001, number='401', is_public=True),
                    CallerId(code=150010003, number='401', is_public=True),
                ],
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '401',
                'callee': CallerId(code=150010001, number='401', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '401',
                'reason': 'completed'
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_ab_callgroup_no_answer(self):
        """
        Test a call to a group where no target picks up.
        """
        events = self.run_and_get_events('fixtures/simple/ab_callgroup_no_answer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509355567.22',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '403',
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509355567.22',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '403',
                'reason': 'no-answer',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_a_cancel_hangup(self):
        """
        Test a call where A hangs up before B can pick up.
        """
        events = self.run_and_get_events('fixtures/simple/ab_a_cancel_hangup.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1508490698.34',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1508490698.34',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'reason': 'cancelled'
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_a_success_hangup(self):
        """
        Test a call where A hangs up after being connected to B.
        """
        events = self.run_and_get_events('fixtures/simple/ab_a_success_hangup.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1508490669.30',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1508490669.30',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1508490669.30',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)
