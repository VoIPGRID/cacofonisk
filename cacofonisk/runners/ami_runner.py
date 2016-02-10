import asyncio
from panoramisk import Manager

from ..channel import ChannelManager


class ChannelManagerAdapterMixin(object):
    """
    ChannelManager adapted to Panoramisk.

    The adapter is used to adapt the events as fed by class:`panoramisk.Manager`
    to the type of events that the ChannelManager takes.
    """
    @staticmethod
    def factory(channel_manager):
        """
        factory returns an instance of ChannelManager that mixes in
        ChannelManagerAdapterMixin with the supplied `channel_manager`
        """
        class AdaptedChannelManager(ChannelManagerAdapterMixin, channel_manager):
            pass
        return AdaptedChannelManager

    def _pre_connect(self, amimgr):
        """
        _pre_connect sets meth:`on_event` as as the callback for all events
        defined in attr:`INTERESTING_EVENTS`.
        """
        for event_name in self.INTERESTING_EVENTS:
            amimgr.register_event(event_name, self.on_event)

    def on_event(self, amimanager, amievent):
        """
        on_event is called everytime the Panoramisk Manager instance encounters
        an interesting event.

        It is called with the amimanager and an amievent. We drop the
        amimanager, because we don't need it.
        """
        return super().on_event(amievent)


class AmiRunner(object):
    """
    A Runner which reads Asterisk AMI events and passes them to a
    ChannelManager instance.
    """
    def __init__(self, amihosts, reporter, channel_manager=ChannelManager):
        """
        Args:
            amihosts [dict]: A list of dictionaries.
        """
        self.amihosts = amihosts
        self.reporter = reporter
        self.channel_manager = ChannelManagerAdapterMixin.factory(channel_manager)
        self.loop = asyncio.get_event_loop()

    def attach_all(self):
        """
        attach_all attaches a channelmanager to all amihosts defined in
        self.amihosts by calling meth:`attach` on all of them.
        """
        assert not hasattr(self, 'amimgrs')
        assert not hasattr(self, 'channel_managers')
        self.amimgrs = []
        self.channel_managers = []

        for amihost in self.amihosts:
            self.attach(amihost)

    def attach(self, amihost):
        """
        attach amihost to a ChannelManager.

        Args:
            amihost (dict): A dictionary containing the connection settings for
                an AMI host.
        """
        # Create Panoramisk asterisk AMI manager.
        amimgr = Manager(
            loop=self.loop, host=amihost['host'], port=amihost['port'],
            username=amihost['username'], secret=amihost['password'],
            ssl=False, encoding='utf8')

        # Create our own channel manager.
        channel_manager = self.channel_manager(
            reporter=self.reporter,
        )

        # Tell Panoramisk to which events we want to listen.
        channel_manager._pre_connect(amimgr)

        # Record them for later use.
        self.amimgrs.append(amimgr)
        self.channel_managers.append(channel_manager)

        # Tell asyncio what to work on.
        asyncio.async(amimgr.connect())

    def run(self):
        """
        Start the runner and run until halted.
        """
        self.attach_all()
        self.loop.run_forever()
