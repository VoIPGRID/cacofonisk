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

    def on_warm_transfer(self, call_id, merged_id, redirector, party1, party2):
        """
        Gets invoked when an attended transfer is completed.

        In an attended transfer, one of the participants of a conversation
        calls a third participant, waits for the third party to answer, talks
        to the third party and then transfers their original conversation
        partner to the third party.

        Args:
            call_id (str): The unique ID of the resulting call.
            merged_id (str): The unique ID of the call which will end.
            redirector (CallerId): The caller ID of the party performing the
                transfer.
            party1 (CallerId): The caller ID of the party which has been
                transferred.
            party2 (CallerId): The caller ID of the party which received the
                transfer.
        """
        pass

    def on_cold_transfer(self, call_id, merged_id, redirector, party1, targets):
        """
        Gets invoked when a blind or blonde transfer is completed.

        In a blind transfer, one of the call participant transfers their
        conversation partner to a third party. However, unlike with an
        attended transfer, the redirector doesn't wait for the other end to
        pick up, but just punches in the number and sends their conversation
        party away. Because of this, multiple phones may actually be addressed
        by this transfer, hence the multiple targets. The real participant can
        be recovered later on when someone answers the transferred call.

        A blonde is a middle road between blind transfers and attended
        transfers. With a blond transfer, the redirector requests an attended
        transfer but doesn't wait for the receiving end to pick up. Since the
        data of blind and blonde transfers looks identical, they don't have
        special hooks.

        Args:
            call_id (str): The unique ID of the resulting call.
            merged_id (str): The unique ID of the call which will end.
            redirector (CallerId): The caller ID of the party performing the
                transfer.
            party1 (CallerId): The caller ID of the party which has been
                transferred.
            targets (list): A list of CallerId objects whose phones are
                ringing for this transfer.
        """
        pass

    def on_forward(self, call_id, caller, loser, targets):
        """
        Gets invoked when a call is forwarded before being picked up.

        There are two known situations when this may occur.

        The first is call forwarding. Some phones support setting a call
        forwarding destination, meaning calls which are not picked up on the
        phone itself are forwarded to someone else.

        The second is call pickup. Phones can be configured in Asterisk to be
        in a call pickup group. If one of the phones is the group rings,
        another phone in the group can type in a special sequence and hijack
        the call so they can answer the call themselves.

        Args:
            call_id (str): The unique ID of the resulting call.
            caller (CallerId): The caller being forwarded.
            loser (CallerId): The party who was originally called.
            targets (list): A list of CallerId's to whom the call is being
                forwarded.
        """
        pass

    def on_b_dial(self, call_id, caller, targets):
        """
        Gets invoked when the B side of a call is initiated.

        In the common case, calls in Asterisk consist of two sides: A
        calls Asterisk and Asterisk calls B. This event is fired when
        Asterisk performs the second step.

        Args:
            call_id (str): A unique identifier of the call.
            caller (CallerId): The initiator of the call.
            targets (list): The recipients of the call.
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
