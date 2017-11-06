Cacofonisk
==========

.. image:: https://travis-ci.org/VoIPGRID/cacofonisk.svg?branch=master
    :target: https://travis-ci.org/VoIPGRID/cacofonisk

Cacofonisk is a framework that connects to the Asterisk PBX, listens to AMI
events and records CallerIDs and CallerID changes on call transfers.

Cacofonisk takes a stream of AMI events as input and translates these to channel
objects. At relevant moments in a call, these channel objects can be used to get
information about the active call and do anything with that information. For
example you may want get a signal everytime that a call is transferred. When a
call is transferred, you may want to know which account is initiating the
transfer, what the callerid is for the call he is transferring and to which
extension the call is being transferred. All this information is available in
Cacafonisk. You may want to write it to file, but this being the 21st century,
you may also want to send it to a url.

Cacofonisk is built on the pretty awesome `Panoramisk
<https://github.com/gawel/panoramisk>`_ library to listen to the AMI.

Installation and testing
------------------------

Cacofonisk can be installed from pypi:

.. code-block:: console

    $ pip install cacofonisk

To install from source, run:

.. code-block:: console

    $ python3 setup.py install

To run tests, run:

.. code-block:: console

    $ python3 setup.py nosetests


Example
-------
for example, to implement the above scenario in cacofonisk, you would do the
following. in ``my_transfer_spammer.py`` you would overwrite ``on_transfer``
like:

To get a notification for everytime an account is ringing and when a transfer is
performed. Write the following to ``report_all_the_things.py``:

.. code-block:: python

    from cacofonisk import AmiRunner, BaseReporter


    class ReportAllTheThings(BaseReporter):
        def __init__(self, *args, **kwargs):
            self.cloudcti_accounts = set()

        def on_b_dial(self, call_id, caller, callee):
            callee_account_code = callee.code
            caller_id = caller.number
            print("{} is being called by {}".format(callee_account_code, caller_id))

        def on_up(self, call_id, caller, callee):
            callee_account_code = callee.code
            caller_id = caller.number
            print("{} is now in conversation with {}".format(callee_account_code, caller_id))

        def on_warm_transfer(self, call_id, redirector, party1, party2):
            print("Account with account code {redirector.account_code} just "
                  "transferred a call with callerid {party1.cli} to an extension at "
                  "{party2.exten}".format(redirector, party1, party2))

        def on_hangup(self, call_id, caller, callee, reason):
            print("{} and {} are no longer calling (reason: {})".format(caller, callee, reason))

  if __name__ == '__main__':
      ami_host = {'host': '127.0.0.1', 'username': 'cacofonisk', 'password': 'bard', 'port': 5038}
      ami_hosts = (ami_host,)

      reporter = ReportAllTheThings()
      runner = AmiRunner(ami_hosts, reporter)
      runner.run()

If you run this like:

.. code-block:: console

    $ python3 report_all_the_things.py

You will see a message printed to the console for every account that is ringing
or transferred.

You can also listen for `UserEvents
<https://wiki.asterisk.org/wiki/display/AST/Asterisk+11+Application_UserEvent>`_.
This can be used to trigger actions based on User defined events in the
dialplan.

Development
===========

Setup:
------

.. code-block:: console

    $ mkvirtualenv cacofonisk --python=`which python3`
    $ pip install -r requirements.txt

Make sure your test user has ``read=all`` event powers in asterisk and
restart asterisk:

Testing:
--------

To make (automated) testing easier, it is possible to let Cacofonisk read events from different sources than AMI. To read files from a json file, the default runner can overwritten to use the ``FileRunner``:

.. code-block:: python

    from cacofonisk import BaseReporter, FileRunner

    class TransferSpammer(BaseReporter):
        def on_transfer(self, redirector, party1, party2):
            print("Account with account code {redirector.account_code} just "
                  "transferred a call with callerid {party1.cli} to an extension at "
                  "{party2.exten}".format(redirector, party1, party2))

    if __name__ == "__main__":
        reporter = TransferSpammer()
        runner = FileRunner("path/to/file.json", reporter)
        runner.run()

Running this script will read events from the specified file. You can see examples for this kind of files in ``examples``. To generate your own json, you can do

.. code-block:: python

    from cacofonisk import JsonReporter

    if __name__ == "__main__":
        ami_host = {'host': '127.0.0.1', 'username': 'cacofonisk', 'password': 'bard', 'port': 5038}
        ami_hosts = (ami_host,)

        reporter = JsonReporter('path/to/file.json')
        runner = AmiRunner(ami_hosts, reporter)
        runner.run()
            
