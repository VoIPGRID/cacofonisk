from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestBlindXferOrig(ChannelEventsTestCase):

    def test_xfer_blind_abbcac(self):
        """Test a blind transfer where B initiates the transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_abbcac.json')

        expected_events = self.events_from_tuples((
            # 203 calls 202
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501834121.34',
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'to_number': '202',
                'targets': [CallerId(code=150010002, number='202', is_public=True)],
            }),
            # 202 picks up
            ('on_up', {
                'call_id': '63f2f9ce924a-1501834121.34',
                'caller': CallerId(code=150010003, name='Julia Rhodes', number='203', is_public=True),
                'to_number': '202',
                'callee': CallerId(code=150010002, number='202', is_public=True),
            }),
            # 202 dials 201...
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501834121.35',
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'to_number': '201',
                'targets': [CallerId(code=150010001, number='201', is_public=True)],
            }),
            # ... and immediately transfers 203 to 201
            ('on_cold_transfer', {
                'redirector': CallerId(code=150010002, number='202', is_public=True),
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'targets': [CallerId(code=150010001, number='201', is_public=True)],
                'new_id': '63f2f9ce924a-1501834121.34',
                'merged_id': '63f2f9ce924a-1501834121.35',
                'to_number': '201',
            }),
            # 201 picks up to talk to 203
            ('on_up', {
                'call_id': '63f2f9ce924a-1501834121.34',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '201',
                'callee': CallerId(code=150010001, number='201', is_public=True),
            }),
            # 203 and 201 are done
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501834121.34',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '201',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_abacbc(self):
        """Test a blind transfer where A initiates the transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_abacbc.json')

        expected_events = self.events_from_tuples((
            # 202 calls 203
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501834972.41',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            # 203 picks up
            ('on_up', {
                'call_id': '63f2f9ce924a-1501834972.41',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '203',
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            # 202 dials 201...
            # (CLI for 150010002 is how it was reached externally,
            # that's okay.)
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501834980.45',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'to_number': '201',
                'targets': [CallerId(code=150010001, name='Robert Murray', number='201', is_public=True)],
            }),
            # ... and immediately transfers 203 to 201
            ('on_cold_transfer', {
                'redirector': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'targets': [CallerId(code=150010001, name='Robert Murray', number='201', is_public=True)],
                'new_id': '63f2f9ce924a-1501834980.45',
                'merged_id': '63f2f9ce924a-1501834972.41',
                'to_number': '201',
            }),
            # 201 picks up to talk to 203
            ('on_up', {
                'call_id': '63f2f9ce924a-1501834980.45',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '201',
                'callee': CallerId(code=150010001, name='Robert Murray', number='201', is_public=True),
            }),
            # 203 and 201 are done
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501834980.45',
                'caller': CallerId(code=150010003, number='203', is_public=True),
                'to_number': '201',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_complex(self):
        """Test a complex blind transfer.

        Test a blind transfer with call groups where B initiates the transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind.json')

        expected_events = self.events_from_tuples((
            # +31501234567 calls 202/205, 202 picks up, blind xfer to 205
            # => 202
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'to_number': '+31507001918',
                'targets': [
                    CallerId(code=126680002, number='+31507001918', is_public=True),
                    CallerId(code=126680005, number='+31507001918', is_public=True),
                ],
            }),

            # => 202 picks up
            ('on_up', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'to_number': '+31507001918',
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),

            # (CLI for 126680002 is how it was reached externally,
            # that's okay.)
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443449049.125',
                'caller': CallerId(code=126680002, number='+31507001918', is_public=True),
                'to_number': '205',
                'targets': [CallerId(code=126680005, number='205', is_public=True)],
            }),

            # Blind xfer.
            # (CLI for 126680002 is how it was reached externally,
            # that's okay.)
            ('on_cold_transfer', {
                'redirector': CallerId(code=126680002, number='+31507001918', is_public=True),
                'caller': CallerId(number='+31501234567', is_public=True),
                'targets': [CallerId(code=126680005, number='205', is_public=True)],
                'new_id': 'vgua0-dev-1443449049.124',
                'merged_id': 'vgua0-dev-1443449049.125',
                'to_number': '205',
            }),

            ('on_up', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'to_number': '205',
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),

            ('on_hangup', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'to_number': '205',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_a_no_answer(self):
        """
        Test a blind transfer from A where the transfer target is down.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_a_no_answer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509114500.0',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509114500.0',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509114500.0',
                # TODO: The name is missing on the caller. Weird, no disaster.
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'to_number': '204',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_b_no_answer(self):
        """
        Test a blind transfer from B where the transfer target is down.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_b_no_answer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509115795.11',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509115795.11',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509115795.11',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_reject(self):
        """
        Test a blind transfer from where the target rejects the transfer.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_reject.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509116084.19',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509116084.19',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509116084.20',
                'caller': CallerId(code=150010004, number='204', is_public=True),
                'to_number': '203',
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
            }),
            ('on_cold_transfer', {
                'redirector': CallerId(code=150010004, number='204', is_public=True),
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'targets': [CallerId(code=150010003, number='203', is_public=True)],
                'new_id': '0f00dcaa884f-1509116084.19',
                'merged_id': '0f00dcaa884f-1509116084.20',
                'to_number': '203',
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509116084.19',
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'to_number': '203',
                'reason': 'no-answer',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_group(self):
        """
        Test a blind transfer where the call is transferred to a group.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_group.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509117819.36',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509117819.36',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509117819.37',
                'caller': CallerId(code=150010004, number='204', is_public=True),
                'to_number': '403',
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
            }),
            ('on_cold_transfer', {
                'redirector': CallerId(code=150010004, number='204', is_public=True),
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'targets': [
                    CallerId(code=150010001, number='403', is_public=True),
                    CallerId(code=150010003, number='403', is_public=True),
                ],
                'new_id': '0f00dcaa884f-1509117819.36',
                'merged_id': '0f00dcaa884f-1509117819.37',
                'to_number': '403',
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509117819.36',
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'to_number': '403',
                'callee': CallerId(code=150010001, number='403', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509117819.36',
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'to_number': '403',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)

    def test_xfer_blind_group_no_answer(self):
        """
        Test a blind transfer where the call is transferred to a group.
        """
        events = self.run_and_get_events('fixtures/xfer_blind/xfer_blind_group_no_answer.json')

        expected_events = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '0f00dcaa884f-1509119608.56',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'targets': [CallerId(code=150010004, number='204', is_public=True)],
            }),
            ('on_up', {
                'call_id': '0f00dcaa884f-1509119608.56',
                'caller': CallerId(code=150010002, name='David Meadows', number='202', is_public=True),
                'to_number': '204',
                'callee': CallerId(code=150010004, number='204', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '0f00dcaa884f-1509119608.56',
                'caller': CallerId(code=150010002, number='202', is_public=True),
                'to_number': '204',
                'reason': 'completed',
            }),
        ))

        self.assertEqual(expected_events, events)
