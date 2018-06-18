from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from .replaytest import ChannelEventsTestCase


class TestAttnXfer(ChannelEventsTestCase):
    def test_xfer_abacbc(self):
        """
        Test attended transfer where A transfers B to C.

        First of all, we need to get notifications that calls are being
        made:
        - 201 (126680001) calls 202
        - 201 calls 203 (126680003)

        Secondly, we need notifications that an (attended) transfer has
        happened:
        - 201 joins the other channels (202 <--> 203)
        """
        events_file = 'fixtures/xfer_attended/xfer_abacbc.json'
        events = self.run_and_get_events(events_file)

        a_chan = SimpleChannel(
            name='SIP/150010001-00000028',
            uniqueid='195176c06ab8-1529941216.590',
            linkedid='195176c06ab8-1529941216.590',
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
            state=6,
        )

        a_chan_3pcc = a_chan.replace(
            name='SIP/150010001-0000002a',
            uniqueid='195176c06ab8-1529941225.617',
            linkedid='195176c06ab8-1529941225.617',
            exten='203',
        )

        b_chan = SimpleChannel(
            name='SIP/150010002-00000029',
            uniqueid='195176c06ab8-1529941216.598',
            linkedid='195176c06ab8-1529941216.590',
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
        )

        b_chan_transferred = b_chan.replace(exten='202')

        c_chan = SimpleChannel(
            name='SIP/150010003-0000002b',
            uniqueid='195176c06ab8-1529941225.625',
            linkedid='195176c06ab8-1529941225.617',
            account_code='150010001',
            caller_id=CallerId(num='203'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
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
                'caller': a_chan_3pcc.replace(state=4),
                'targets': [c_chan.replace(state=5)],
            }),
            ('on_up', {
                'caller': a_chan_3pcc,
                'target': c_chan,
            }),
            ('on_attended_transfer', {
                'caller': b_chan_transferred,
                'target': c_chan,
                'transferer': a_chan_3pcc,
            }),
            ('on_hangup', {
                'caller': b_chan_transferred,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_xfer_abbcac(self):
        """
        Test attended transfer where B transfers A to C.

        First of all, we need to get notifications that calls are being
        made:
        - +31501234567 calls 201 (126680001)
        - 201 calls 202

        Secondly, we need notifications that an (attended) transfer has
        happened:
        - 201 joins the other channels (+31501234567 <--> 202)
        """
        events_file = 'fixtures/xfer_attended/xfer_abbcac.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-0000002c',
                'targets': ['SIP/150010002-0000002d'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-0000002c',
                'target': 'SIP/150010002-0000002d',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010002-0000002e',
                'targets': ['SIP/150010003-0000002f'],
            }),
            ('on_up', {
                'caller': 'SIP/150010002-0000002e',
                'target': 'SIP/150010003-0000002f',
            }),
            ('on_attended_transfer', {
                'caller': 'SIP/150010001-0000002c',
                'target': 'SIP/150010003-0000002f',
                'transferer': 'SIP/150010002-0000002e',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-0000002c',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_abbcac_anonymous(self):
        """
        Test that an attended transfer where the caller is anonymous works.
        """
        events_file = 'fixtures/xfer_attended/xfer_abbcac_anon.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000027',
                'targets': ['SIP/150010001-00000028'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000027',
                'target': 'SIP/150010001-00000028',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000029',
                'targets': ['SIP/150010003-0000002a'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000029',
                'target': 'SIP/150010003-0000002a',
            }),
            ('on_attended_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-00000027',
                'target': 'SIP/150010003-0000002a',
                'transferer': 'SIP/150010001-00000029',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000027',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

        # Check the privacy flag was set correctly before and after the
        # transfer.
        self.assertEqual(
            '33 (Presentation Prohibited, Passed Screen)',
            events[0][1]['caller'].cid_calling_pres,
        )

        self.assertEqual(
            '33 (Presentation Prohibited, Passed Screen)',
            events[4][1]['caller'].cid_calling_pres,
        )

    def test_xfer_abcbac(self):
        """
        Test attn transfer where A and C call B, and B transfers them together.
        """
        events_file = 'fixtures/xfer_attended/xfer_abcbac.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010002-0000003c',
                'targets': ['SIP/150010001-0000003d'],
            }),
            ('on_up', {
                'caller': 'SIP/150010002-0000003c',
                'target': 'SIP/150010001-0000003d',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010003-0000003e',
                'targets': ['SIP/150010001-0000003f'],
            }),
            ('on_up', {
                'caller': 'SIP/150010003-0000003e',
                'target': 'SIP/150010001-0000003f',
            }),
            ('on_attended_transfer', {
                'caller': 'SIP/150010003-0000003e',
                'target': 'SIP/150010002-0000003c',
                'transferer': 'SIP/150010001-0000003d',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010003-0000003e',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
