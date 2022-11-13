import logging
import os

from core.models import (
    configure_logging,
    getLogger,
)

temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

log_file_name = os.path.join(temp_dir, f"app.log")

logger = getLogger(__name__)

level_text = "INFO"
logging_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}
logger.line()
log_level = logging_levels.get(level_text)
if log_level is None:
    # log_level = self.config.remove("log_level")
    logger.warning("Invalid logging level set: %s.", level_text)
    logger.warning("Using default logging level: INFO.")
else:
    logger.info("Logging level: %s", level_text)
logger.info("Log file: %s", log_file_name)
configure_logging(log_file_name, log_level)
logger.debug("Successfully configured logging.")
