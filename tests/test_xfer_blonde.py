from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from tests.replaytest import ChannelEventsTestCase


class TestBlondeXfer(ChannelEventsTestCase):
    """
    Test call state notifications for blonde transfers.

    A blonde transfer (also known as semi-attended transfer) is a type of
    transfer which looks like an attended transfer, but the transferer
    doesn't wait for person C to pick up.
    """

    def test_xfer_blonde_abacbc(self):
        """
        Test blonde transfer where A initiates the transfer.
        """
        events_file = 'fixtures/xfer_blonde/xfer_blonde_abacbc.json'
        events = self.run_and_get_events(events_file)

        a_chan = SimpleChannel(
            name='SIP/150010001-00000090',
            uniqueid='f29ea68048f6-1530023922.2627',
            linkedid='f29ea68048f6-1530023922.2627',
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
            state=6,
        )

        a_chan_transferer = a_chan.replace(
            name='SIP/150010001-00000092',
            uniqueid='f29ea68048f6-1530023931.2654',
            linkedid='f29ea68048f6-1530023931.2654',
            exten='203',
        )

        b_chan = SimpleChannel(
            name='SIP/150010002-00000091',
            uniqueid='f29ea68048f6-1530023922.2635',
            linkedid='f29ea68048f6-1530023922.2627',
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
        )

        b_chan_transferring = b_chan.replace(
            exten='203',
        )

        b_chan_transferred = b_chan_transferring.replace(
            connected_line=CallerId(),
        )

        c_chan = SimpleChannel(
            name='SIP/150010003-00000093',
            uniqueid='f29ea68048f6-1530023932.2662',
            linkedid='f29ea68048f6-1530023931.2654',
            account_code='150010001',
            caller_id=CallerId(num='203'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
        )

        c_chan_transferred = c_chan.replace(
            connected_line=CallerId(num='202'),
        )

        expected_events = [
            ('on_b_dial', {
                'caller': a_chan.replace(state=4),
                'targets': [b_chan.replace(state=5)],
            }),
            ('on_up', {
                'caller': a_chan,
                'target': b_chan,
            }),
            ('on_b_dial', {
                'caller': a_chan_transferer.replace(state=4),
                'targets': [c_chan.replace(state=5)],
            }),
            ('on_blonde_transfer', {
                'caller': b_chan_transferring,
                'targets': [c_chan.replace(state=5)],
                'transferer': a_chan_transferer.replace(state=4),
            }),
            ('on_up', {
                'caller': b_chan_transferred,
                'target': c_chan_transferred,
            }),
            ('on_hangup', {
                'caller': b_chan_transferred,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_xfer_blonde_abbcac(self):
        """
        Test blonde transfer where B initiates the transfer.
        """
        events_file = 'fixtures/xfer_blonde/xfer_blonde_abbcac.json'
        events = self.run_and_get_events(events_file)

        a_chan = SimpleChannel(
            name='SIP/voipgrid-siproute-docker-00000096',
            uniqueid='f29ea68048f6-1530024929.2709',
            linkedid='f29ea68048f6-1530024929.2709',
            account_code='15001',
            caller_id=CallerId(num='+31260010001'),
            cid_calling_pres=None,
            connected_line=CallerId(name='', num=''),
            exten='+31150010001',
            state=6,
        )

        a_chan_transferred = a_chan.replace(
            exten='202',
        )

        b_chan = SimpleChannel(
            name='SIP/150010001-00000097',
            uniqueid='f29ea68048f6-1530024929.2716',
            linkedid='f29ea68048f6-1530024929.2709',
            account_code='15001',
            caller_id=CallerId(num='+31150010001'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='+31260010001'),
            exten='s',
            state=6,
        )

        b_chan_transferer = b_chan.replace(
            name='SIP/150010001-00000098',
            uniqueid='f29ea68048f6-1530024939.2753',
            linkedid='f29ea68048f6-1530024939.2753',
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
        )

        c_chan = SimpleChannel(
            name='SIP/150010002-00000099',
            uniqueid='f29ea68048f6-1530024939.2761',
            linkedid='f29ea68048f6-1530024939.2753',
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
        )

        c_chan_transferred = c_chan.replace(
            connected_line=CallerId(num='+31260010001'),
        )

        expected_events = [
            ('on_b_dial', {
                'caller': a_chan.replace(state=4),
                'targets': [b_chan.replace(state=5)],
            }),
            ('on_up', {
                'caller': a_chan,
                'target': b_chan,
            }),
            ('on_b_dial', {
                'caller': b_chan_transferer.replace(state=4),
                'targets': [c_chan.replace(state=5)],
            }),
            ('on_blonde_transfer', {
                'caller': a_chan_transferred,
                'targets': [c_chan.replace(state=5)],
                'transferer': b_chan_transferer.replace(state=4),
            }),
            ('on_up', {
                'caller': a_chan_transferred,
                'target': c_chan_transferred,
            }),
            ('on_hangup', {
                'caller': a_chan_transferred,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_xfer_blonde_reject(self):
        """
        Test blonde transfer where the transfer target rejects the call.
        """
        events_file = 'fixtures/xfer_blonde/xfer_blonde_reject.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a1',
                'targets': ['SIP/150010001-000000a2'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a1',
                'target': 'SIP/150010001-000000a2',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-000000a3',
                'targets': ['SIP/150010002-000000a4'],
            }),
            ('on_blonde_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a1',
                'targets': ['SIP/150010002-000000a4'],
                'transferer': 'SIP/150010001-000000a3',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a1',
                'reason': 'busy',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blonde_group_b(self):
        """
        Test blonde transfer where the call is transferred to a group by B.
        """
        events_file = 'fixtures/xfer_blonde/xfer_blonde_group_b.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a7',
                'targets': ['SIP/150010001-000000a8'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a7',
                'target': 'SIP/150010001-000000a8',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-000000a9',
                'targets': [
                    'SIP/150010002-000000aa',
                    'SIP/150010003-000000ab',
                ],
            }),
            ('on_blonde_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a7',
                'targets': [
                    'SIP/150010002-000000aa',
                    'SIP/150010003-000000ab',
                ],
                'transferer': 'SIP/150010001-000000a9'
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a7',
                'target': 'SIP/150010002-000000aa',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-000000a7',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blonde_group_a(self):
        """
        Test blonde transfer where the call is transferred to a group by A.
        """
        events_file = 'fixtures/xfer_blonde/xfer_blonde_group_a.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-000000ac',
                'targets': ['SIP/voipgrid-siproute-docker-000000ad'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-000000ac',
                'target': 'SIP/voipgrid-siproute-docker-000000ad',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-000000b0',
                'targets': [
                    'SIP/150010002-000000b1',
                    'SIP/150010003-000000b2',
                ],
            }),
            ('on_blonde_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-000000ad',
                'targets': [
                    'SIP/150010002-000000b1',
                    'SIP/150010003-000000b2',
                ],
                'transferer': 'SIP/150010001-000000b0',
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-000000ad',
                'target': 'SIP/150010002-000000b1',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-000000ad',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
