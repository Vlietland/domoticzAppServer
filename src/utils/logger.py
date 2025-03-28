from dotenv import load_dotenv
import logging
import os

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s",
    handlers=[logging.StreamHandler()]
)

def getLogger(name):
    return logging.getLogger(name)
