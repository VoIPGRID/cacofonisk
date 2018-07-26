from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from .replaytest import ChannelEventsTestCase


class TestSimple(ChannelEventsTestCase):

    def test_ab_success_a_hangup(self):
        """
        Test a simple, successful call where A hangs up.
        """
        fixture_file = 'fixtures/simple/ab_success_a_hangup.json'
        events = self.run_and_get_events(fixture_file)

        calling_chan = SimpleChannel(
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
            linkedid='195176c06ab8-1529936170.42',
            name='SIP/150010001-00000004',
            state=6,
            uniqueid='195176c06ab8-1529936170.42',
        )

        target_chan = SimpleChannel(
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            linkedid='195176c06ab8-1529936170.42',
            name='SIP/150010002-00000005',
            state=6,
            uniqueid='195176c06ab8-1529936170.50',
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

    def test_ab_success_b_hangup(self):
        """
        Test a simple, successful call where B hangs up.
        """
        fixture_file = 'fixtures/simple/ab_success_b_hangup.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000013',
                'targets': ['SIP/150010002-00000014'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000013',
                'target': 'SIP/150010002-00000014',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000013',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ab_success_twoclients(self):
        """
        Test a simple, successful call with calls through a proxy.

        Account 260010001 using +31260010001 as outdialing number, dials
        +31150010001 which is connected to account 150010001 with internal
        number 201 the call is picked up and completed successfully.
        """
        fixture_file = 'fixtures/simple/ab_success_twoclients.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/260010001-00000015',
                'targets': ['SIP/voipgrid-siproute-docker-00000016'],
            }),
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'targets': ['SIP/150010001-00000018'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'target': 'SIP/150010001-00000018',
            }),
            ('on_up', {
                'caller': 'SIP/260010001-00000015',
                'target': 'SIP/voipgrid-siproute-docker-00000016',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000017',
                'reason': 'completed',
            }),
            ('on_hangup', {
                'caller': 'SIP/260010001-00000015',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ab_reject(self):
        """
        Test a simple call where B rejects the call.
        """
        fixture_file = 'fixtures/simple/ab_reject.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000008',
                'targets': ['SIP/150010002-00000009'],
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000008',
                'reason': 'busy',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ab_dnd(self):
        """
        Test a simple call where B is set to Do Not Disturb.
        """
        fixture_file = 'fixtures/simple/ab_dnd.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_hangup', {
                'caller': 'SIP/150010001-00000006',
                'reason': 'busy',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ab_a_cancel_hangup(self):
        """
        Test a call where A hangs up before B can pick up.
        """
        fixture_file = 'fixtures/simple/ab_a_cancel.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000002',
                'targets': ['SIP/150010002-00000003'],
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000002',
                'reason': 'cancelled',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ab_callgroup(self):
        """
        Test a simple call to a group where one phone is picked up.
        """
        fixture_file = 'fixtures/simple/ab_callgroup.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-0000000d',
                'targets': [
                    'SIP/150010002-0000000e',
                    'SIP/150010003-0000000f',
                ],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-0000000d',
                'target': 'SIP/150010002-0000000e',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-0000000d',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ab_callgroup_no_answer(self):
        """
        Test a call to a group where no target picks up.
        """
        fixture_file = 'fixtures/simple/ab_callgroup_no_answer.json'
        events = self.run_and_get_events(fixture_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000010',
                'targets': [
                    'SIP/150010002-00000012',
                    'SIP/150010003-00000011',
                ],
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000010',
                'reason': 'no-answer',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
