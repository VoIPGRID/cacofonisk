from cacofonisk.callerid import CallerId
from .replaytest import ChannelEventsTestCase


class TestSimpleOrig(ChannelEventsTestCase):

    def test_ab_success(self):
        """Test a simple, successful call.

        202 calls 203, 203 picks up and later the call is disconnected.
        """
        events = self.run_and_get_events('examples/orig/ab_success.json')

        expecteds = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, number='203', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501851189.231',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, number='203', is_public=True),
                'reason': 'completed',
            }),
        ))

        self.assertEqual(events, expecteds)

    def test_ab_busy(self):
        """Test a simple call where B is busy.
        """
        events = self.run_and_get_events('examples/orig/ab_busy.json')

        expecteds = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501851519.239',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='201', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501851519.239',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='201', is_public=True),
                'reason': 'busy'
            }),
        ))

        self.assertEqual(events, expecteds)

    def test_ab_callgroup(self):
        """Test a simple call to a group where one phone is picked up.
        """
        events = self.run_and_get_events('examples/orig/ab_callgroup.json')

        expecteds = self.events_from_tuples((
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='401', is_public=True),
            }),
            ('on_b_dial', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, number='401', is_public=True),
            }),
            ('on_up', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='401', is_public=True),
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010003, name='', number='401', is_public=True),
                'reason': 'no-answer'
            }),
            ('on_hangup', {
                'call_id': '63f2f9ce924a-1501852169.254',
                'caller': CallerId(code=150010002, name='Robert Murray', number='202', is_public=True),
                'callee': CallerId(code=150010001, number='401', is_public=True),
                'reason': 'completed'
            }),
        ))

        self.assertEqual(events, expecteds)

