from unittest import TestCase
from unittest.mock import MagicMock

from cacofonisk import BaseReporter
from cacofonisk.callerid import CallerId
from cacofonisk.channel import SimpleChannel
from cacofonisk.reporters import MultiReporter


class MultiReporterTestCase(TestCase):

    def setUp(self):
        self.mock_reporter = MagicMock(spec=BaseReporter)
        self.multi_reporter = MultiReporter([self.mock_reporter])

        self.a_party = SimpleChannel(
            name='SIP/voipgrid-siproute-docker-00000036',
            uniqueid='f29ea68048f6-1530017224.892',
            linkedid='f29ea68048f6-1530017224.892',
            account_code='15001',
            caller_id=CallerId(num='+31150010001'),
            cid_calling_pres=None,
            connected_line=CallerId(),
            exten='+31150010004',
            state=6,
        )

        self.b_party = SimpleChannel(
            account_code='150010001',
            caller_id=CallerId(name='Andrew Garza', num='201'),
            cid_calling_pres='1 (Presentation Allowed, Passed Screen)',
            connected_line=CallerId(),
            exten='202',
            linkedid='195176c06ab8-1529936170.42',
            name='SIP/150010001-00000004',
            state=6,
            uniqueid='195176c06ab8-1529936170.42',
        )

        self.c_party = SimpleChannel(
            account_code='150010001',
            caller_id=CallerId(num='202'),
            cid_calling_pres='0 (Presentation Allowed, Not Screened)',
            connected_line=CallerId(name='Andrew Garza', num='201'),
            exten='s',
            linkedid='195176c06ab8-1529936170.42',
            name='SIP/150010002-00000005',
            state=6,
            uniqueid='195176c06ab8-1529936170.50',
        )

    def test_close(self):
        self.multi_reporter.close()
        self.mock_reporter.close.assert_called_once_with()

    def test_on_event(self):
        event_dict = {'Linkedid': '195176c06ab8-1529936170.42'}
        self.multi_reporter.on_event(event_dict)
        self.mock_reporter.on_event.assert_called_once_with(event_dict)

    def test_on_user_event(self):
        event_dict = {'Linkedid': '195176c06ab8-1529936170.42'}
        self.multi_reporter.on_user_event(self.a_party, event_dict)
        self.mock_reporter.on_user_event.assert_called_once_with(self.a_party, event_dict)

    def test_on_b_dial(self):
        targets = [self.b_party, self.c_party]

        self.multi_reporter.on_b_dial(self.a_party, targets)
        self.mock_reporter.on_b_dial.assert_called_once_with(
            self.a_party, targets)

    def test_on_up(self):
        self.multi_reporter.on_up(self.a_party, self.b_party)
        self.mock_reporter.on_up.assert_called_once_with(
            self.a_party, self.b_party)

    def test_on_attended_transfer(self):
        self.multi_reporter.on_attended_transfer(
            self.a_party, self.b_party, self.c_party)
        self.mock_reporter.on_attended_transfer.assert_called_once_with(
            self.a_party, self.b_party, self.c_party)

    def test_on_blonde_transfer(self):
        self.multi_reporter.on_blonde_transfer(
            self.a_party, self.b_party, [self.c_party])
        self.mock_reporter.on_blonde_transfer.assert_called_once_with(
            self.a_party, self.b_party, [self.c_party])

    def test_on_blind_transfer(self):
        self.multi_reporter.on_blind_transfer(
            self.a_party, self.b_party, [self.c_party])
        self.mock_reporter.on_blind_transfer.assert_called_once_with(
            self.a_party, self.b_party, [self.c_party])

    def test_on_hangup(self):
        self.multi_reporter.on_hangup(self.a_party, 'busy')
        self.mock_reporter.on_hangup.assert_called_once_with(
            self.a_party, 'busy')
