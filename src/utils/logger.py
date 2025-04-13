from dotenv import load_dotenv
import logging
import os

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL")
MAX_LOG_LENGTH = 2000

class TruncatingLogger(logging.Logger):
    def _log(self, level, msg, args, **kwargs):
        if isinstance(msg, str) and len(msg) > MAX_LOG_LENGTH:
            msg = msg[:MAX_LOG_LENGTH] + "... [truncated]"
        super()._log(level, msg, args, **kwargs)

logging.setLoggerClass(TruncatingLogger)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s",
    handlers=[logging.StreamHandler()]
)

def getLogger(name):
    return logging.getLogger(name)