# Cacofonisk

Cacofonisk is a framework that connects to the Asterisk PBX, listens to events
on the Asterisk Management Interface (AMI) and tracks the status of calls
currently in progress in Asterisk.

Cacofonisk takes a stream of AMI events as input and uses these to keep track
of the channels currently active in Asterisk and how they are related. When
something interesting happens to one of the channels, it will call a method on
a call state Reporter with interesting information about the call, like who is
in the call, and a unique identifier.

This data can then be used to send webhooks regarding a call, to notify a
person who is being called, or to log calls being performed.

## Status

This product is actively being developed and used at VoIPGRID.

## Usage

### Requirements

- Python >= 3.4
- Panoramisk 1.x
- Asterisk >= 12

### Installation

Cacofonisk is available on Pypi so you can easily install it with pip:

```bash
$ pip install cacofonisk
```

To install the dependencies from source:

```bash
$ python3 setup.py install
```

### Running

To run Cacofonisk, you will need two things: a Runner and a Reporter.

A Runner is a class which is responsible for passing AMI events to the
Cacofonisk. Two runners are included: an AmiRunner (which connects to the
Asterisk Management Interface) and a FileRunner (which imports AMI events from
a JSON file).

A Reporter is a class which takes the interesting data from Cacofonisk and does
awesome things with it. You can find various Reporters in the `examples`
folder.

To create your own reporter, you can extend the BaseReporter class and
implement your own event handlers, like so:

```python
from cacofonisk import AmiRunner, BaseReporter


class ReportAllTheThings(BaseReporter):

    def on_b_dial(self, caller, targets):
        target_channels = [target.name for target in targets]
        caller_number = caller.caller_id.num
        print("{} is now calling {}".format(
            caller_number, ', '.join(target_channels),
        ))

    def on_up(self, caller, target):
        target_number = target.caller_id.num
        caller_number = caller.caller_id.num
        print("{} is now in conversation with {}".format(caller_number, target_number))

    def on_hangup(self, caller, reason):
        caller_number = caller.caller_id.num
        print("{} is no longer calling (reason: {})".format(caller_number, reason))


reporter = ReportAllTheThings()
runner = AmiRunner(['tcp://username:password@127.0.0.1:5038'], reporter)
runner.run()
```

This reporter can then be passed to a Runner of your choice to process AMI
events.

For more information about the parameters of the reporter, please see the docs
in BaseReporter.

You can also listen for
[UserEvents](https://wiki.asterisk.org/wiki/display/AST/Asterisk+13+Application_UserEvent)
using the `on_user_event` function. This can be used to pass additional data
from Asterisk to your Cacofonisk application.

#### Running the tests

To run the test suite:

```bash
$ python3 -m unittest
```

## Contributing

See the [CONTRIBUTING.md](CONTRIBUTING.md) file on how to contribute to this project.

## Contributors

See the [CONTRIBUTORS.md](CONTRIBUTORS.md) file for a list of contributors to the project.

## Roadmap

### Changelog

The changelog can be found in the [CHANGELOG.md](CHANGELOG.md) file.

### In progress

No features are currently in progress.

### Future

No features are currently scheduled. Have great ideas? Please don't hesitate to share them!

## Get in touch with a developer

If you want to report an issue see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more info.

We will be happy to answer your other questions at opensource@wearespindle.com.

## License

Cacofonisk is made available under the MIT license. See the [LICENSE file](LICENSE) for more info.
