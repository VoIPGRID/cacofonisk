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

file = '/dev/stdin'
if len(sys.argv) == 2:
    file = sys.argv[1]

reporter = LoggingReporter()
# Process the specified AMI fixture.
runner = FileRunner(file, reporter)
runner.run()
reporter.close()
