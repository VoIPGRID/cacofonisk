# Changelog

## 0.5.0 - AMI v2

- Upgrade Cacofonisk to work with AMI v2 (Asterisk 12+). **WARNING**: This
change is not backwards compatible. If you use Asterisk <11, you can keep using
version 0.4.0.
- Rename ChannelManager to EventHandler and decouple Asterisk channel tracking
from (opinionated) call tracking.
- Reporters now get immutable copies of Channels rather than CallerId objects,
so it's possible to analyze more channel attributes in the reporter.
- `trace_msg` and `trace_ami` have been removed in favor of proper logging
facilities.

## 0.4.0 - ConnectAB

- Add support for calls where Asterisk calls and connects both parties.

## 0.3.0 - Fixed Destinations

- Calls to external phone numbers (rather than just phone accounts) are now
tracked correctly.
- The `on_transfer` hook was split to `on_warm_transfer` (for attended
transfers) and `on_cold_transfer` (for blind and blonde transfers), with
different method signatures.
- The `on_b_dial` events for a single call have been merged. If multiple
destinations start to ring for a single call, one `on_b_dial` event will be
triggered with a list of CallerId objects.
- The `on_pickup` event was removed. You can compare the data from the
`on_b_dial` call with the `on_up` call to see whether the callee's phone rang.

## 0.2.2 - Cancelled Calls

- Fix issue where calls which were hung up by the caller before being answered
were not tracked correctly.

## 0.2.1 - Call Confirmation

- Fix issue where `on_up` would trigger before both call parties were connected.
This issue was most prevalent when one party needed to perform additional steps
before the call was patched through (like pressing a button).

## 0.2.0 - Queues

- Calls passed through the Queue app are now tracked correctly (requires the
`eventwhencalled` flag to be enabled).

## 0.1.0 - Ups and Downs

- Major refactor of the existing code.
- Add `on_up` and `on_hangup` events.
- Add `call_id` to uniquely identify a call (based on the source channel's
UniqueId, just like Asterisk's LinkedId).