Concepts
========

Runners
-------

The ChannelManager operates on a stream of channelevents such as are emitted by
the AMI of one or more Asterisken. 'runners' can be set on a Cacofonisk instance
to specify where the events come frome. In production, cacofonisk would listen
to an actual AMI. For this purpose, ``cacofonisk.AmiRunner`` can be used.

For (automated) tests it is more convenient to read events from a file. To make
this possible, cacofonisk makes it possible to convert a stream of AMI events to
a list of json objects, and write them to a file using the JsonReporter. Such a file can be
replayed using ``cacofonisk.JsonFileRunner``.

All runners should be passed a ``Reporter`` instance.

To start the runner, runner.run() is used:

.. code-block:: python

    from cacofonisk import AmiRunner, JsonFileRunner, DebugReporter

    reporter = DebugReporter()
    # To attach the AmiRunner
    runner = AmiRunner([(ami_host, ami_user, ami_secret),], reporter)
    runner.run()

    # To attach the JsonFileRunner
    runner = JsonFileRunner('path/to/file.json', reporter)
    runner.run()

Reporter
--------
The reporter is attached to the ChannelManager. It has an ``on_ami_event`` method
that is called for every AMI event that is encountered. When no reporter is
specified, the ChannelManager will use the default reporter at `verbosity=0`. In
effect this means that no information will be displayed.

The JsonReporter is used to generate json files from AMI events. To do this,
specify the JsonReporter on cacofonisk as follows:

.. code-block:: python

    from cacofonisk import AmiRunner, JsonReporter

    reporter = JsonFileReporter('path/to/file.json')
    # To attach the AmiRunner
    runner = AmiRunner([(ami_host, ami_user, ami_secret),], reporter)
    runner.run()

This will create a file containing all AMI events for the duration of the run at
the specified path.

The ``DebugReporter`` can be used to get detailed reports of events within the
ChannelManager. It prints information to stdout.


The ChannelManager
------------------

A ChannelManager is instantiated for every input source. So that if three AMI
interfaces are set on the runner, three ChannelManagers will be active. The
ChannelManager is a central part of the way in which Cacofonisk functions. It
contains all the logic that decides about which channels are logically in one
conversation and which channel is associated with which part of the call.

For most uses however, it is not necessary to access the ChannelManager
directly, because the Reporter probably has all the needed information
available. If it is needed to make changes to the ChannelManager, a subclass of
ChannelManager can be passed to the runner:

.. code-block:: python

    from cacofonisk import AmiRunner, BaseReporter, ChannelManager


    class MyAwesomeChannelManager(ChannelManager):
        def on_event(self, event):
            super().on_event(event)
            print("Never gonna give you up!")

    reporter = BaseReporter()
    channel_manager = MyAwesomeChannelManager()
    runner = AmiRunner(ami_hosts, reporter, channel_manager)
    runner.run()


Channel
-------

The ChannelManager operates on Channels. These can be linked, unlinked, masqueraded and destroyed just like any Asterisk Channel. This operations are pretty lowlevel, but there is one very nifty use of Channel. Information can be added to the dictionary at ``Channel.custom``. This dictionary is retained when a Channel is masqueraded.


CallerId
--------

The CallerId contains the following information about participants in a call:

 * code: The accountcode.
 * name: The callerid name.
 * number: The callerid number.
 * is_public: Whether or not the participant wants to share this information.

The CallerId is passed to the ``on_b_dial`` and ``on_transfer`` methods of a
reporter.

Writing tests
-------------

A testcase can be written that reads from a json eventlog. Below is an example
for a test that makes sure that events are found at all.

.. code-block:: python

    from cacofonisk.utils.testcases import BaseTestCase, SilentReporter
    from cacofonisk.channel import ChannelManager


    class TestReporter(SilentReporter):
        """
        A report that increments the property ``no_of_events`` by one, every
        time ``on_event()`` is called.
        """
        def __init__(self, *args, **kwargs):
            self.total_events = 0

        def on_event(self, event):
            self.total_events += 1


    class MyVeryOwnTestCase(BaseTestCase):
        """
        Test my very own code.
        """
        def test_events_come_in(self):
            """
            Play a log and test that events are coming in.
            """
            reporter = TestReporter()

            events = self.load_events_from_disk(
                            '/path/to/event_file.json'
                    )
            chanmgr = ChannelManager(reporter=reporter)
            for event in events:
                chanmgr.on_event(event)

            self.assertNotEqual(reporter.no_of_events, 0)
