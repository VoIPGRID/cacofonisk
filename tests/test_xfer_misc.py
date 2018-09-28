from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from tests.replaytest import ChannelEventsTestCase


class TestMiscXfer(ChannelEventsTestCase):
    """
    Test various types of esoteric call types where the participants change.

    Currently, this class tests call pickups and call forwarding.
    """

    def test_sip_pickup(self):
        """
        Test call pickup performed with a SIP Replaces INVITE.
        """
        events = self.run_and_get_events('fixtures/xfer_misc/sip_pickup.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-0000001f',
                'targets': ['SIP/150010002-00000020'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-0000001f',
                'target': 'SIP/150010003-00000021',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-0000001f',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_star_pickup(self):
        """
        Test call pickup performed with the Pickup app in Asterisk.
        """
        events = self.run_and_get_events('fixtures/xfer_misc/star_pickup.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000022',
                'targets': ['SIP/150010002-00000023'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000022',
                'target': 'SIP/150010003-00000024',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000022',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_call_forwarding(self):
        """
        Test a call where the call is locally forwarded to another phone.
        """
        events = self.run_and_get_events(
            'fixtures/xfer_misc/call_forwarding.json')

        calling_chan = SimpleChannel(
            name='SIP/voipgrid-siproute-docker-00000016',
            uniqueid='b6093874285e-1530191379.305',
            linkedid='b6093874285e-1530191379.305',
            account_code='15001',
            caller_id=CallerId(num='+31260010001'),
            cid_calling_pres=None,
            connected_line=CallerId(),
            exten='+31150010001',
            state=6,
        )

        target_chan = SimpleChannel(
            name='SIP/150010002-00000018',
            uniqueid='b6093874285e-1530191380.328',
            linkedid='b6093874285e-1530191379.305',
            account_code='15001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='+31260010001'),
            exten='s',
            state=6,
        )

        expected_events = [
            ('on_b_dial', {
                'caller': calling_chan.replace(state=4),
                'targets': [target_chan.replace(state=5)],
            }),
            ('on_up', {
                'caller': calling_chan,
                'target': target_chan,
            }),
            ('on_hangup', {
                'caller': calling_chan,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_call_forwarding_to_group(self):
        """
        Test call forwarding where the call is forwarded to a group.
        """
        events = self.run_and_get_events(
            'fixtures/xfer_misc/call_forwarding_to_group.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000021',
                'targets': [
                    'SIP/150010002-00000023',
                    'SIP/150010003-00000024',
                ],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000021',
                'target': 'SIP/150010003-00000024',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000021',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
