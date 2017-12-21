from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestConnectab(ChannelEventsTestCase):

    def test_account_world(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        217 is dialed,
        217 picks up,
        +31613925xxx is dialed
        +31613925xxx picks up
        +31613925xxx hangs up
        """
        events = self.run_and_get_events('fixtures/connectab/ctd-account-world.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1511536963.147',
                'caller': CallerId(code=126680005, number='+31853030900', is_public=True),
                'to_number': '+31613925xxx',
                'targets': [CallerId(code=0, number='+31613925xxx', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1511536963.147',
                'caller': CallerId(code=126680005, number='+31853030900', is_public=True),
                'to_number': '+31613925xxx',
                'callee': CallerId(code=0, number='+31613925xxx', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1511536963.147',
                'caller': CallerId(code=126680005, number='+31853030900', is_public=True),
                'to_number': '+31613925xxx',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_account_account(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        203 is dialed,
        203 picks up,
        202 is dialed
        202 picks up
        203 hangs up
        """
        events = self.run_and_get_events('fixtures/connectab/ctd-account-account.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua1-staging-1511945444.284',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '202',
                'targets': [CallerId(code=150010002, number='202', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua1-staging-1511945444.284',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '202',
                'callee': CallerId(code=150010002, number='202', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua1-staging-1511945444.284',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '202',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_account_world_deny_a(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        203 is dialed,
        203 refuses the call
        """
        events = self.run_and_get_events('fixtures/connectab/ctd-account-world-deny_a.json')

        self.assertEqual((), events)

    def test_account_world_fail(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        203 is dialed,
        203 picks up, and hangs up fast
        """
        events = self.run_and_get_events('fixtures/connectab/ctd-account-world-fail2.json')

        self.assertEqual((), events)

    def test_account_world_deny_b(self):
        """
        Click-to-dial call between a phoneaccount and an external number.

        203 is dialed,
        203 picks up
        +31613925xxx does not pickup
        """
        events = self.run_and_get_events('fixtures/connectab/ctd-account-world-deny_b.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua1-staging-1512032862.847',
                'caller': CallerId(code=150010003, number='+31150010001', is_public=True),
                'to_number': '+31613925xxx',
                'targets': [CallerId(code=0, name='', number='+31613925xxx', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'ua1-staging-1512032862.847',
                'caller': CallerId(code=150010003, number='+31150010001', is_public=True),
                'to_number': '+31613925xxx',
                'reason': 'no-answer',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_ctd_attn_xfer(self):
        """
        Click-to-dial with an attended transfer.

        Ensure that the call_id which is used for ConnectAB is consistent with
        other functions (like transfers).
        """
        events = self.run_and_get_events('fixtures/connectab/ctd-attn-xfer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1513778720.1901',
                'caller': CallerId(code=126680005, number='217', is_public=True),
                'to_number': '218',
                'targets': [CallerId(code=126680010, name='', number='218', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1513778720.1901',
                'caller': CallerId(code=126680005, number='217', is_public=True),
                'to_number': '218',
                'callee': CallerId(code=126680010, name='', number='218', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': 'ua0-acc-1513778732.1912',
                'caller': CallerId(code=126680005, number='+31853030900', is_public=True),
                'to_number': '0612345678',
                'targets': [CallerId(number='+31612345678', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1513778732.1912',
                'caller': CallerId(code=126680005, number='+31853030900', is_public=True),
                'to_number': '0612345678',
                'callee': CallerId(code=126680005, number='+31612345678', is_public=True),
            }),
            ('on_warm_transfer', {
                'redirector': CallerId(code=126680005, number='+31853030900', is_public=True),
                'caller': CallerId(code=126680005, number='217', is_public=True),
                'callee': CallerId(code=126680005, number='+31612345678', is_public=True),
                'new_id': 'ua0-acc-1513778732.1912',
                'merged_id': 'ua0-acc-1513778720.1901',
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1513778732.1912',
                'caller': CallerId(code=126680005, number='217', is_public=True),
                'to_number': '218',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_cmn_world_account(self):
        """
        Call-me-now call between a mobilephone and an internal number.

        +31613925xxx is dialed,
        +31613925xxx picks up,
        203 is dialed
        203 picks up,
        +31613925xxx hangs up
        """
        events = self.run_and_get_events('fixtures/connectab/cmn-world-account.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua1-staging-1512038737.882',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua1-staging-1512038737.882',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '203',
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua1-staging-1512038737.882',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '203',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_cmn_world_account_unaccepted(self):
        """
        Call-me-now call between a mobilephone and an internal number.

        +31613925xxx is dialed,
        +31613925xxx picks up and does not accept.
        """
        events = self.run_and_get_events('fixtures/connectab/cmn-world-account-unaccepted.json')

        self.assertEqual((), events)

    def test_cmn_world_world(self):
        """
        Call-me-now call between a mobilephone and an internal number.

        +31613925xxx is dialed,
        +31613925xxx picks up,
        +31150010003 is dialed and starts ua1-staging-1512036277.877,
        +31150010003 picks up,
        +31150010003 hangs up
        """
        events = self.run_and_get_events('fixtures/connectab/cmn-world-world.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua1-staging-1512036255.866',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '+31150010003',
                'targets': [CallerId(code=0, number='+31150010003', is_public=True)],
            }),
            ('on_b_dial', {
                'call_id': 'ua1-staging-1512036277.877',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '+31150010003',
                'targets': [CallerId(code=150010003, number='+31150010003', is_public=True)],
            }),
            ('on_up', {
                'call_id': 'ua1-staging-1512036277.877',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '+31150010003',
                'callee': CallerId(code=150010003, number='+31150010003', is_public=True),
            }),
            ('on_up', {
                'call_id': 'ua1-staging-1512036255.866',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '+31150010003',
                'callee': CallerId(code=0, number='+31150010003', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'ua1-staging-1512036277.877',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '+31150010003',
                'reason': 'completed',
            }),
            ('on_hangup', {
                'call_id': 'ua1-staging-1512036255.866',
                'caller': CallerId(code=15001, number='+31613925xxx', is_public=True),
                'to_number': '+31150010003',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_cmn_self_world(self):
        """
        Call-me-now between an external number and a self owned number.

        In here, you'll see two calls:
        - The "inbound" call from Call-me-now which goes to the local number.
        - The "inbound" call from world-in which is routed to the destination.
        """
        events = self.run_and_get_events('fixtures/connectab/cmn-self-world.json')

        expected_event = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': 'ua0-acc-1513786051.1965',
                'caller': CallerId(code=12668, number='+31508009074', is_public=True),
                'targets': [CallerId(number='+31853030903', is_public=True)],
                'to_number': '+31853030903',
            }),
            ('on_b_dial', {
                'call_id': 'ua0-acc-1513786064.1976',
                'caller': CallerId(code=12668, number='+31508009074', is_public=True),
                'targets': [CallerId(code=126680010, number='+31853030903', is_public=True)],
                'to_number': '+31853030903',
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1513786064.1976',
                'caller': CallerId(code=12668, number='+31508009074', is_public=True),
                'callee': CallerId(code=126680010, number='+31853030903', is_public=True),
                'to_number': '+31853030903',
            }),
            ('on_up', {
                'call_id': 'ua0-acc-1513786051.1965',
                'caller': CallerId(code=12668, number='+31508009074', is_public=True),
                'callee': CallerId(number='+31853030903', is_public=True),
                'to_number': '+31853030903',
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1513786051.1965',
                'caller': CallerId(code=12668, number='+31508009074', is_public=True),
                'reason': 'completed',
                'to_number': '+31853030903',
            }),
            ('on_hangup', {
                'call_id': 'ua0-acc-1513786064.1976',
                'caller': CallerId(code=12668, number='+31508009074', is_public=True),
                'reason': 'completed',
                'to_number': '+31853030903',
            }),
        ))

        self.assertEqual(expected_event, events)
