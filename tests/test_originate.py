from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from tests.replaytest import ChannelEventsTestCase


class TestOriginate(ChannelEventsTestCase):

    def test_ctd_account_account(self):
        """
        Click-to-dial call between a phoneaccount and an internal number.

        In this scenario:
        1. 201 is dialed,
        2. 201 picks up,
        3. 202 is dialed
        4. 202 picks up
        5. 201 hangs up

        Which is reported as:
        1. 201 calls 202
        2. 202 picks up
        3. 201 hangs up
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-account.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000002',
                'targets': ['SIP/150010002-00000003'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000002',
                'target': 'SIP/150010002-00000003',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000002',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ctd_account_world(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        In this scenario:
        1. 201 is dialed
        2. 201 picks up
        3. +31260010001 is dialed
        4. +31260010001 picks up
        5. +31260010001 hangs up

        Which is reported as:
        1. 201 dials +31260010001
        2. +31260010001 picks up
        3. +31260010001 hangs up
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-world.json')

        calling_chan = SimpleChannel(
            account_code='15001',
            caller_id=CallerId(num='201'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Calling...', num='+31150010001'),
            exten='+31260010001',
            linkedid='c4061ca6474c-1531990515.302',
            name='SIP/150010001-00000008',
            state=6,
            uniqueid='c4061ca6474c-1531990515.317',
        )

        target_chan = SimpleChannel(
            account_code='15001',
            caller_id=CallerId(num='+31260010001'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='+31150010001'),
            exten='s',
            linkedid='c4061ca6474c-1531990515.302',
            name='SIP/voipgrid-siproute-docker-00000009',
            state=6,
            uniqueid='c4061ca6474c-1531990517.363',
        )

        expected_events = [
            ('on_b_dial', {
                'caller': calling_chan,
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

    def test_ctd_account_world_deny_a(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        In this scenario:
        1. 201 is dialed
        2. 201 refuses the call

        Which is reported as:
        1. 201's leg hangs up with reason 'busy'. The A leg is the only SIP
           channel in an originated call to reach RINGING, so the on_b_dial_ringing
           originated-fallback promotes it to is_calling=True. When 201 then
           hangs up, on_hangup fires for the promoted channel. Previously this
           was silent — the new behaviour ensures Click-to-Dial callers get
           notified that their CTD attempt didn't go through.
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-world-deny-a.json')

        expected_events = [
            ('on_hangup', {
                'caller': 'SIP/150010001-00000010',
                'reason': 'busy',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ctd_account_world_deny_b(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        In this scenario:
        1. 201 is dialed
        2. 201 picks up
        3. +31260010001 is dialed
        4. +31260010001 rejects the call

        Which is reported as:
        1. 201 dials +31260010001
        2. +31260010001 hangs up
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-world-deny-b.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000011',
                'targets': ['SIP/voipgrid-siproute-docker-00000012'],
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-00000011',
                'reason': 'busy',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ctd_attn_xfer_abbcac(self):
        """
        Click-to-dial with an attended transfer initiated by B.
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-account-xfer-attn-abbcac.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-0000001d',
                'targets': ['SIP/150010002-0000001e'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-0000001d',
                'target': 'SIP/150010002-0000001e',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010002-0000001f',
                'targets': ['SIP/150010003-00000020'],
            }),
            ('on_b_dial_end', {
                'caller': 'SIP/150010002-0000001f',
                'reason': 'answer',
                'targets': ['SIP/150010003-00000020']}),
            ('on_up', {
                'caller': 'SIP/150010002-0000001f',
                'target': 'SIP/150010003-00000020',
            }),
            ('on_attended_transfer', {
                'caller': 'SIP/150010001-0000001d',
                'target': 'SIP/150010003-00000020',
                'transferer': 'SIP/150010002-0000001f',
            }),
            ('on_hangup', {
                'caller': 'SIP/150010001-0000001d',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ctd_attn_xfer_abacbc(self):
        """
        Click-to-dial with an attended transfer initiated by A.
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-world-xfer-attn-abacbc.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000025',
                'targets': ['SIP/voipgrid-siproute-docker-00000026'],
            }),
            ('on_up', {
                'caller': 'SIP/150010001-00000025',
                'target': 'SIP/voipgrid-siproute-docker-00000026',
            }),
            ('on_b_dial', {
                'caller': 'SIP/150010001-00000029',
                'targets': ['SIP/150010003-0000002a'],
            }),
            ('on_b_dial_end', {
                'caller': 'SIP/150010001-00000029',
                'reason': 'answer',
                'targets': ['SIP/150010003-0000002a']}),
            ('on_up', {
                'caller': 'SIP/150010001-00000029',
                'target': 'SIP/150010003-0000002a',
            }),
            ('on_attended_transfer', {
                'caller': 'SIP/voipgrid-siproute-docker-00000026',
                'target': 'SIP/150010003-0000002a',
                'transferer': 'SIP/150010001-00000029',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000026',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ctd_account_world_no_ringing(self):
        """
        Click-to-dial where the B side never reaches state 5 RINGING.
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-world-no-ringing.json')

        calling_chan = SimpleChannel(
            account_code='15001',
            caller_id=CallerId(num='2401'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Calling...', num='+31150010001'),
            exten='+31260010001',
            linkedid='ua5-ams-1552575068.23242646',
            name='SIP/150010063-0015f5f1',
            state=6,
            uniqueid='ua5-ams-1552575068.23242663',
        )

        target_chan = SimpleChannel(
            account_code='15001',
            caller_id=CallerId(num='+31260010001'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(num='+31150010001'),
            exten='s',
            linkedid='ua5-ams-1552575068.23242646',
            name='SIP/voipgrid-siproute-ams-0015f5f3',
            state=6,
            uniqueid='ua5-ams-1552575069.23242717',
        )

        expected_events = [
            ('on_b_dial', {
                'caller': calling_chan,
                'targets': [target_chan],  # no .replace(state=5) here
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

    def test_ctd_account_world_b_rejects_fast(self):
        """
        Click-to-dial where the B side returns a final response without ever
        sending 180 Ringing (e.g. upstream 404 Not Found).

        Sequence:
        1. 201 (account 100890001) is dialed and answers.
        2. The orchestrator's worker semi dials B (+31501234567) via siproute.
        3. The upstream returns 404 Not Found directly; B's PJSIP channel
           goes DOWN -> HANGUP without ever reaching state 5 RINGING and
           without reaching state 6 UP.
        4. The whole call is torn down.

        Before the on_b_dial_ringing originated-fallback was added, no
        notifications fired at all for this pattern (Alarmed reported this
        in production). Now A is promoted to is_calling=True at its first
        RINGING (via the fallback) and gets its exten set from
        channel.connected_line.num (the B number) — so on_hangup fires
        with reason 'completed' and the eventual reporter notification
        carries the B number as destination.number.
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-account-world-b-rejects-fast.json')

        expected_events = [
            ('on_hangup', {
                'caller': 'PJSIP/100890001-000000a9',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_cmn_world_world(self):
        """
        Call-me-now call between two external numbers.
        """
        events = self.run_and_get_events(
            'fixtures/originate/cmn-world-world.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'SIP/voipgrid-siproute-docker-0000002b',
                'targets': ['SIP/voipgrid-siproute-docker-0000002e'],
            }),
            ('on_up', {
                'caller': 'SIP/voipgrid-siproute-docker-0000002b',
                'target': 'SIP/voipgrid-siproute-docker-0000002e',
            }),
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-0000002b',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_cmn_world_account_unaccepted(self):
        """
        Call-me-now call between two external numbers where A does not accept.

        +31260010001 is dialed,
        +31260010001 picks up and does not accept.

        The first-called party hangs up after declining the confirm prompt.
        The on_b_dial_ringing originated-fallback promotes that channel to
        is_calling=True (it's the only SIP channel of the originated call to
        reach RINGING), so on_hangup fires for it with reason 'completed'
        once the confirm flow ends. Previously this was silent.
        """
        events = self.run_and_get_events(
            'fixtures/originate/cmn-world-world-unaccepted.json')

        expected_events = [
            ('on_hangup', {
                'caller': 'SIP/voipgrid-siproute-docker-00000031',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)

    def test_ctd_out_of_order(self):
        """
        Click-to-dial with out-of-order AMI events.

        This fixture represents a CTD call where AMI events arrive in an order
        where the DialBegin for Bob fires before Alice's PJSIP has entered any
        bridge. get_bridge_peers_recursive() traverses through the bridge chain
        that forms after Alice answers to find Alice's PJSIP as the caller.

        Event Timeline:
        1. PJSIP/898970006-00060687 created (caller, Alice)
        2. DialBegin for caller PJSIP (triggers on_b_dial_ringing for Alice)
        3. Alice PJSIP enters bridge (3 seconds later, after answering)
        4. Local channel starts dialing Bob (3.4 seconds later)
        5. Bob (siproute) starts ringing -> triggers on_b_dial_ringing for Bob

        When on_b_dial_ringing runs for Bob (step 5):
        - Alice's bridges are already set up (she answered in step 3)
        - get_bridge_peers_recursive() traverses Local;2's bridge chain to find Alice
        - Alice is set as is_calling=True, ringing notification is sent
        - on_up fires when Bob answers
        """
        events = self.run_and_get_events(
            'fixtures/originate/ctd-out-of-order.json')

        expected_events = [
            ('on_b_dial', {
                'caller': 'PJSIP/898970006-00060687',
                'targets': ['PJSIP/voipgrid-siproute-114_121-00060688'],
            }),
            ('on_up', {
                'caller': 'PJSIP/898970006-00060687',
                'target': 'PJSIP/voipgrid-siproute-114_121-00060688',
            }),
            ('on_hangup', {
                'caller': 'PJSIP/898970006-00060687',
                'reason': 'completed',
            }),
        ]

        self.assertEqualChannels(expected_events, events)
