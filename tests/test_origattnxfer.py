from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestAttnXferOrig(ChannelEventsTestCase):
    def test_xfer_abacbc(self):
        """
        First of all, we need to get notifications that calls are being
        made:
        - 201 (126680001) calls 202
        - 201 calls 203 (126680003)

        Secondly, we need notifications that an (attended) transfer has
        happened:
        - 201 joins the other channels (202 <--> 203)
        """
        events = self.run_and_get_events('examples/orig/xfer_abacbc.json')

        expecteds = self.events_from_tuples((
            # 201 calls 202
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1442387090.552',
                'caller': CallerId(code=126680001, number='201', is_public=True),
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1442387090.552',
                'caller': CallerId(code=126680001, number='201', is_public=True),
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),

            # 201 calls 203
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1442387091.556',
                'caller': CallerId(code=126680001, number='201', is_public=True),
                'callee': CallerId(code=126680003, number='203', is_public=True),
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1442387091.556',
                'caller': CallerId(code=126680001, number='201', is_public=True),
                'callee': CallerId(code=126680003, number='203', is_public=True),
            }),

            # 201 transfers 202 <-> 203
            ('on_transfer', {
                'redirector': CallerId(code=126680001, number='201', is_public=True),
                'party1': CallerId(code=126680002, number='202', is_public=True),
                'party2': CallerId(code=126680003, number='203', is_public=True),
                'new_id': 'vgua0-dev-1442387091.556',
                'merged_id': 'vgua0-dev-1442387090.552',
            }),

            # 202 and 203 are done
            ('on_hangup', {
                'call_id': 'vgua0-dev-1442387091.556',
                'caller': CallerId(code=126680002, number='202', is_public=True),
                'callee': CallerId(code=126680003, number='203', is_public=True),
                'reason': 'completed',
            })
        ))

        self.assertEqual(events, expecteds)

    def test_xfer_abbcac(self):
        """
        First of all, we need to get notifications that calls are being
        made:
        - +31501234567 calls 201 (126680001)
        - 201 calls 202

        Secondly, we need notifications that an (attended) transfer has
        happened:
        - 201 joins the other channels (+31501234567 <--> 202)
        """
        events = self.run_and_get_events(
            'examples/orig/xfer_abbcac.json')

        expecteds = self.events_from_tuples((
            # +31501234567 calls 201
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1442387041.544',
                'caller': CallerId(code=0, name='Foo bar', number='+31501234567', is_public=True),
                'callee': CallerId(code=126680001, number='+31508009000', is_public=True),
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1442387041.544',
                'caller': CallerId(code=0, name='Foo bar', number='+31501234567', is_public=True),
                'callee': CallerId(code=126680001, number='+31508009000', is_public=True),
            }),

            # 201 calls 202
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1442387044.548',
                'caller': CallerId(code=126680001, number='201', is_public=True),
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1442387044.548',
                'caller': CallerId(code=126680001, number='201', is_public=True),
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),

            # 201 transfers +31501234567 <-> 202
            ('on_transfer', {
                'redirector': CallerId(code=126680001, number='201', is_public=True),
                'party1': CallerId(code=0, name='Foo bar', number='+31501234567', is_public=True),
                'party2': CallerId(code=126680002, number='202', is_public=True),
                'new_id': 'vgua0-dev-1442387044.548',
                'merged_id': 'vgua0-dev-1442387041.544',
            }),

            # +31501234567 and 202 are done
            ('on_hangup', {
                'call_id': 'vgua0-dev-1442387044.548',
                'caller': CallerId(code=0, name='Foo bar', number='+31501234567', is_public=True),
                'callee': CallerId(code=126680002, number='202', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expecteds)
