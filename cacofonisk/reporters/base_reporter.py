class BaseReporter(object):
    """
    BaseReporter is a skeleton baseclass for any Reporter classes. The methods
    can be overwritten. See class:`ChannelManager` to see where these methods
    are called.
    """
    def trace_ami(self, event):
        """Log the full AMI event before it's being processed.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        pass

    def trace_msg(self, msg):
        """Log a diagnostic message before calling one of the events below.

        Args:
            msg (str): A log string.
        """
        pass

    def close(self):
        """Called on end, so any buffered output can be flushed."""
        pass

    def on_event(self, event):
        """Called after the regular even processing has been done.

        Useful when custom event processing is required in addition to
        regular event processing.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        pass

    def on_transfer(self, call_id, merged_id, redirector, party1, party2):
        """
        Gets invoked when a call is transferred.

        In the common case, a call transfer consists of three parties
        where the redirector was speaking to party1 and party2. By
        transferring the call, she ties party1 and party2 together and
        leaves herself.

        But there are other cases, including the case where the
        redirector is the party that takes an incoming call and places
        himself on end of the bridge. In that case he is both the
        redirector and one of party1 or party2.

        Args:
            call_id (str): A unique identifier of this call.
            merged_id (str): The unique identifier of the call being joined
                with this call.
            redirector (CallerId): The initiator of the transfer.
            party1 (CallerId): One of the two parties that are tied
                together.
            party2 (CallerId): The other one.
        """
        pass

    def on_b_dial(self, call_id, caller, callee):
        """
        Gets invoked when the B side of a call is initiated.

        In the common case, calls in Asterisk consist of two sides: A
        calls Asterisk and Asterisk calls B. This event is fired when
        Asterisk performs the second step.

        Args:
            call_id (str): A unique identifier of the call.
            caller (CallerId): The initiator of the call.
            callee (CallerId): The recipient of the call.
        """
        pass

    def on_user_event(self, event):
        """Handle custom UserEvent messages from Asterisk.

        Adding user events to a dial plan is a useful way to send additional
        information to Cacofonisk. You could add additional user info,
        parameters used for processing the events and more.

        Args:
            event (Message): Dict-like object with all attributes in the event.
        """
        pass

    def on_up(self, call_id, caller, callee):
        """Track when a call has been set up between two parties.

        In simple calls, a "up" event is raised when a call has been ringing
        and it has been answered. Additionally, around the transfer of a call
        a new "up" event is raised as well not notify who are still calling.

        Args:
            call_id (str): A unique identifier of the call.
            caller (CallerId): The initiator of the call.
            callee (CallerId): The recipient of the call.
        """
        pass

    def on_hangup(self, call_id, caller, callee, reason):
        """Track when a call between two parties has ended.

        Args:
            call_id (str): A unique identifier of the call.
            caller (CallerId): The initiator of the call.
            callee (CallerId): The recipient of the call.
            reason (str): A textual reason as to why the call was ended.
        """
        pass
