"""
This example connects to the specified AMI hosts and prints a message when an
account is ringing and when a call is transferred.
"""
from cacofonisk import AmiRunner, BaseReporter


class TransferSpammer(BaseReporter):

    def on_event(self, event):
        pass

    def on_b_dial(self, caller, callee):
        callee_account_code = callee.code
        caller_id = caller.number
        print("{callee.code} is being called by {caller.number}".format(callee=callee, caller=caller))

    def on_warm_transfer(self, redirector, party1, party2):
        print("Account with account code {redirector.account_code} just "
                "transferred a call with callerid {party1.cli} to an extension at "
                "{party2.exten}".format(
                    redirector=redirector, party1=party1,
                    party2=party2))

if __name__ == '__main__':
    ami_host1 = {'host': '127.0.0.1', 'username': 'cacofonisk', 'password': 'bard', 'port': 5038}
    ami_hosts = (ami_host1,)

    reporter = TransferSpammer()
    runner = AmiRunner(ami_hosts, reporter)
    runner.run()
