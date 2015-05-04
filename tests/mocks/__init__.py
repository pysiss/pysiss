""" file: __init__.py (pysiss.tests.mocks)
"""

import logging.config
from pysiss._log_config import LOG_CONFIG
logging.config.dictConfig(LOG_CONFIG)

PRINT_INTERCEPTIONS = False
