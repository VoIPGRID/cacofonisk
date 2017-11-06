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
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, number='203', is_public=True),
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
                'targets': [CallerId(code=150010001, number='201', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501851519.239',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='201', is_public=True),
                'reason': 'busy'
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_ab_acceptance(self):
        """Test a simple, successful via callgroup with call acceptance.

        +315080xxxxx calls +31612345678 picks up, accepts the call by pressing 1, and later the call is disconnected.
        """
        events = self.run_and_get_events('fixtures/simple/ab_acceptance.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1506952916.1769',
                'caller': CallerId(code=0, name='', number='+315080xxxxx', is_public=True),
                'targets': [CallerId(code=0, name='', number='+31612345678', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1506952916.1769',
                'caller': CallerId(code=0, name='', number='+315080xxxxx', is_public=True),
                'callee': CallerId(code=0, name='', number='+31612345678', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1506952916.1769',
                'caller': CallerId(code=0, name='', number='+315080xxxxx', is_public=True),
                'callee': CallerId(code=0, name='', number='+31853xxxxxx', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expected_events)

    def test_ab_noacceptance(self):
        """Test a simple, successful via callgroup with call acceptance.

        +315080xxxxx calls +31613925xxx picks up, does NOT accept the call, and later the call is disconnected.
        """
        events = self.run_and_get_events('fixtures/simple/ab_noacceptance.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1507621393.1940',
                'caller': CallerId(code=0, name='', number='+315080xxxxx', is_public=True),
                'targets': [CallerId(code=0, name='', number='+31613925xxx', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1507621393.1940',
                'caller': CallerId(code=0, name='', number='+315080xxxxx', is_public=True),
                'callee': CallerId(code=0, name='', number='+31613925xxx', is_public=True),
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
                'targets': [
                    CallerId(code=150010001, number='401', is_public=True),
                    CallerId(code=150010003, number='401', is_public=True),
                ],
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='401', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='401', is_public=True),
                'reason': 'completed'
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_ab_callgroup_failure(self):
        """
        Test a call to a group where no target picks up.
        """
        events = self.run_and_get_events('fixtures/simple/ab_callgroup_failure.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509355567.22',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509355567.22',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                # TODO: Decide whether this callee and reason is OK.
                # With a call with multiple dials, the callee and reason are
                # taken from the last B to hang up. This may not be desirable.
                # Instead, you could remove the callees from hangups entirely
                # and use some other information to determine a reason (based
                # on whether the call was picked up, for example).
                'callee': CallerId(code=150010003, number='403', is_public=True),
                'reason': 'rejected',
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
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1508490698.34',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'callee': CallerId(code=150010004, number='204', is_public=True),
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
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1508490669.30',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1508490669.30',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'callee': CallerId(code=150010004, number='204', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)
