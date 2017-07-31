from .replaytest import ChannelEventsTestCase, MockChannelManager


class TestVarSet(ChannelEventsTestCase):

    def test_user_event(self):
        """Test UserEvents are passed on to the reporter.

        The Asterisk event type UserEvent is reserved for custom events
        defined by the user. You can use it to pass additional data from a
        dial plan to Cacofonisk (like whether it should send events for a
        given call).
        """
        class UserEventReporter(MockChannelManager):
            def on_b_dial(self, caller_channel, callee_channel):
                pass

            def on_up(self, caller_channel, callee_channel):
                pass

            def on_transfer(self, redirector, party1, party2):
                pass

            def on_hangup(self, caller_channel, callee_channel, reason):
                pass

            def on_user_event(self, event):
                self._events.append({key: event[key] for key in ['UserEvent', 'Provider', 'AccountCode']})

        events = self.run_and_get_events('examples/orig/user_events.json', UserEventReporter)

        expecteds = (
            {
                'Provider': 'cloudcti',
                'UserEvent': 'NotifyCallstate',
                'AccountCode': '150010003',
            },
            {
                'Provider': 'cloudcti',
                'UserEvent': 'NotifyCallstate',
                'AccountCode': '150010001'
            }
        )

        self.assertEqual(events, expecteds)
