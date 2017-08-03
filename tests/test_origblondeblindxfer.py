from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestBlondeBlindXferOrig(ChannelEventsTestCase):
    def test_xfer_blondeanon(self):
        events = self.run_and_get_events(
            'examples/orig/xfer_blondeanon.json')

        expecteds = self.events_from_tuples((
            # +31507xxxxxx calls 202/205, 205 picks up, blonde xfer to 202
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443448768.113',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443448768.113', # FIXME ideally, this is vgua0-dev-1443448768.115
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680005, number='+31507001918', is_public=True),
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1443448768.113',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680005, number='+31507001918', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443448768.115',  # FIXME this should match with the b_dial to 202
                'caller': CallerId(number='Anonymous', is_public=False),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
                'reason': 'no-answer',
            }),

            # Blonde xfer consists of a nice 2ndary dial, like the
            # attended transfer. But the bridge isn't up on the target
            # channel, so the last CLI takes more work to get right.
            # Luckily that is tucked away in the ChannelManager class.
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443448784.120',
                'caller': CallerId(code=126680005, name='No NAT', number='205', is_public=True),
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),
            ('on_transfer', {
                'redirector': CallerId(code=126680005, name='No NAT', number='205', is_public=True),
                'party1': CallerId(number='+31507xxxxxx', is_public=False),
                'party2': CallerId(code=126680002, number='202', is_public=True),
                'new_id': 'vgua0-dev-1443448784.120',
                'merged_id': 'vgua0-dev-1443448768.116',  # FIXME this should be vgua0-dev-1443448768.113
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1443448784.120',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680002, number='202', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443448784.120',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680002, number='202', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expecteds)

    def test_xfer_blondeblindanon(self):
        """
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
        """
        events = self.run_and_get_events(
            'examples/orig/xfer_blondeblindanon.json')

        expecteds = self.events_from_tuples((
            # +31507xxxxxx calls 201/202/+31612345678
            # => 126680001 (doesn't answer)
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680001, number='+31507001918', is_public=True),
                'reason': 'no-answer',
            }),

            # => 202 (gets picked up)
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),

            # => +31612345678 (gets busy)
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(number='+31612345678', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(number='+31612345678', is_public=True),
                'reason': 'busy',
            }),

            # => 202 picks up
            ('on_up', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),

            # 202 calls 205
            # This is a regular call, and this is hung up again by the
            # phone.
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442640.94',
                'caller': CallerId(code=126680002, name='John 202 Doe', number='202', is_public=True),
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),
            # ('on_hangup', (0, 'John 202 Doe', '202', True),
            #               (126680005, '', '205', True),
            #               'completed'),

            # 202 transfers +31507xxxxxx <-> 205
            # The transferor had detected ringing pressed the attn. xfer
            # button. The phone hung up the first call and proceeded
            # with a blind transfer (this).
            # Our channel internals make sure that a transfer first gets
            # a proper on_b_dial event. The CLI number looks odd, but
            # it's okay, because it's what 126680002 was reached by.
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='+31507xxxxxx', is_public=False),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
                'reason': 'completed',
            }),
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(code=126680002, number='+31507001918', is_public=True),
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),
            # Again, the CLI-num for 126680002 is okay.
            # Ideally, I'd like to see +31507xxxxxx in CLI-num, but I
            # can live with 'P', since the is_public is False anyway.
            ('on_transfer', {
                'redirector': CallerId(code=126680002, number='+31507001918', is_public=True),
                'party1': CallerId(number='P', is_public=False),  # +31507xxxxxx ?
                'party2': CallerId(code=126680005, number='205', is_public=True),
                'new_id': 'vgua0-dev-1443442648.100',  # FIXME this and the merged ids are bogus
                'merged_id': 'vgua0-dev-1443442620.85',
            }),
            ('on_up', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='P', is_public=False),  # +31507xxxxxx ?
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443442620.82',
                'caller': CallerId(number='P', is_public=False),  # +31507xxxxxx ?
                'callee': CallerId(code=126680005, number='205', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expecteds)

    def test_xfer_blind(self):
        events = self.run_and_get_events(
            'examples/orig/xfer_blind.json')

        expecteds = self.events_from_tuples((
            # +31501234567 calls 202/205, 202 picks up, blind xfer to 205
            # => 202
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),

            # => 205
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443449049.124',  # FIXME: Ideally, this would be a different ID.
                'caller': CallerId(number='+31501234567', is_public=True),
                'callee': CallerId(code=126680005, number='+31507001918', is_public=True),
            }),

            # => 202 picks up
            ('on_up', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'callee': CallerId(code=126680002, number='+31507001918', is_public=True),
            }),

            # => 205 doesn't pick up
            ('on_hangup', {
                'call_id': 'vgua0-dev-1443449049.128',
                'caller': CallerId(number='+31501234567', is_public=True),
                'callee': CallerId(code=126680005, number='+31507001918', is_public=True),
                'reason': 'no-answer',
            }),

            # (CLI for 126680002 is how it was reached externally,
            # that's okay.)
            ('on_b_dial', {
                'call_id': 'vgua0-dev-1443449060.133',
                'caller': CallerId(code=126680002, number='+31507001918', is_public=True),
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),

            # Blind xfer.
            # (CLI for 126680002 is how it was reached externally,
            # that's okay.)
            ('on_transfer', {
                'redirector': CallerId(code=126680002, number='+31507001918', is_public=True),
                'party1': CallerId(number='+31501234567', is_public=True),
                'party2': CallerId(code=126680005, number='205', is_public=True),
                'new_id': 'vgua0-dev-1443449049.124',
                'merged_id': 'vgua0-dev-1443449060.133',
            }),

            ('on_up', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'callee': CallerId(code=126680005, number='205', is_public=True),
            }),

            ('on_hangup', {
                'call_id': 'vgua0-dev-1443449049.124',
                'caller': CallerId(number='+31501234567', is_public=True),
                'callee': CallerId(code=126680005, number='205', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expecteds)
