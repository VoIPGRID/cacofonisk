from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from tests.replaytest import ChannelEventsTestCase


class TestBlindXfer(ChannelEventsTestCase):

    def test_xfer_blind_abbcac(self):
        """
        Test a blind transfer where B initiates the transfer.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_abbcac.json'
        events = self.run_and_get_events(events_file)

        a_chan = SimpleChannel(
            name='SIP/150010001-00000003',
            uniqueid='07b796be1962-1529998959.65',
            linkedid='07b796be1962-1529998959.65',
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
            state=6,
        )

        a_chan_transferred = a_chan.replace(
            account_code='150010002',
            caller_id=a_chan.caller_id.replace(name=''),
            exten='203',
        )

        b_chan = SimpleChannel(
            name='SIP/150010002-00000004',
            uniqueid='07b796be1962-1529998959.73',
            linkedid='07b796be1962-1529998959.65',
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
        )

        c_chan = SimpleChannel(
            name='SIP/150010003-00000005',
            uniqueid='07b796be1962-1529998966.104',
            linkedid='07b796be1962-1529998959.65',
            account_code='150010001',
            caller_id=CallerId(num='203'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='201'),
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
            ('on_blind_transfer', {
                'caller': a_chan_transferred,
                'targets': [c_chan.replace(state=5)],
                'transferer': b_chan.replace(exten='203'),
            }),
            ('on_up', {
                'caller': a_chan_transferred,
                'target': c_chan,
            }),
            ('on_hangup', {
                'caller': a_chan_transferred,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_xfer_blind_abacbc(self):
        """
        Test a blind transfer where A initiates the transfer.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_abacbc.json'
        events = self.run_and_get_events(events_file)

        a_chan = SimpleChannel(
            name='SIP/150010001-00000006',
            uniqueid='07b796be1962-1529998985.130',
            linkedid='07b796be1962-1529998985.130',
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
            state=6,
        )

        b_chan = SimpleChannel(
            name='SIP/150010002-00000007',
            uniqueid='07b796be1962-1529998985.138',
            linkedid='07b796be1962-1529998985.130',
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            state=6,
        )

        b_chan_transferred = b_chan.replace(
            exten='203',
        )

        c_chan = SimpleChannel(
            name='SIP/150010003-00000008',
            uniqueid='07b796be1962-1529998993.169',
            linkedid='07b796be1962-1529998985.130',
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='203'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='202'),
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
            ('on_blind_transfer', {
                'caller': b_chan_transferred,
                'targets': [c_chan.replace(state=5)],
                'transferer': a_chan.replace(exten='203'),
            }),
            ('on_up', {
                'caller': b_chan_transferred,
                'target': c_chan,
            }),
            ('on_hangup', {
                'caller': b_chan_transferred,
                'reason': 'completed',
            }),
        ]

        self.assertEqual(expected_events, events)

    def test_xfer_blind_a_no_answer(self):
        """
        Test a blind transfer from A where the transfer target is down.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_a_no_answer.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000012',
                'targets': ['SIP/150010002-00000013'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000012',
                'target': 'SIP/150010002-00000013',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000012',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blind_b_no_answer(self):
        """
        Test a blind transfer from B where the transfer target is down.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_b_no_answer.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000015',
                'targets': ['SIP/150010002-00000016'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000015',
                'target': 'SIP/150010002-00000016',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000015',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blind_reject(self):
        """
        Test a blind transfer from where the target rejects the transfer.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_reject.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000018',
                'targets': ['SIP/150010002-00000019'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000018',
                'target': 'SIP/150010002-00000019',
            }),
            ('on_blind_transfer', {
                'caller': 'SIP/150010001-00000018',
                'targets': ['SIP/150010003-0000001a'],
                'transferer': 'SIP/150010002-00000019',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000018',
                'reason': 'no-answer',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blind_group(self):
        """
        Test a blind transfer where the call is transferred to a group.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_group.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'targets': ['SIP/150010001-00000018'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'target': 'SIP/150010001-00000018',
            }),
            ('on_blind_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'targets': [
                    'SIP/150010002-00000019',
                    'SIP/150010003-0000001a',
                ],
                'transferer': 'SIP/150010001-00000018',
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'target': 'SIP/150010003-0000001a',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blind_group_no_answer(self):
        """
        Test a blind transfer where the call is transferred to a group.
        """
        events_file = 'fixtures/xfer_blind/xfer_blind_group_no_answer.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000023',
                'targets': ['SIP/150010001-00000024'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000023',
                'target': 'SIP/150010001-00000024',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000023',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
