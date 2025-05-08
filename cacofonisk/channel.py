from collections import namedtuple

from cacofonisk.callerid import CallerId


class MissingUniqueid(KeyError):
    pass


class Channel(object):
    """
    A Channel holds Asterisk channel state.

    It can be dialed, bridge, and updated with new data. All of the above is
    typical low level Asterisk channel behaviour.
    """

    def __init__(self, event):
        """
        Create a new channel instance.

        Args:
            event (dict): The attributes of a Newchannel event.
        """
        self.name = event['Channel']
        self.uniqueid = event['Uniqueid']
        self.linkedid = event['Linkedid']
        self.state = int(event['ChannelState'])
        self.exten = event['Exten']
        self.account_code = event['AccountCode']
        self.cid_calling_pres = None
        self.caller_id = CallerId(
            name=event['CallerIDName'],
            num=event['CallerIDNum'],
        )
        self.connected_line = CallerId(
            name=event['ConnectedLineName'],
            num=event['ConnectedLineNum'],
        )

        # Create vars which are used to store generated data based on other
        # events from Asterisk.
        self.fwd_local_bridge = None
        self.back_local_bridge = None
        self.back_dial = None
        self.fwd_dials = []
        self.bridge = None
        self.is_originated = False
        self.is_calling = self.uniqueid == self.linkedid

        # The Custom dict can be used to store custom data.
        self.custom = {}

    def __repr__(self):
        return (
            '<Channel('
            'name={self.name!r} '
            'id={self.uniqueid!r} '
            'linkedid={self.linkedid!r} '
            'forward_local_bridge={next} '
            'backward_local_bridge={prev} '
            'state={self.state!r} '
            'cli="{self.caller_id.name!r}" <{self.caller_id.num!r}> '
            'exten={self.exten})>').format(
            self=self,
            next=(self.fwd_local_bridge and self.fwd_local_bridge.name),
            prev=(self.back_local_bridge and self.back_local_bridge.name))

    @property
    def is_local(self):
        """
        Whether the current channel is a local channel.

        A connection to Asterisk consist of two parts, an internal connection
        and an external connection. The internal connection is prefixed
        with 'Local/', whereas a external connection is prefixed with 'SIP/'.

        Returns:
            bool: True if the channel is local, false otherwise.
        """
        return self.name.startswith('Local/')

    @property
    def has_extension(self):
        """
        Check if the channel has a valid extension (not empty or star signal).

        Calling channels in Asterisk typically have an extension which
        tells Asterisk where it should direct the call. Checking whether the
        channel has an extension is usually a good indicator to determine
        whether the channel is calling or not.

        Returns:
            bool: Whether the channel has a valid extension.
        """
        return (
                self.exten and self.exten != 's' and
                not self.exten.startswith('*')
        )

    def get_dialing_channel(self):
        """
        Figure out on whose channel's behalf we're calling.

        When a channel is not bridged yet, you can use this on the
        B-channel to figure out which A-channel initiated the call.

        Returns:
            Channel: The master channel dialing this channel.
        """
        if self.back_dial:
            # Check if we are being dialed.
            a_chan = self.back_dial
        else:
            # This is the root channel.
            a_chan = None

        # If our a_chan has a local bridge, use the back part of that bridge
        # to check for further dials.
        if a_chan and a_chan.back_local_bridge:
            a_chan = a_chan.back_local_bridge

        # If we have an incoming channel, recurse through the channels to find
        # the true origin channel. If we don't have one, it means we're the
        # origin channel.
        return a_chan.get_dialing_channel() if a_chan else self

    def get_dialed_channels(self):
        """
        Figure out which channels are calling on our behalf.

        When a channel is not bridged yet, you can use this on the
        A-channel to find out which channels are dialed on behalf of
        this channel.

        It works like this:

        * A-channel (this) has a list of _fwd_dials items (open
          dials).
        * We loop over those (a list of uniqueids) and find the
          corresponding channels.
        * Those channels may be SIP channels, or they can be local
          channels, in which case we have to look further (by calling
          this function on those channels).

        Returns:
            set: A set of all channels being dialed by this channel.
        """
        b_channels = set()

        b_chans = self.fwd_dials

        for b_chan in b_chans:
            # Likely, b_chan.fwd_local_bridge is None, in which case we're
            # looking at a real tech channel (non-Local).
            # Or, the b_chan has one.fwd_local_bridge, after which we have
            # to call this function again.
            if b_chan.fwd_local_bridge:
                b_chan = b_chan.fwd_local_bridge

                assert not b_chan.fwd_local_bridge, (
                    'Since when does asterisk do double links? b_chan={!r}'
                    .format(b_chan)
                )

                b_channels.update(b_chan.get_dialed_channels())
            else:
                assert not b_chan.fwd_dials
                b_channels.add(b_chan)

        return b_channels

    def get_bridge_peers_recursive(self):
        """
        Traverse (local) bridges recursively and get all non-Local channels.

        Uses _get_peers_recursive to traverse the local and non-local
        bridges recursively, but also checks the local bridges of self for
        more channels.

        This cannot be done in one step, as doing so would cause a recursion
        loop while traversing the same local bridge back and forth.

        Returns:
            set: A set of non-local Channels.
        """
        peers = self._bridge_peers_recurse()

        if self.fwd_local_bridge:
            fwd_peers = self.fwd_local_bridge._bridge_peers_recurse()
            for peer in fwd_peers:
                peers.add(peer)

        if self.back_local_bridge:
            back_peers = self.back_local_bridge._bridge_peers_recurse()
            for peer in back_peers:
                peers.add(peer)

        return peers

    def _bridge_peers_recurse(self):
        """
        The recursive step of get_bridge_peers_recursive.

        This function finds the non-Local channels of the current bridge,
        as well as the non-Local channels of the channels linked through
        local bridges.

        Returns:
            set: A set of non-local Channels.
        """
        if not self.bridge:
            return set()

        peers = set()

        if not self.is_local:
            peers.add(self)

        for peer in [peer for peer in self.bridge.peers if peer != self]:
            if not peer.is_local:
                peers.add(peer)
            elif peer.is_local and peer.fwd_local_bridge:
                rec_peers = peer.fwd_local_bridge._bridge_peers_recurse()

                for recursive_peer in rec_peers:
                    peers.add(recursive_peer)
            elif peer.is_local and peer.back_local_bridge:
                rec_peers = peer.back_local_bridge._bridge_peers_recurse()

                for recursive_peer in rec_peers:
                    peers.add(recursive_peer)

        return peers

    def as_namedtuple(self):
        """
        Convert Channel to a SimpleChannel, so it's safe to pass to a reporter.

        Returns:
            SimpleChannel: A SimpleChannel with the data of this channel.
        """
        fields = SimpleChannel._fields

        return SimpleChannel(
            **{field: getattr(self, field) for field in fields})


class ChannelDict(dict):
    """
    ChannelDict is a dict which raises a MissingUniqueid if the key is missing.
    """

    def __getitem__(self, item):
        try:
            return super(ChannelDict, self).__getitem__(item)
        except KeyError:
            raise MissingUniqueid(item)


class SimpleChannel(namedtuple(
    'SimpleChannelBase', 'name uniqueid linkedid account_code caller_id '
                         'cid_calling_pres connected_line exten state'
)):
    def replace(self, **kwargs):
        """
        Make the _replace method public.

        Args:
            **kwargs: The fields to replace.

        Returns:
            A new instance of SimpleChannel.
        """
        return self._replace(**kwargs)
