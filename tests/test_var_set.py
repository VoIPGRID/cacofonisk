from cacofonisk import BaseReporter
from tests.replaytest import ChannelEventsTestCase


class TestVarSet(ChannelEventsTestCase):

    def test_user_event(self):
        """Test UserEvents are passed on to the reporter.

        The Asterisk event type UserEvent is reserved for custom events
        defined by the user. You can use it to pass additional data from a
        dial plan to Cacofonisk (like whether it should send events for a
        given call).
        """
        class UserEventReporter(BaseReporter):
            def __init__(self):
                super(UserEventReporter, self).__init__()
                self.events = []

            def on_user_event(self, caller, event):
                desired = ('UserEvent', 'Provider', 'AccountCode',
                           'WebhookUrls', 'Direction', 'ClientId',
                           'AccountInternalNumber', 'UserInternalNumbers')
                event = {key: event[key] for key in desired if key in event}
                self.events.append(event)

        events = self.run_and_get_events(
            'fixtures/var_set/user_events.json',
            UserEventReporter()
        )

        expected_events = [
            {
                'AccountCode': '260010001',
                'AccountInternalNumber': '201',
                'ClientId': '26001',
                'Direction': 'outbound',
                'Provider': 'webhook',
                'UserEvent': 'NotifyCallstate',
                'WebhookUrls': '',
            },
            {
                'AccountCode': '15001',
                'ClientId': '15001',
                'Direction': 'inbound',
                'UserEvent': 'NotifyCallstate',
                'WebhookUrls': 'http://example.com/foo/bar',
            },
            {
                'AccountCode': '150010001',
                'Provider': 'cloudcti',
                'UserEvent': 'NotifyCallstate',
            },
            {
                'AccountCode': '150010001',
                'AccountInternalNumber': '201',
                'Provider': 'webhook',
                'UserEvent': 'NotifyCallstate',
                'UserInternalNumbers': '601',
            },
        ]

        self.assertEqual(expected_events, events)
