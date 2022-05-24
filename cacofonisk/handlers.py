import logging

from .bridge import Bridge, BridgeDict, MissingBridgeUniqueid
from .channel import Channel, ChannelDict, MissingUniqueid
from .constants import (AST_CAUSE_ANSWERED_ELSEWHERE, AST_CAUSE_CALL_REJECTED,
                        AST_CAUSE_INTERWORKING, AST_CAUSE_NO_ANSWER,
                        AST_CAUSE_NO_USER_RESPONSE, AST_CAUSE_NORMAL_CLEARING,
                        AST_CAUSE_UNKNOWN, AST_CAUSE_USER_BUSY, AST_STATE_DOWN,
                        AST_STATE_RING, AST_STATE_RINGING, AST_STATE_UP)


class EventHandler(object):
    """
    The EventHandler translates AMI events to high level call events.

    There are two ways to use EventHandler.

    The simple way to use this method is to pass your own Reporter to it.
    The Reporter receives simple, high level hooks about a call. See
    BaseReporter for more information about these hooks.

    Alternatively, you can implement your own, more low-level events by
    extending EventHandler and overriding one or more of the following methods:
    - on_state_change
    - on_a_dial
    - on_b_dial
    - on_bridge_enter
    - on_attended_transfer
    - on_blind_transfer
    - on_blonde_transfer
    - on_user_event
    - on_hangup

    See the docs about the particular methods for more information about
    what they receive and how they work.
    """
    FILTER_EVENTS = True

    def __init__(self, reporter, hostname='localhost', logger=None):
        """
        Create a EventHandler instance.

        Args:
            reporter (Reporter): A reporter to send events to.
        """
        self._reporter = reporter
        self._channels = ChannelDict()
        self._bridges = BridgeDict()
        self._logger = logger or logging.getLogger(__name__)
        self._hostname = hostname

    @classmethod
    def event_handlers(cls):
        """
        Get the events we would like to receive, and functions to handle them.

        Returns:
            dict: A dict with event names as keys and functions as values.
        """
        return {
            'FullyBooted': cls._on_fully_booted,
            # Events related to call setup.
            'Newchannel': cls._on_new_channel,
            'Newstate': cls._on_new_state,
            'LocalBridge': cls._on_local_bridge,
            'Hangup': cls._on_hangup,
            'DialBegin': cls._on_dial_begin,
            'DialEnd': cls._on_dial_end,
            # Events which change channel vars.
            'NewCallerid': cls._on_new_callerid,
            'NewAccountCode': cls._on_new_accountcode,
            'NewConnectedLine': cls._on_new_connected_line,
            # Transfer events.
            'AttendedTransfer': cls._on_attended_transfer,
            'BlindTransfer': cls._on_blind_transfer,
            # Bridges and their contents.
            'BridgeCreate': cls._on_bridge_create,
            'BridgeEnter': cls._on_bridge_enter,
            'BridgeLeave': cls._on_bridge_leave,
            'BridgeDestroy': cls._on_bridge_destroy,
            # User Events
            'UserEvent': cls.on_user_event,
            # Queue Events
            'QueueCallerAbandon': cls._on_queue_caller_abandon,
        }

    def on_event(self, event):
        """
        Interpret an event, update local state and send notifications.

        This function wraps _on_event to catch exceptions related to missing
        channels and bridges, which can happen if the Cacofonisk connects to a
        running Asterisk.

        Args:
            event (dict): A dictionary containing an AMI event.
        """
        try:
            handlers = self.event_handlers()
            if event['Event'] in handlers and handlers[event['Event']]:
                handlers[event['Event']](self, event)

        except MissingUniqueid as e:
            # If this is after a recent FullyBooted and/or start of
            # self, it is reasonable to expect that certain events will
            # fail.
            self._logger.warning(
                'Channel with Uniqueid {} not in mem when processing event: '
                '{!r}'.format(e.args[0], event))
        except MissingBridgeUniqueid as e:
            # This too is reasonably expected.
            self._logger.warning(
                'Bridge with Uniqueid {} not in mem when processing event: '
                '{!r}'.format(e.args[0], event))

        self._reporter.on_event(event)

    def _on_queue_caller_abandon(self, event):
        """
        Handle Queue Caller Abandon messages from Asterisk.

        Args:
            event (dict): Dict-like object with all attributes of the event.
        """
        channel = self._channels[event['Uniqueid']]
        self._reporter.on_queue_caller_abandon(caller=channel.as_namedtuple())

    def _on_fully_booted(self, event):
        """
        FullyBooted event is sent on successful connection to Asterisk.

        Args:
            event (dict): A FullyBooted event.
        """
        self._logger.info('Connection established to Asterisk on {}'.format(
            self._hostname))

        if len(self._bridges) > 0:
            self._logger.warning('Bridge buffers not empty! Flushing {} '
                                 'bridges.'.format(len(self._bridges)))
            self._bridges = BridgeDict()

        if len(self._channels) > 0:
            self._logger.warning('Channel buffers not empty! Flushing {} '
                                 'channels.'.format(len(self._channels)))
            self._channels = ChannelDict()

    def _on_new_channel(self, event):
        """
        NewChannel event is sent when Asterisk creates a new channel.

        If this event is received, a new Channel will be created and
        populated using the data in this event.

        Args:
            event (dict): A NewChannel event.
        """
        channel = Channel(event)
        self._channels[channel.uniqueid] = channel

    def _on_new_state(self, event):
        """
        NewState event is sent when the state of a channel changes.

        In the phase where a phone dials, rings and is picked up,
        the channel state changes several times.

        Args:
            event (dict): A NewState event.
        """
        channel = self._channels[event['Uniqueid']]

        old_state = channel.state
        channel.state = int(event['ChannelState'])
        assert old_state != channel.state

        self.on_state_change(channel, old_state)

    def _on_local_bridge(self, event):
        """
        A LocalBridge is sent when two local channels are bridge.

        Asterisk Local Channels always have two semi-channels, identified
        with the ;1 and ;2 suffixes. When a call is set up, a LocalBridge is
        created to link both semi-channels together.

        Args:
            event (dict): A LocalBridge event.
        """
        local_one = self._channels[event['LocalOneUniqueid']]
        local_two = self._channels[event['LocalTwoUniqueid']]

        assert local_one.fwd_local_bridge is None
        assert local_one.back_local_bridge is None
        assert local_two.fwd_local_bridge is None
        assert local_two.back_local_bridge is None

        local_one.fwd_local_bridge = local_two
        local_two.back_local_bridge = local_one

    def _on_hangup(self, event):
        """
        A Hangup event is sent when a channel is hung up.

        Args:
            event (dict): A Hangup event.
        """
        channel = self._channels[event['Uniqueid']]

        self.on_hangup(channel, event)

        # Disconnect all channels linked to this channel.
        if channel.fwd_local_bridge:
            channel.fwd_local_bridge.back_local_bridge = None

        if channel.back_local_bridge:
            channel.back_local_bridge.fwd_local_bridge = None

        # Remove the channel from our own list.
        del self._channels[channel.uniqueid]

        # If we don't have any channels, check if we're completely clean.
        if not len(self._channels):
            self._logger.info('(no channels left)')

    def _on_dial_begin(self, event):
        """
        A DialBegin event is sent when a dial is created between two channels.

        Dials are created to connect channels during the call setup phase.
        In a simple call scenario, you'd see two dials being created: a dial
        from the calling SIP channel to Local channel semi one, and from
        Local channel semi two to the target SIP channel. The Local semi
        channels are connected using a LocalBridge. By tracing the dials and
        local bridges, it's possible to follow the relation between a
        calling channel and it's targets.

        Args:
            event (dict): A DialBegin event.
        """
        if 'DestUniqueid' in event:
            if 'Uniqueid' in event:
                # This is a dial between two channels. So let's link them
                # together.
                channel = self._channels[event['Uniqueid']]
                destination = self._channels[event['DestUniqueid']]
                channel.is_calling = True

                # Verify target is not being dialed already.
                assert not destination.back_dial

                # _fwd_dials is a list of channels being dialed by A.
                channel.fwd_dials.append(destination)

                # _back_dial is the channel dialing B.
                destination.back_dial = channel

                self.on_dial_begin(channel, destination)
            else:
                # The dial has a destination but not source. That means this
                # Dial was created by an Originate.
                destination = self._channels[event['DestUniqueid']]
                destination.is_originated = True
        else:
            raise AssertionError(
                'A DialBegin event was generated without DestUniqueid: '
                '{}'.format(event))

    def _on_dial_end(self, event):
        """
        DialEnd event is sent when a dial is disconnected between two channels.

        When a call is answered (picked up) or hung up (without being picked
        up), the dial between two channels is ended. After a DialEnd, you will
        either see multiple Hangup events, or see bridges being set up to
        connect the Channels.

        Args:
            event (dict): A DialEnd event.
        """
        # Check if we have a source and destination channel to pull
        # apart. Originate creates Dials without source.
        if 'Uniqueid' in event and 'DestUniqueid' in event:
            channel = self._channels[event['Uniqueid']]
            destination = self._channels[event['DestUniqueid']]

            destination.back_dial = None

            if destination in channel.fwd_dials:
                channel.fwd_dials.remove(destination)
        else:
            # Dials without Uniqueid and DestUniqueid can occur, but we
            # can't/don't handle them.
            pass

    def _on_attended_transfer(self, event):
        """
        An AttendedTransfer event is sent after attended and blonde transfers.

        Args:
            event (dict): An AttendedTransfer event.
        """
        orig_transferer = self._channels[event['OrigTransfererUniqueid']]
        second_transferer = self._channels[
            event['SecondTransfererUniqueid']]

        if event['DestType'] == 'Bridge':
            self.on_attended_transfer(
                orig_transferer, second_transferer, event)
        elif event['DestType'] == 'App' and event['DestApp'] == 'Dial':
            self.on_blonde_transfer(
                orig_transferer, second_transferer, event)
        else:
            raise NotImplementedError(event)

    def _on_blind_transfer(self, event):
        """
        A BlindTransfer event is sent after blind transfers.

        Args:
            event (dict): A BlindTransfer event.
        """
        transferer = self._channels[event['TransfererUniqueid']]
        transferee = self._channels[event['TransfereeUniqueid']]

        self.on_blind_transfer(transferer, transferee, event)

    def _on_bridge_create(self, event):
        """
        A BridgeCreate event is sent when Asterisk creates a new bridge.

        Args:
            event (dict): A BridgeCreate event.
        """
        assert event['BridgeUniqueid'] not in self._bridges
        bridge = Bridge(event)
        self._bridges[bridge.uniqueid] = bridge

    def _on_bridge_enter(self, event):
        """
        A BridgeEnter event is sent when a channel joins a bridge.

        Args:
            event (dict): A BridgeEnter event.
        """
        channel = self._channels[event['Uniqueid']]
        bridge = self._bridges[event['BridgeUniqueid']]

        bridge.peers.add(channel)
        channel.bridge = bridge

        self.on_bridge_enter(channel, bridge)

    def _on_bridge_leave(self, event):
        """
        A BridgeLeave event is sent when a channel is removed from a bridge.

        Args:
            event (dict): A BridgeLeave event.
        """
        channel = self._channels[event['Uniqueid']]
        bridge = self._bridges[event['BridgeUniqueid']]

        bridge.peers.remove(channel)
        channel.bridge = None

    def _on_bridge_destroy(self, event):
        """
        A BridgeDestroy event is sent when a bridge is removed by Asterisk.

        Args:
            event (dict): A BridgeDestroy event.
        """
        assert len(self._bridges[event['BridgeUniqueid']]) is 0
        del self._bridges[event['BridgeUniqueid']]

    def _on_new_callerid(self, event):
        """
        A NewCallerid event is sent when the CallerID of a channel changes.

        Args:
            event (dict): A NewCallerid event.
        """
        channel = self._channels[event['Uniqueid']]

        channel.caller_id = channel.caller_id.replace(
            name=event['CallerIDName'],
            num=event['CallerIDNum'],
        )
        channel.cid_calling_pres = event['CID-CallingPres']

    def _on_new_connected_line(self, event):
        """
        A NewConnectedLine event is sent when the ConnectedLine changes.

        Args:
            event (dict): A NewConnectedLine event.
        """
        channel = self._channels[event['Uniqueid']]

        channel.connected_line = channel.connected_line.replace(
            name=event['ConnectedLineName'],
            num=event['ConnectedLineNum'],
        )

    def _on_new_accountcode(self, event):
        """
        A NewAccountCode is sent when the AccountCode of a channel changes.

        Args:
            event (dict): A NewAccountCode event.
        """
        channel = self._channels[event['Uniqueid']]

        channel.account_code = event['AccountCode']

    # ===================================================================
    # Actual event handlers you can override
    # ===================================================================

    def on_state_change(self, channel, old_state):
        """
        Handle the change of a ChannelState.

        If the status goes from DOWN to RING, then it means the calling party
        hears a dialing tone. If the status goes from DOWN to RINGING or UP,
        then it means the phone of a called party is starting to ring (or has
        been answered immediately without ringing).

        Args:
            channel (Channel): The channel being changed.
            old_state (int): The state before the state change.
        """
        if channel.is_local:
            return

        new_state = channel.state

        if old_state == AST_STATE_DOWN:
            if new_state == AST_STATE_RING:
                self.on_a_dial(channel)
            elif new_state in (AST_STATE_RINGING, AST_STATE_UP):
                self.on_b_dial(channel)

    def on_a_dial(self, channel):
        """
        Handle the event where the caller phone hears the ring tone.

        We don't want this. It's work to get all the values right, and
        when we do, this would look just like on_b_dial.

        Args:
            channel (Channel):
        """
        pass

    def on_b_dial(self, channel):
        """
        Handle the event where a callee phone starts to ring.

        In our case, we check if a dial has already been set up for the
        channel. If so, we may want to send a ringing event.

        Args:
            channel (Channel): The channel of the B side.
        """
        if channel.back_dial:
            self.on_b_dial_ringing(channel)

    def on_dial_begin(self, channel, destination):
        """
        Handle an event where a dial is set up.

        In our case, we check if the channel already has state ringing.
        If so, we may want to send a ringing event.

        Args:
            channel (Channel): The channel initiating the dial.
            destination (Channel): The channel being dialed.
        """
        if not destination.is_local and destination.state == 5:
            self.on_b_dial_ringing(destination)

    def on_b_dial_ringing(self, channel):
        """
        Check a ringing channel and sent a ringing event if required.

        By default, this function will only be called if the destination
        channel:

        - Has an open dial (so a way to trace back how it's being called).
        - Has state "ringing".

        Args:
            channel (Channel): The channel being dialed.
        """
        if 'ignore_b_dial' in channel.custom:
            # Notifications were already sent for this channel.
            # Unset the flag and move on.
            del (channel.custom['ignore_b_dial'])
            return

        a_chan = channel.get_dialing_channel()

        if 'raw_blind_transfer' in a_chan.custom:
            # This is an interesting exception: we got a Blind Transfer
            # message earlier and recorded it in this attribute. We'll
            # translate this b_dial to first a on_b_dial and then the
            # on_transfer event.
            transferer = a_chan.custom.pop('raw_blind_transfer')

            target_chans = a_chan.get_dialed_channels()

            for target in target_chans:
                # To prevent notifications from being sent multiple times,
                # we set a flag on all other channels except for the one
                # starting to ring right now.
                if target != channel:
                    target.custom['ignore_b_dial'] = True

            self._reporter.on_blind_transfer(
                caller=a_chan.as_namedtuple(),
                transferer=transferer.as_namedtuple(),
                targets=[chan.as_namedtuple() for chan in target_chans],
            )
        elif (
                a_chan.is_originated and
                a_chan.fwd_dials and a_chan.fwd_local_bridge
        ):
            # Calls setup through Originate are harder to track.
            # The Channel passed to the Originate has two semis. The Context
            # channel is called first, and when it's up, put in a bridge
            # with semi 2. Next, semi 1 will dial out to the other party.

            # To make it look like a normal call, we will show the call from
            # the Context as the calling party and the call from Channel as
            # the called party.
            originating_chan = a_chan
            a_bridge = originating_chan.fwd_local_bridge.bridge
            a_chan = [peer for peer in a_bridge.peers
                      if not peer.is_local][0]

            if not a_chan.is_local:
                called_exten = originating_chan.fwd_dials[0].exten
                a_chan.exten = called_exten
                a_chan.is_calling = True

                if not a_chan.has_extension:
                    self._logger.error(
                        'Caller (Originate) did not have an extension: '
                        '{}'.format(channel))

                self._reporter.on_b_dial(
                    caller=a_chan.as_namedtuple(),
                    targets=[channel.as_namedtuple()],
                )
        elif not a_chan.is_local:
            # We'll want to send one ringing event for all targets, so send
            # one notification and mark the rest as already notified.
            open_dials = a_chan.get_dialed_channels()
            targets = [dial.as_namedtuple() for dial in open_dials]

            if not a_chan.has_extension:
                self._logger.error(
                    'Caller (Dial) did not have an extension: {}'.format({
                        'caller': a_chan.as_namedtuple(),
                        'destination': channel.as_namedtuple(),
                    }))

            if not targets:
                self._logger.error(
                    'Caller (Dial) did not have any dialed channels: '
                    '{}'.format({
                        'caller': a_chan.as_namedtuple(),
                        'destination': channel.as_namedtuple(),
                    }))

            self._reporter.on_b_dial(
                caller=a_chan.as_namedtuple(),
                targets=targets,
            )

            for b_chan in open_dials:
                if b_chan != channel:
                    # To prevent notifications from being sent multiple
                    # times, we set a flag on all other channels except
                    # for the one starting to ring right now.
                    b_chan.custom['ignore_b_dial'] = True

    def on_bridge_enter(self, channel, bridge):
        """
        Post-process a BridgeEnter event to notify of a call in progress.

        This function will check if the bridge already contains other SIP
        channels. If so, it's interpreted as a call between two channels
        being connected.

        WARNING: This function does not behave as desired for
        bridges with 3+ parties, e.g. conference calls.

        Args:
            channel (Channel): The channel entering the bridge.
            bridge (Bridge): The bridge the channel enters.
        """
        sip_peers = channel.get_bridge_peers_recursive()

        if len(sip_peers) < 2:
            # There are not enough interesting channels to form a call.
            return

        callers = set([peer for peer in sip_peers if peer.is_calling])
        targets = sip_peers - callers

        if len(callers) > 1:
            # Hmm, we have multiple callers. This can happen on an
            # AB-CB-AC transfer. Let's do something ugly.

            # Our oldest caller is going to be the new caller.
            sorted_callers = sorted(
                callers, key=lambda chan: chan.name.rsplit('-', 1)[1])
            caller = sorted_callers.pop(0)

            # The rest are will be marked as targets.
            for non_caller in sorted_callers:
                targets.add(non_caller)
                non_caller.is_calling = False
        elif len(callers) < 1:
            # A call should always have a caller.
            self._logger.warning('Call {} has too few callers: {}'.format(
                channel.linkedid, len(callers)))
            return
        else:
            caller = next(iter(callers))

        if len(targets) != 1:
            # This can happen with a conference call, but is not supported.
            self._logger.warning('Call {} has {} targets.'.format(
                channel.linkedid, len(targets)))
            return
        else:
            target = next(iter(targets))

        # Check and set a flag to prevent the event from being fired again.
        if 'is_picked_up' not in caller.custom:
            caller.custom['is_picked_up'] = True

            self._reporter.on_up(
                caller=caller.as_namedtuple(),
                target=target.as_namedtuple(),
            )

    def on_attended_transfer(self, orig_transferer, second_transferer, event):
        """
        Gets invoked when an attended transfer is completed.

        In an attended transfer, one of the participants of a conversation
        calls a third participant, waits for the third party to answer, talks
        to the third party and then transfers their original conversation
        partner to the third party.

        Args:
            orig_transferer (Channel): The original channel is the channel
            which the redirector used to talk with the person who's being
            transferred.
            second_transferer (Channel): The target channel is the channel
            which the redirector used to set up the call to the person to
            whom the call is being transferred.
            event (dict): The data of the AttendedTransfer event.
        """
        if 'TransfereeUniqueid' in event and 'TransferTargetUniqueid' in event:
            # Nice, Asterisk just told us who the transferee and transfer
            # target are. Let's just do what Asterisk says.
            transferee = self._channels[event['TransfereeUniqueid']]
            target = self._channels[event['TransferTargetUniqueid']]
        else:
            # Ouch, Asterisk didn't tell us who is the transferee and who is
            #  the target, which means we need to figure it out ourselves.

            # We can find both channels in the Destination Bridge.
            target_bridge = self._bridges[event['DestBridgeUniqueid']]

            if len(target_bridge) < 2:
                self._logger.warning(
                    'Attn Xfer DestBridge does not have enough peers for '
                    'event: {!r}'.format(event))
                return

            peer_one, peer_two = target_bridge.peers

            # The next challenge now is to figure out which channel is the
            # transferee and which one is the target..
            if peer_one.linkedid == event['OrigTransfererLinkedid']:
                # Peer one has the same linkedid as the call before the
                # transfer, so it must be the transferee.
                transferee = peer_one
                target = peer_two
            elif peer_two.linkedid == event['OrigTransfererLinkedid']:
                transferee = peer_two
                target = peer_one
            else:
                raise NotImplementedError(
                    'Could not determine caller and target after attended '
                    'transfer - OrigTransfererLinkedid not found. '
                    'OrigTransferer: {}. SecondTransferer: {}. Peers: {}. '
                    'Event: {}.'.format(
                        orig_transferer, second_transferer,
                        target_bridge.peers, event,
                    )
                )

        if transferee.is_local:
            # If the channels were not optimized before the transfer was
            # started, the transferee may be a local channel. To generate the
            # right event, we need to find the real SIP channel which started
            # the transfer.
            for peer in transferee.get_bridge_peers_recursive():
                if peer not in (target, second_transferer, orig_transferer):
                    transferee = peer

        transferee.is_calling = True
        # transferee becomes the new caller, so it should have a valid
        # extension. We can use set it to one of the transfer extensions.
        if event['SecondTransfererExten']:
            transferee.exten = event['SecondTransfererExten']
        elif event['OrigTransfererExten']:
            transferee.exten = event['OrigTransfererExten']
        else:
            transferee.exten = event['TransferTargetCallerIDNum']

        if not transferee.has_extension:
            self._logger.error(
                'Transferee (attn xfer) did not have an extension: '
                '{}'.format(transferee))

        # In some transfer scenarios, a caller can become a target. Because
        # of that, we need to make sure the target is not marked as calling.
        target.is_calling = False

        self._reporter.on_attended_transfer(
            caller=transferee.as_namedtuple(),
            transferer=second_transferer.as_namedtuple(),
            target=target.as_namedtuple(),
        )

        # Prevent a hangup event from being fired for the transfer channels.
        orig_transferer.custom['ignore_a_hangup'] = True
        second_transferer.custom['ignore_a_hangup'] = True

    def on_blind_transfer(self, transferer, transferee, event):
        """
        Handle a blind (cold) transfer event.

        In a blind transfer, one of the call participant transfers their
        conversation partner to a third party. However, unlike with an
        attended transfer, the redirector doesn't wait for the other end to
        pick up, but just punches in the number and sends their conversation
        party away. Because of this, multiple phones may actually be addressed
        by this transfer, hence the multiple targets. The real participant can
        be recovered later on when someone answers the transferred call.

        This Transfer event is earlier than the dial. We mark it and
        wait for the b_dial event. In on_b_dial we send out both the
        on_b_dial and the on_transfer.

        Args:
            transferer (Channel): The channel referring to another extension.
            transferee (Channel): The channel being referred.
            event (dict): The data of the BlindTransfer event.
        """
        transferee.custom['raw_blind_transfer'] = transferer

        # Remove the is_picked_up flag so we can figure a new in-progress
        # event when the transfer target picks up.
        try:
            del transferee.custom['is_picked_up']
        except KeyError:
            pass

        # Prevent a hangup event from being fired for the transfer channels.
        transferer.custom['ignore_a_hangup'] = True

        # Make it look like the transferee is calling the transfer extension.
        transferee.is_calling = True

        transferee.exten = event['Extension']
        transferer.exten = event['Extension']

    def on_blonde_transfer(self, orig_transferer, second_transferer, event):
        """
        Handle the AttendedTransfer event for a blonde transfer.

        A blonde is a middle road between blind transfers and attended
        transfers. With a blond transfer, the redirector requests an attended
        transfer but doesn't wait for the receiving end to pick up. Since the
        data of blind and blonde transfers looks identical, they don't have
        special hooks.

        Args:
            orig_transferer (Channel): The original channel is the channel
            which the redirector used to talk with the person who's being
            transferred.
            second_transferer (Channel): The target channel is the channel
            which the redirector used to set up the call to the person to
            whom the call is being transferred.
            event (dict): The AttendedTransfer event.
        """
        transferee = self._channels[event['TransfereeUniqueid']]

        # Remove the is_picked_up flag so we can figure a new in-progress
        # event when the transfer target picks up.
        try:
            del transferee.custom['is_picked_up']
        except KeyError:
            pass

        # Make it look like the transferee is calling the transfer extension.
        transferee.is_calling = True
        transferee.exten = second_transferer.exten

        if not transferee.has_extension:
            self._logger.error(
                'Transferee (blonde xfer) did not have an extension: '
                '{}'.format(transferee))

        targets = second_transferer.get_dialed_channels().union(
            transferee.get_dialed_channels())

        self._reporter.on_blonde_transfer(
            caller=transferee.as_namedtuple(),
            transferer=second_transferer.as_namedtuple(),
            targets=[target.as_namedtuple() for target in targets],
        )

        # Prevent a hangup event from being fired for the transfer channels.
        orig_transferer.custom['ignore_a_hangup'] = True
        second_transferer.custom['ignore_a_hangup'] = True

    def on_user_event(self, event):
        """
        Handle custom UserEvent messages from Asterisk.

        Adding user events to a dial plan is a useful way to send additional
        information to Cacofonisk. You could add additional user info,
        parameters used for processing the events and more.

        Args:
            event (dict): Dict-like object with all attributes of the event.
        """
        self._reporter.on_user_event(self._channels[event['Uniqueid']].as_namedtuple(), event)

    def on_hangup(self, channel, event):
        """
        Process the channel just before it is hung up.

        Args:
            channel (Channel): The channel being disconnected.
            event (dict): The Hangup event data.
        """
        if channel.is_local:
            return

        if 'raw_blind_transfer' in channel.custom:
            # Panic! This channel had a blind transfer coming up but it's
            # being hung up! That probably means the blind transfer target
            # could not be reached.
            # Ideally, we would simulate a full blind transfer having been
            # completed but hung up with an error. However, no channel
            # to the third party has been created.
            redirector = channel.custom.pop('raw_blind_transfer')

            a_chan = redirector if redirector.is_calling else channel

            # TODO: Maybe give another status code than 'completed' here?
            self._reporter.on_hangup(
                caller=a_chan.as_namedtuple(),
                reason='completed',
            )

        elif 'ignore_a_hangup' in channel.custom:
            # This is a calling channel which performed an attended
            # transfer. Because the call has already been "hung up"
            # with the transfer, we shouldn't send a hangup notification.
            pass

        elif channel.is_calling:
            # The caller is being disconnected, so we should notify the
            # user.
            self._reporter.on_hangup(
                caller=channel.as_namedtuple(),
                reason=self._hangup_reason(channel, event),
            )

    def _hangup_reason(self, channel, event):
        """
        Map the Asterisk hangup causes to easy to understand strings.

        Args:
            channel (Channel): The channel which is hung up.
            event (Event): The data of the event.
        """
        hangup_cause = int(event['Cause'])

        # See https://wiki.asterisk.org/wiki/display/AST/Hangup+Cause+Mappings
        if hangup_cause == AST_CAUSE_NORMAL_CLEARING:
            # If channel is not up, the call never really connected.
            # This happens when call confirmation is unsuccessful.
            if channel.state == AST_STATE_UP:
                return 'completed'
            else:
                return 'no-answer'
        elif hangup_cause == AST_CAUSE_USER_BUSY:
            return 'busy'
        elif hangup_cause in (AST_CAUSE_NO_USER_RESPONSE, AST_CAUSE_NO_ANSWER):
            return 'no-answer'
        elif hangup_cause == AST_CAUSE_ANSWERED_ELSEWHERE:
            return 'answered-elsewhere'
        elif hangup_cause == AST_CAUSE_CALL_REJECTED:
            return 'rejected'
        elif hangup_cause == AST_CAUSE_UNKNOWN or hangup_cause == AST_CAUSE_INTERWORKING:
            # Sometimes Asterisk doesn't set a proper hangup cause.
            # If our a_chan is already up, this probably means the
            # call was successful. If not, that means the caller hung up,
            # which we assign the "cancelled" status.
            if channel.state == AST_STATE_UP:
                return 'completed'
            else:
                return 'cancelled'
        else:
            return 'failed'
