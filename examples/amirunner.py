import logging
import sys

from cacofonisk import AmiRunner, LoggingReporter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter(
    '%(asctime)s %(name)s: %(levelname)s: %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)


reporter = LoggingReporter()
# Attach the AmiRunner to the specified Asterisk.
runner = AmiRunner([
    'tcp://cacofonisk:bard@127.0.0.1:5038',
], reporter, logger=logger)
runner.run()
