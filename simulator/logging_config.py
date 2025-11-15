# simulator/logging_config.py
import logging
import sys

# Set up the configuration right here at the top level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def get_logger(name):
    """A simple helper to get a named logger."""
    return logging.getLogger(name)
