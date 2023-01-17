from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from tests.replaytest import ChannelEventsTestCase


class TestMobile(ChannelEventsTestCase):

    def test_simple_mobile(self):
        """
        Test a call from external which is routed to another number.
        """
        events_file = 'fixtures/mobile/simple_mobile.json'
        events = self.run_and_get_events(events_file)

        caller = SimpleChannel(
            name='SIP/voipgrid-siproute-docker-00000036',
            uniqueid='f29ea68048f6-1530017224.892',
            linkedid='f29ea68048f6-1530017224.892',
            account_code='15001',
            caller_id=CallerId(num='+31150010001'),
            cid_calling_pres=None,
            connected_line=CallerId(),
            exten='+31150010004',
            state=6,
        )

        target = SimpleChannel(
            name='SIP/voipgrid-siproute-docker-00000037',
            uniqueid='f29ea68048f6-1530017224.905',
            linkedid='f29ea68048f6-1530017224.892',
            account_code='15001',
            caller_id=CallerId(num='+31260010001'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='+31150010001'),
            exten='s',
            state=6,
        )

        expected_events = [
            ('on_b_dial', {
                'caller': caller.replace(state=4),
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

    def test_acceptance_simple(self):
        """
        Test a call routed to another number with call acceptance.

        Call Acceptance is a feature where the called channel first needs to
        complete a DTMF challenge in order to verify the call was picked up by
        a human (and not voicemail).
        """
        events_file = 'fixtures/mobile/acceptance_simple.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000048',
                'targets': ['SIP/voipgrid-siproute-docker-00000049'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000048',
                'target': 'SIP/voipgrid-siproute-docker-00000049',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000048',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_acceptance_reject(self):
        """
        Test call acceptance where target does not accept call.
        """
        events_file = 'fixtures/mobile/acceptance_reject.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000063',
                'targets': ['SIP/voipgrid-siproute-docker-00000064'],
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000063',
                'reason': 'no-answer',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_acceptance_group_pickup(self):
        """
        Test call acceptance to group with call acceptance and timeout.

        In this example, both targets are picked up, but only one can complete
        call confirmation. The other target is hung up by Asterisk.
        """
        events_file = 'fixtures/mobile/acceptance_group_pickup.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000069',
                'targets': [
                    'SIP/voipgrid-siproute-docker-0000006a',
                    'SIP/voipgrid-siproute-docker-0000006c',
                ],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000069',
                'target': 'SIP/voipgrid-siproute-docker-0000006c',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000069',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_acceptance_group_reject(self):
        """
        Test call acceptance to a group with call acceptance and reject.
        """
        events_file = 'fixtures/mobile/acceptance_group_reject.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-00000072',
                'targets': [
                    'SIP/voipgrid-siproute-docker-00000073',
                    'SIP/voipgrid-siproute-docker-00000074',
                ],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-00000072',
                'target': 'SIP/voipgrid-siproute-docker-00000073',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000072',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_acceptance_timeout(self):
        """
        Test call acceptance to a group with call acceptance and reject.
        """
        events_file = 'fixtures/mobile/acceptance_timeout.json'
        events = self.run_and_get_events(events_file)

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-0000007b',
                'targets': ['SIP/voipgrid-siproute-docker-0000007c'],
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-0000007b',
                'reason': 'no-answer',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
