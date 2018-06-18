class MissingBridgeUniqueid(KeyError):
    pass


class Bridge(object):
    """
    The Bridge object represents a Bridge in Asterisk.

    With Asterisk 12+, Asterisk creates bridges and puts channels into them to
    make audio flow between the channels. This class is a Python representation
    of such bridges.
    """

    def __init__(self, event):
        """
        Create a new bridge object.

        Args:
            event (Event): A BridgeCreate event.
        """
        self.uniqueid = event['BridgeUniqueid']
        self.type = event['BridgeType']
        self.technology = event['BridgeTechnology']
        self.creator = event['BridgeCreator']
        self.video_source_mode = event['BridgeVideoSourceMode']

        self.peers = set()

    def __len__(self):
        """
        Get the number of channels in this bridge.

        Returns:
            int: The number of channels in this bridge.
        """
        return len(self.peers)

    def __repr__(self):
        """
        Get a textual representation of this bridge.

        Returns:
            str: A representation of this bridge.
        """
        return '<Bridge(id={self.uniqueid},peers={peers})>'.format(
            self=self,
            peers=','.join([chan.name for chan in self.peers]),
        )


class BridgeDict(dict):
    """
    A dict which raises a MissingBridgeUniqueid exception if a key is missing.
    """

    def __getitem__(self, item):
        try:
            return super(BridgeDict, self).__getitem__(item)
        except KeyError:
            raise MissingBridgeUniqueid(item)
