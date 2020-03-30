from datetime import datetime, timedelta

DEFAULT_EXECUTION_TIMEOUT = timedelta(minutes=2)
DEFAULT_RETRIES = 1
DEFAULT_RETRY_DELAY = timedelta(minutes=2)
DEFAULT_START_DATE = datetime.today() - timedelta(minutes = 0.5)
