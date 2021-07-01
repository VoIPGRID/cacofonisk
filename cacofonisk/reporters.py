import logging


class BaseReporter(object):
    def close(self):
        """
        Called on end, so any buffered output can be flushed.
        """
        pass

    def on_event(self, event):
        """
        Called after the regular even processing has been done.

        Useful when custom event processing is required in addition to
        regular event processing.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        pass

    def on_b_dial(self, caller, targets):
        """
        Gets invoked when the B side of a call is initiated.

        In the common case, calls in Asterisk consist of two sides: A calls
        Asterisk and Asterisk calls B. This event is fired when Asterisk
        performs the second step.

        Args:
            caller (SimpleChannel): The initiator of the call.
            targets (list): The recipients of the call.
        """
        pass

    def on_up(self, caller, target):
        """
        Track when a call has been set up between two parties.

        In simple calls, a "up" event is raised when a call has been ringing
        and it has been answered. Additionally, around the transfer of a call
        a new "up" event is raised as well not notify who are still calling.

        Args:
            caller (SimpleChannel): The initiator of the call.
            target (SimpleChannel): The recipient of the call.
        """
        pass

    def on_attended_transfer(self, caller, transferer, target):
        """
        Gets invoked when an attended transfer is completed.

        In an attended transfer, one of the participants of a conversation
        calls a third participant, waits for the third party to answer, talks
        to the third party and then transfers their original conversation
        partner to the third party.

        Args:
            caller (SimpleChannel): The party which has been transferred.
            transferer (SimpleChannel): The party who initiated the transfer.
            target (SimpleChannel): The party which received the transfer.
        """
        pass

    def on_blonde_transfer(self, caller, transferer, targets):
        """
        Gets invoked when a blonde transfer is completed.

        A blonde transfer is a transfer which is started like an attended
        transfer, but the transferer steps out of the call before it is
        picked up.

        Args:
            caller (SimpleChannel): The party being transferred.
            transferer (SimpleChannel): The party initiating the transfer.
            targets (list): The channels being dialed.
        """
        pass

    def on_blind_transfer(self, caller, transferer, targets):
        """
        Gets invoked when a blind transfer is completed.

        A blind transfer is transfer where the transferer tells Asterisk to
        refer the call to another number and immediately ends the call. No
        b_dial is triggered before the transfer is completed.

        Args:
            caller (SimpleChannel): The party being transferred.
            transferer (SimpleChannel): The party initiating the transfer.
            targets (list): The channels being dialed.
        """
        pass

    def on_user_event(self, caller, event):
        """
        Handle custom UserEvent messages from Asterisk.

        Adding user events to a dial plan is a useful way to send additional
        information to Cacofonisk. You could add additional user info,
        parameters used for processing the events and more.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        pass

    def on_hangup(self, caller, reason):
        """
        Track when a call ends for a caller.

        Args:
            caller (SimpleChannel): The initiator of the call.
            reason (str): A textual reason as to why the call was ended.
        """
        pass

    def on_queue_caller_abandon(self, caller):
        """
        Track when a caller abandons a queue.

        Args:
            caller (SimpleChannel): The initiator of the call.
        """
        pass


