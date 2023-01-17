from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from tests.replaytest import ChannelEventsTestCase

class TestQueue(ChannelEventsTestCase):

    def test_queue_simple(self):
        """
        Test a simple call through a queue to a single account.
        """
        fixture_file = 'fixtures/queue/queue_simple.json'
        events = self.run_and_get_events(fixture_file)

        caller = SimpleChannel(
            name='SIP/voipgrid-siproute-docker-00000025',
            uniqueid='195176c06ab8-1529939196.518',
            linkedid='195176c06ab8-1529939196.518',
            account_code='15001',
            caller_id=CallerId(num='+31150010001'),
            cid_calling_pres=None,
            connected_line=CallerId(),
            exten='+31150010004',
            state=6,
        )

        target = SimpleChannel(
            name='SIP/150010002-00000026',
            uniqueid='195176c06ab8-1529939198.548',
            linkedid='195176c06ab8-1529939196.518',
            account_code='15001',
            caller_id=CallerId(num='+31150010004'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='+31150010001'),
            exten='s',
            state=6,
        )

        expected_events = [
            ('on_b_dial', {
                'caller': caller,
                'targets': [target.replace(state=5)],
            }),
            ('on_up', {
                'caller': caller,
                'target': target,
            }),
            ('on_hangup', {
                'caller': caller,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_queue_group(self):
        """
        Test a simple call through a queue to a group.
        """
        fixture_file = 'fixtures/queue/queue_group.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-0000001b',
                'targets': [
                    'SIP/150010002-0000001d',
                    'SIP/150010003-0000001c',
                ],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-0000001b',
                'target': 'SIP/150010002-0000001d',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-0000001b',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_queue_a_cancel(self):
        """
        Test a call where A exits the queue before B can pick up.
        """
        events = self.run_and_get_events('fixtures/queue/queue_a_cancel.json')
        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000019',
                'targets': [
                    'SIP/150010002-0000001a',
                ],
            }),
            ('on_queue_caller_abandon', {
                'caller': 'SIP/voipgrid-siproute-docker-00000019',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000019',
                'reason': 'completed',
            }),
        ]
        self.assertEqualChannels(expected_events, events)

    def test_queue_attn_xfer(self):
        """
        Test an attended transfer with someone coming through a queue.
        """
        events = self.run_and_get_events('fixtures/queue/queue_attn_xfer.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000087',
                'targets': ['SIP/150010001-00000088'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000087',
                'target': 'SIP/150010001-00000088',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000089',
                'targets': ['SIP/150010002-0000008a'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000089',
                'target': 'SIP/150010002-0000008a',
            }),
            ('on_attended_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-00000087',
                'target': 'SIP/150010002-0000008a',
                'transferer': 'SIP/150010001-00000089',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000087',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_queue_blind_xfer(self):
        """
        Test a blind transfer with someone from a queue.
        """
        events = self.run_and_get_events('fixtures/queue/queue_blind_xfer.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-0000008d',
                'targets': ['SIP/150010001-0000008e'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-0000008d',
                'target': 'SIP/150010001-0000008e',
            }),
            ('on_blind_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-0000008d',
                'targets': ['SIP/150010002-0000008f'],
                'transferer': 'SIP/150010001-0000008e',
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-0000008d',
                'target': 'SIP/150010002-0000008f',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-0000008d',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
