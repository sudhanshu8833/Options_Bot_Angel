

import logging
from datamanagement.helpful_scripts.strategy import run_strategy
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger('dev_log')
error = logging.getLogger('error_log')

def do_something():
    logger.info("LOGGING STARTED")
    strat = run_strategy()
    value=strat.run()


def my_scheduled_job():
    logger.info("LOGGING STARTED")
    strat = run_strategy()
    value=strat.run()

