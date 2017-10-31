from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestBlondeXferOrig(ChannelEventsTestCase):
    """Test call state notifications for blonde transfers.

    A blonde transfer (also known as semi-attended transfer) is a type of
    transfer which looks like an attended transfer, but the transferrer
    doesn't wait for person C to pick up.
    """
    def test_xfer_blonde_abacbc(self):
        """
        Test blonde transfer where A initiates the transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blonde_abacbc.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1502178068.16',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '201',
                'targets': [CallerId(code=150010001, number='201', is_public=True)],
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1502178068.16',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '201',
                'callee': CallerId(code=150010001, number='201', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1502178076.20',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_cold_transfer', {
                'redirector': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'caller': CallerId(code=150010001, number='201', is_public=True),
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
                'new_id': '63f2f9ce924a-1502178076.20',
                'merged_id': '63f2f9ce924a-1502178068.16',
                'to_number': '203',
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1502178076.20',
                'caller': CallerId(code=150010001, number='201', is_public=True),
                'to_number': '203',
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1502178076.20',
                'caller': CallerId(code=150010001, number='201', is_public=True),
                'to_number': '203',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blonde_abbcac(self):
        """
        Test blonde transfer where B initiates the transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blonde_abbcac.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1502179190.24',
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'to_number': '202',
                'targets': [CallerId(code=150010002, number='202', is_public=True)],
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1502179190.24',
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'to_number': '202',
                'callee': CallerId(code=150010002, number='202', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1502179195.28',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '201',
                'targets': [CallerId(code=150010001, name='', number='201', is_public=True)],
            }),
            ('on_cold_transfer', {
                'redirector': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'targets': [CallerId(code=150010001, name='', number='201', is_public=True)],
                'new_id': '63f2f9ce924a-1502179195.28',
                'merged_id': '63f2f9ce924a-1502179190.24',
                'to_number': '201',
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1502179195.28',
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'to_number': '201',
                'callee': CallerId(code=150010001, name='', number='201', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1502179195.28',
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'to_number': '201',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blondeanon(self):
        """
        Complex test of blonde transfer.

        Test call groups, anonymous callers and a blond transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blondeanon.json')

        expected_events = self.events_from_tuples((
            # +31507xxxxxx calls 202/205, 205 picks up, blonde xfer to 202
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443448768.113',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'to_number': '+31507001918',
                'targets': [
                    CallerId(code=126680002, number='+31507001918', is_public=True),
                    CallerId(code=126680005, number='+31507001918', is_public=True),
                ],
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1443448768.113',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'to_number': '+31507001918',
                'callee': CallerId(code=126680005, number='+31507001918', is_public=True),
            }),

            # Blonde xfer consists of a nice secondary dial, like the
            # attended transfer. But the bridge isn't up on the target
            # channel, so the last CLI takes more work to get right.
            # Luckily that is tucked away in the ChannelManager class.
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443448784.120',
                'caller': CallerId(code=126680005, name='No NAT', number='205', is_public=True),
                'to_number': '202',
                'targets': [CallerId(code=126680002, number='202', is_public=True)],
            }),
            ('on_cold_transfer', {
                'redirector': CallerId(code=126680005, name='No NAT', number='205', is_public=True),
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'targets': [CallerId(code=126680002, number='202', is_public=True)],
                'new_id': 'vgua0-dev-1443448784.120',
                'merged_id': 'vgua0-dev-1443448768.113',
                'to_number': '202',
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1443448784.120',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'to_number': '202',
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443448784.120',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'to_number': '202',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blondeblindanon(self):
        """Test the blond blind transfer (SPA941 call).

        First of all, we need to get notifications that calls are being
        made:
        - +31507xxxxxx calls 202 (126680002)
        - 202 calls 205 (126680005) but doesn't wait for pickup

        Secondly, we need notifications that an (attended) transfer has
        happened. This is done using a blind transfer (broken blonde
        transfer of SPA941 which involves a premature call to 205).
        - 202 joins the other channels (+31507xxxxxx <--> 205)

        The blondeblindanon transfer is a legacy thing of the SPA941
        that doesn't do blonde transfers. Instead, it hangs up after
        hearing the ringing to do a blind transfer.

        The call IDs are a mess now, but fixing it is too complicated
        for a severely outdated phone.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blondeblindanon.json')

        expected_events = self.events_from_tuples((
            # +31507xxxxxx calls 201/202/+31612345678
            # => 126680001 (doesn't answer)
            # => +31612345678 (gets busy)
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'to_number': '+31507001918',
                'targets': [
                    CallerId(number='+31612345678', is_public=True),
                    CallerId(code=126680002, number='+31507001918', is_public=True),
                ],
            }),

            # => 202 picks up
            ('on_up', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'to_number': '+31507001918',
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),

            # 202 calls 205
            # This is a regular call, and this is hung up again by the
            # phone.
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442640.94',
                'caller': CallerId(code=126680002, name='John 202 Doe', number='202', is_public=True),
                'to_number': '205',
                'targets': [CallerId(code=126680005, number='205', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443442640.94',
                'caller': CallerId(code=126680002, name='John 202 Doe', number='202', is_public=True),
                'to_number': '205',
                'reason': 'cancelled',
            }),

            # 202 transfers +31507xxxxxx <-> 205
            # The transferor had detected ringing pressed the attn. xfer
            # button. The phone hung up the first call and proceeded
            # with a blind transfer (this).
            # Our channel internals make sure that a transfer first gets
            # a proper on_b_dial event. The CLI number looks odd, but
            # it's okay, because it's what 126680002 was reached by.
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442620.85',
                'caller': CallerId(code=126680002, number='+31507001918', is_public=True),
                'to_number': '205',
                'targets': [CallerId(code=126680005, number='205', is_public=True)],
            }),
            # Again, the CLI-num for 126680002 is okay.
            # Ideally, I'd like to see +31507xxxxxx in CLI-num, but I
            # can live with 'P', since the is_public is False anyway.
            ('on_cold_transfer', {
                'redirector': CallerId(code=126680002, number='+31507001918', is_public=True),
                'caller': CallerId(number='P', is_public=False),  # +31507xxxxxx ?
                'targets': [CallerId(code=126680005, number='205', is_public=True)],
                'new_id': 'vgua0-dev-1443442620.82',
                'merged_id': 'vgua0-dev-1443442620.85',
                'to_number': '205',
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='P', is_public=False),  # Technically +31507xxxxxx
                'to_number': '205',
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='P', is_public=False),  # Technically +31507xxxxxx
                'to_number': '205',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blonde_reject(self):
        """
        Test blonde transfer where the transfer target rejects the call.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blonde_reject.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509119790.66',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509119790.66',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509119799.70',
                'caller': CallerId(code=150010004, name='Jonathan Carey', number='204', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509119799.70',
                'caller': CallerId(code=150010004, name='Jonathan Carey', number='204', is_public=True),
                'to_number': '203',
                'reason': 'no-answer',
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509119790.66',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blonde_group_b(self):
        """
        Test blonde transfer where the call is transferred to a group by B.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blonde_group_b.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509120252.74',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509120252.74',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509120257.78',
                'caller': CallerId(code=150010004, name='Jonathan Carey', number='204', is_public=True),
                'to_number': '403',
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
            }),
            ('on_cold_transfer', {
                'new_id': '0f00dcaa884f-1509120257.78',
                'merged_id': '0f00dcaa884f-1509120252.74',
                'redirector': CallerId(code=150010004, name='Jonathan Carey', number='204', is_public=True),
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
                'to_number': '403',
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509120257.78',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '403',
                'callee': CallerId(code=150010001, number='403', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509120257.78',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '403',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blonde_group_a(self):
        """
        Test blonde transfer where the call is transferred to a group by A.
        """
        events = self.run_and_get_events('fixtures/xfer_blonde/xfer_blonde_group_a.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509353018.11',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509353018.11',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509353024.15',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '403',
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
            }),
            ('on_cold_transfer', {
                'new_id': '0f00dcaa884f-1509353024.15',
                'merged_id': '0f00dcaa884f-1509353018.11',
                'redirector': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'caller': CallerId(code=150010004, number='204', is_public=True),
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
                'to_number': '403',
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509353024.15',
                'caller': CallerId(code=150010004, number='204', is_public=True),
                'to_number': '403',
                'callee': CallerId(code=150010001, number='403', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509353024.15',
                'caller': CallerId(code=150010004, number='204', is_public=True),
                'to_number': '403',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)
