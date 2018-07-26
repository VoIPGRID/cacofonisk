import logging
import sys

from cacofonisk import FileRunner, LoggingReporter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter(
    '%(asctime)s %(name)s: %(levelname)s: %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

reporter = LoggingReporter()
# Process the specified AMI fixture.
runner = FileRunner(
    '../tests/fixtures/simple/ab_success_b_hangup.json', reporter)
runner.run()
reporter.close()
