from .replaytest import ChannelEventsTestCase


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

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000090',
                'targets': ['SIP/150010002-00000091'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000090',
                'target': 'SIP/150010002-00000091',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000092',
                'targets': ['SIP/150010003-00000093'],
            }),
            ('on_blonde_transfer', {
                'caller': 'SIP/150010002-00000091',
                'targets': ['SIP/150010003-00000093'],
                'transferer': 'SIP/150010001-00000092',
            }),
            ('on_up', {
                'caller': 'SIP/150010002-00000091',
                'target': 'SIP/150010003-00000093',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010002-00000091',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_xfer_blonde_abbcac(self):
        """
        Test blonde transfer where B initiates the transfer.
        """
        events_file = 'fixtures/xfer_blonde/xfer_blonde_abbcac.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000096',
                'targets': ['SIP/150010001-00000097'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000096',
                'target': 'SIP/150010001-00000097',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000098',
                'targets': ['SIP/150010002-00000099'],
            }),
            ('on_blonde_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-00000096',
                'targets': ['SIP/150010002-00000099'],
                'transferer': 'SIP/150010001-00000098',
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000096',
                'target': 'SIP/150010002-00000099',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000096',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

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
