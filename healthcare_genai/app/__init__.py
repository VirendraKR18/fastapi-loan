import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv('.env')

# Define a custom filter to exclude 404 errors
class ExcludeSpecificMessagesFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        return (
            "Not Found:" not in message and
            "Forbidden" not in message and
            "Invalid HTTP_HOST header" not in message and
            "Bad Request" not in message and
            "HTTP Request:" not in message and
            "Redirecting" not in message and
            "Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None))" not in message and
            "Connection pool is full, discarding connection" not in message and
            "Forbidden" not in message
        )

logging_str = "%(asctime)s [%(levelname)-8s] %(message)s"
# log_dir = "logs"
 
# log_filepath = os.path.join(log_dir, os.getenv("LOG_FILENAME"))
log_filepath = os.getenv("LOG_FILENAME")
# os.makedirs(log_dir, exist_ok=True)

# Create the custom filter instance
exclude_specific_messages_filter = ExcludeSpecificMessagesFilter()

logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.FileHandler(log_filepath),
        # logging.StreamHandler(sys.stdout)
    ]
)

# Apply the filter to the handlers
for handler in logging.getLogger().handlers:
    handler.addFilter(exclude_specific_messages_filter)
 
logger = logging.getLogger("kanini")
