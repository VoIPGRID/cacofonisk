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
                'to_number': '202',
                'targets': [CallerId(code=123450002, number='202', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1445001221.106',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'to_number': '202',
                'callee': CallerId(code=123450003, number='202', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1445001221.106',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'to_number': '202',
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
                'to_number': '202',
                'targets': [CallerId(code=123450003, number='203', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1444992672.12',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'to_number': '202',
                'callee': CallerId(code=123450003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1444992672.12',
                'caller': CallerId(code=123450001, name='Alice', number='201', is_public=True),
                'to_number': '202',
                'reason': 'completed',
            })
        ))

        self.assertEqual(expected_events, events)

    def test_call_forwarding_to_group(self):
        """
        Test call forwarding where the call is forwarded to a group.
        """
        events = self.run_and_get_events('fixtures/xfer_misc/call_forwarding_to_group.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1509629983.1135',
                'caller': CallerId(number='+31508009000', is_public=True),
                'to_number': '+31853030903',
                'targets': [
                    CallerId(code=126680023, name='', number='402', is_public=True),
                    CallerId(code=126680024, name='', number='402', is_public=True),
                ],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1509629983.1135',
                'caller': CallerId(number='+31508009000', is_public=True),
                'to_number': '+31853030903',
                'callee': CallerId(code=126680024, name='', number='402', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1509629983.1135',
                'caller': CallerId(number='+31508009000', is_public=True),
                'to_number': '+31853030903',
                'reason': 'completed',
            })
        ))

        self.assertEqual(events, expected_events)

    def test_call_forwarding_to_from_group(self):
        """
        Test call to a group where member forwards the call to another group.
        """
        events = self.run_and_get_events('fixtures/xfer_misc/call_forwarding_to_from_group.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1509631559.1176',
                'caller': CallerId(number='+31612345678', is_public=True),
                'to_number': '+31853030903',
                'targets': [
                    CallerId(code=126680010, number='+31853030903', is_public=True),
                ],
            }),
            # Due to how the channel gathering works, you get two dial events,
            # one for the first hop where the phone in the first call group
            # will ring, and a second one where all the phones to which the
            # call was forwarded will ring.
            ('on_b_dial', {
                'call_id': 'ua0-acc-1509631559.1176',
                'caller': CallerId(number='+31612345678', is_public=True),
                'to_number': '+31853030903',
                'targets': [
                    CallerId(code=126680010, number='+31853030903', is_public=True),
                    CallerId(code=126680023, number='402', is_public=True),
                    CallerId(code=126680024, number='402', is_public=True),
                ],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1509631559.1176',
                'caller': CallerId(number='+31612345678', is_public=True),
                'to_number': '+31853030903',
                'callee': CallerId(code=126680024, number='402', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1509631559.1176',
                'caller': CallerId(number='+31612345678', is_public=True),
                'to_number': '+31853030903',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expected_events)
