class BaseReporter(object):
    """
    BaseReporter is a skeleton baseclass for any Reporter classes. The methods
    can be overwritten. See class:`ChannelManager` to see where these methods
    are called.
    """
    def trace_ami(self, event):
        "Called on incoming AMI events."
        pass

    def trace_msg(self, msg):
        "Called on trace messages."
        pass

    def finalize(self):
        "Called on end, so any buffered output can be flushed."
        pass

    def on_event(self, event):
        pass

    def on_transfer(self):
        pass

    def on_b_dial(self, caller, callee):
        pass
