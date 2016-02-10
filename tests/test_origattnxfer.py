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
        events = self.run_and_get_events(
            'examples/orig/xfer_abacbc.json')

        expecteds = self.events_from_tuples((
            # 201 calls 202
            ('on_b_dial', (126680001, '', '201', True),
                          (126680002, '', '202', True)),
            # 201 calls 203
            ('on_b_dial', (126680001, '', '201', True),
                          (126680003, '', '203', True)),
            # 201 transfers 202 <-> 203
            ('on_transfer', (126680001, '', '201', True),
                            (126680002, '', '202', True),
                            (126680003, '', '203', True)),
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
            ('on_b_dial', (0, 'Foo bar', '+31501234567', True),
                          (126680001, '', '+31508009000', True)),
            # 201 calls 202
            ('on_b_dial', (126680001, '', '201', True),
                          (126680002, '', '202', True)),
            # 201 transfers +31501234567 <-> 202
            ('on_transfer', (126680001, '', '201', True),
                            (0, 'Foo bar', '+31501234567', True),
                            (126680002, '', '202', True)),
        ))

        self.assertEqual(events, expecteds)
