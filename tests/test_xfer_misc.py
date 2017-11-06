from cacofonisk.callerid import CallerId
from tests.replaytest import ChannelEventsTestCase


class TestMiscXfer(ChannelEventsTestCase):
    """
    Test various types of esoteric call types where the participants change.

    Currently, this class tests call pickups and call forwarding.
    """

    def test_call_pickup(self):
        """
        Test a call pickup transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_misc/call_pickup.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1445001221.106',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'targets': [CallerId(code=123450002, number='202', is_public=True)],
            }),
            ('on_forward', {
                'call_id': 'vgua0-dev-1445001221.106',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'loser': CallerId(code=123450002, number='202', is_public=True),
                'targets': [CallerId(code=123450003, number='202', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1445001221.106',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'callee': CallerId(code=123450003, number='202', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_call_forwarding(self):
        """
        Test a call where the call is locally forwarded to another phone.
        """
        events = self.run_and_get_events('fixtures/xfer_misc/call_forwarding.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1444992672.12',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'targets': [CallerId(code=123450002, number='202', is_public=True)],
            }),
            ('on_forward', {
                'call_id': 'vgua0-dev-1444992672.12',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'loser': CallerId(code=123450002, number='202', is_public=True),
                'targets': [CallerId(code=123450003, number='203', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1444992672.12',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'callee': CallerId(code=123450003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1444992672.12',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'callee': CallerId(code=123450003, number='202', is_public=True),
                'reason': 'completed',
            })
        ))

        self.assertEqual(expected_events, events)
