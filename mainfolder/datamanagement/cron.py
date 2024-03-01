

import logging
from datamanagement.helpful_scripts.strategy import run_strategy
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger('dev_log')
error = logging.getLogger('error_log')
i=0
def do_something():
    logger.info("LOGGING STARTED")
    strat = run_strategy()
    value=strat.run()


def my_scheduled_job():
    i+=1
    logger.info(f"LOGGING STARTED {i}")
    # strat = run_strategy()
    # value=strat.run()

