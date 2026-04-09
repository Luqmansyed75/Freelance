import logging
import datetime
import os

# 1. Create the 'logs' directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 2. Set the path inside the 'logs' folder
log_filename = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.log")

# 3. Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname).1s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(log_filename),
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Project started. Logs are being saved to the /logs folder.")