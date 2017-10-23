from .replaytest import ChannelEventsTestCase, TestReporter


class TestVarSet(ChannelEventsTestCase):

    def test_user_event(self):
        """Test UserEvents are passed on to the reporter.

        The Asterisk event type UserEvent is reserved for custom events
        defined by the user. You can use it to pass additional data from a
        dial plan to Cacofonisk (like whether it should send events for a
        given call).
        """
        class UserEventReporter(TestReporter):
            def on_b_dial(self, call_id, caller, callee):
                pass

            def on_warm_transfer(self, new_id, merged_id, redirector, party1, party2):
                pass

            def on_up(self, call_id, caller, callee):
                pass

            def on_hangup(self, call_id, caller, callee, reason):
                pass

            def on_user_event(self, event):
                self.events.append({key: event[key] for key in ['UserEvent', 'Provider', 'AccountCode']})

        events = self.run_and_get_events('fixtures/var_set/user_events.json', UserEventReporter())

        expected_events = (
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

        self.assertEqual(expected_events, events)
