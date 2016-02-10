from .replaytest import ChannelEventsTestCase


class TestBlondeBlindXferOrig(ChannelEventsTestCase):
    def test_xfer_blondeanon(self):
        events = self.run_and_get_events(
            'examples/orig/xfer_blondeanon.json')

        expecteds = self.events_from_tuples((
            # +31507xxxxxx calls 202/205, 205 picks up, blonde xfer to 202
            ('on_b_dial', (0, '', '+31507xxxxxx', False),
                          (126680002, '', '+31507001918', True)),
            ('on_b_dial', (0, '', '+31507xxxxxx', False),
                          (126680005, '', '+31507001918', True)),

            # Blonde xfer consists of a nice 2ndary dial, like the
            # attended transfer. But the bridge isn't up on the target
            # channel, so the last CLI takes more work to get right.
            # Luckily that is tucked away in the ChannelManager class.
            ('on_b_dial', (126680005, 'No NAT', '205', True),
                          (126680002, '', '202', True)),
            ('on_transfer', (126680005, 'No NAT', '205', True),  # redirector
                            (0, '', '+31507xxxxxx', False),      # party1
                            (126680002, '', '202', True)),       # party2
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
            # => 202 (gets picked up)
            ('on_b_dial', (0, '', '+31507xxxxxx', False),
                          (126680002, '', '+31507001918', True)),
            # => +31612345678 (gets busy)
            ('on_b_dial', (0, '', '+31507xxxxxx', False),
                          (0, '', '+31612345678', True)),

            # 202 calls 205
            # This is a regular call, and this is hung up again by the
            # phone.
            ('on_b_dial', (126680002, 'John 202 Doe', '202', True),
                          (126680005, '', '205', True)),

            # 202 transfers +31507xxxxxx <-> 205
            # The transferor had detected ringing pressed the attn. xfer
            # button. The phone hung up the first call and proceeded
            # with a blind transfer (this).
            # Our channel internals make sure that a transfer first gets
            # a proper on_b_dial event. The CLI number looks odd, but
            # it's okay, because it's what 126680002 was reached by.
            ('on_b_dial', (126680002, '', '+31507001918', True),
                          (126680005, '', '205', True)),
            # Again, the CLI-num for 126680002 is okay.
            # Ideally, I'd like to see +31507xxxxxx in CLI-num, but I
            # can live with 'P', since the is_public is False anyway.
            ('on_transfer', (126680002, '', '+31507001918', True),
                            (0, '', 'P', False),  # +31507xxxxxx ?
                            (126680005, '', '205', True)),
        ))

        self.assertEqual(events, expecteds)

    def test_xfer_blind(self):
        events = self.run_and_get_events(
            'examples/orig/xfer_blind.json')

        expecteds = self.events_from_tuples((
            # +31501234567 calls 202/205, 202 picks up, blind xfer to 205
            # => 202
            ('on_b_dial', (0, '', '+31501234567', True),
                          (126680002, '', '+31507001918', True)),
            # => 205
            ('on_b_dial', (0, '', '+31501234567', True),
                          (126680005, '', '+31507001918', True)),

            # (CLI for 126680002 is how it was reached externally,
            # that's okay.)
            ('on_b_dial', (126680002, '', '+31507001918', True),
                          (126680005, '', '205', True)),

            # Blind xfer.
            # (CLI for 126680002 is how it was reached externally,
            # that's okay.)
            ('on_transfer', (126680002, '', '+31507001918', True),
                            (0, '', '+31501234567', True),
                            (126680005, '', '205', True)),
        ))

        self.assertEqual(events, expecteds)