class LoggingReporter(BaseReporter):
    """
    LoggingReporter is a simple base reporter which logs all calls to the
    provided Logger instance.
    """
    def __init__(self, logger=None):
        """
        Create a logger for this reporter.

        Args:
            logger (Logger): An optional logger instance.
        """
        self._logger = logger or logging.getLogger(__name__)

    def close(self):
        """
        Called on end, so any buffered output can be flushed.
        """
        pass

    def on_event(self, event):
        """
        Called after the regular even processing has been done.

        Useful when custom event processing is required in addition to
        regular event processing.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        pass

    def on_b_dial(self, caller, targets):
        """
        Gets invoked when the B side of a call is initiated.

        In the common case, calls in Asterisk consist of two sides: A calls
        Asterisk and Asterisk calls B. This event is fired when Asterisk
        performs the second step.

        Args:
            caller (SimpleChannel): The initiator of the call.
            targets (list): The recipients of the call.
        """
        self._logger.info('{} ringing: {} --> {} ({})'.format(
            caller.linkedid, caller, caller.exten, targets))

    def on_up(self, caller, target):
        """
        Track when a call has been set up between two parties.

        In simple calls, a "up" event is raised when a call has been ringing
        and it has been answered. Additionally, around the transfer of a call
        a new "up" event is raised as well not notify who are still calling.

        Args:
            caller (SimpleChannel): The initiator of the call.
            target (SimpleChannel): The recipient of the call.
        """
        self._logger.info('{} up: {} --> {} ({})'.format(
            caller.linkedid, caller, caller.exten, target))

    def on_attended_transfer(self, caller, transferer, target):
        """
        Gets invoked when an attended transfer is completed.

        In an attended transfer, one of the participants of a conversation
        calls a third participant, waits for the third party to answer, talks
        to the third party and then transfers their original conversation
        partner to the third party.

        Args:
            caller (SimpleChannel): The party which has been transferred.
            transferer (SimpleChannel): The party who initiated the transfer.
            target (SimpleChannel): The party which received the transfer.
        """
        self._logger.info(
            '{} <== {} attn xfer: {} <--> {} (through {})'.format(
                caller.linkedid, transferer.linkedid,
                caller, target, transferer))

    def on_blonde_transfer(self, caller, transferer, targets):
        """
        Gets invoked when a blonde transfer is completed.

        A blonde transfer is a transfer which is started like an attended
        transfer, but the transferer steps out of the call before it is
        picked up.

        Args:
            caller (SimpleChannel): The party being transferred.
            transferer (SimpleChannel): The party initiating the transfer.
            targets (list): The channels being dialed.
        """
        self._logger.info(
            '{} <== {} blonde xfer: {} <--> {} (through {})'.format(
                caller.linkedid, transferer.linkedid, caller, targets,
                transferer))

    def on_blind_transfer(self, caller, transferer, targets):
        """
        Gets invoked when a blind transfer is completed.

        A blind transfer is transfer where the transferer tells Asterisk to
        refer the call to another number and immediately ends the call. No
        b_dial is triggered before the transfer is completed.

        Args:
            caller (SimpleChannel): The party being transferred.
            transferer (SimpleChannel): The party initiating the transfer.
            targets (list): The channels being dialed.
        """
        self._logger.info('{} bld xfer: {} <--> {} (through {})'.format(
            caller.linkedid, caller, targets, transferer))

    def on_user_event(self, caller, event):
        """
        Handle custom UserEvent messages from Asterisk.

        Adding user events to a dial plan is a useful way to send additional
        information to Cacofonisk. You could add additional user info,
        parameters used for processing the events and more.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        self._logger.info('{} user_event: {}'.format(event['Linkedid'], event))

    def on_hangup(self, caller, reason):
        """
        Track when a call ends for a caller.

        Args:
            caller (SimpleChannel): The initiator of the call.
            reason (str): A textual reason as to why the call was ended.
        """
        self._logger.info('{} hangup: {} --> {} (reason: {})'.format(
            caller.linkedid, caller, caller.exten, reason))


class MultiReporter(LoggingReporter):
    """
    MultiReporter is a reporter which combines multiple reporters and
    forwards received events to all of them.
    """
    def __init__(self, reporters, logger=None):
        """
        Create a multi reporter with the given reporters.

        Args:
            reporters (list): An iterable with reporters.
            logger (Logger): Not used.
        """
        super(MultiReporter, self).__init__(logger=logger)

        self.reporters = reporters

    def close(self):
        super(MultiReporter, self).close()

        for reporter in self.reporters:
            reporter.close()

    def on_event(self, event):
        super(MultiReporter, self).on_event(event)

        for reporter in self.reporters:
            reporter.on_event(event)

    def on_user_event(self, caller, event):
        super(MultiReporter, self).on_user_event(caller, event)

        for reporter in self.reporters:
            reporter.on_user_event(caller, event)

    def on_b_dial(self, caller, targets):
        super(MultiReporter, self).on_b_dial(caller, targets)

        for reporter in self.reporters:
            reporter.on_b_dial(caller, targets)

    def on_up(self, caller, target):
        super(MultiReporter, self).on_up(caller, target)

        for reporter in self.reporters:
            reporter.on_up(caller, target)

    def on_attended_transfer(self, caller, transferer, target):
        super(MultiReporter, self).on_attended_transfer(
            caller, transferer, target)

        for reporter in self.reporters:
            reporter.on_attended_transfer(caller, transferer, target)

    def on_blonde_transfer(self, caller, transferer, targets):
        super(MultiReporter, self).on_blonde_transfer(
            caller, transferer, targets)

        for reporter in self.reporters:
            reporter.on_blonde_transfer(caller, transferer, targets)

    def on_blind_transfer(self, caller, transferer, targets):
        super(MultiReporter, self).on_blind_transfer(
            caller, transferer, targets)

        for reporter in self.reporters:
            reporter.on_blind_transfer(caller, transferer, targets)

    def on_hangup(self, caller, reason):
        super(MultiReporter, self).on_hangup(caller, reason)

        for reporter in self.reporters:
            reporter.on_hangup(caller, reason)

    def on_queue_caller_abandon(self, caller):
        super(MultiReporter, self).on_queue_caller_abandon(caller)

        for reporter in self.reporters:
            reporter.on_queue_caller_abandon(caller)
