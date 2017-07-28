from .replaytest import ChannelEventsTestCase, MockChannelManager


class TestVarSet(ChannelEventsTestCase):

    def test_set_channel_vars(self):
        """Test receive variables from VarSet events.

        Many details about a call can be obtained by listening to the VarSet
        events. In this test, a few known keys are tracked to check whether
        they are stored correctly.
        """
        class ChannelVarReporter(MockChannelManager):

            def _get_channel_vars(self, channel):
                desired_vars = ['client_id', 'account_id', 'limit_client', 'hide_ext_cliname']

                return {key: channel.custom[key] for key in desired_vars}

            def on_b_dial(self, caller_channel, callee_channel):
                self._events.append({
                    'event': 'on_b_dial',
                    'caller_vars': self._get_channel_vars(caller_channel),
                    'callee_vars': self._get_channel_vars(callee_channel),
                })

            def on_up(self, caller_channel, callee_channel):
                self._events.append({
                    'event': 'on_up',
                    'caller_vars': self._get_channel_vars(caller_channel),
                    'callee_vars': self._get_channel_vars(callee_channel),
                })

            def on_hangup(self, caller_channel, callee_channel, reason):
                self._events.append({
                    'event': 'on_hangup',
                    'caller_vars': self._get_channel_vars(caller_channel),
                    'callee_vars': self._get_channel_vars(callee_channel),
                })

            def on_transfer(self, redirector, party1, party2):
                pass

        events = self.run_and_get_events('examples/orig/user_var_set.json', ChannelVarReporter)

        expecteds = (
            {
                'event': 'on_b_dial',
                'callee_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010001',
                },
                'caller_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010002',
                }
            },
            {
                'event': 'on_up',
                'callee_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010001',
                },
                'caller_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010002',
                }
            },
            {
                'event': 'on_b_dial',
                'callee_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010003',
                },
                'caller_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010002',
                }
            },
            {
                'event': 'on_up',
                'callee_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010003',
                },
                'caller_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010002',
                }
            },
            {
                'event': 'on_hangup',
                'callee_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010003',
                },
                'caller_vars': {
                    'hide_ext_cliname': '1',
                    'client_id': '15001',
                    'limit_client': '0',
                    'account_id': '150010001',
                }
            },
        )

        self.assertEqual(events, expecteds)

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
