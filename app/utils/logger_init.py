import logging

from app.utils import env_config as config

# add color to the log levels
# protected member access # pylint: disable=protected-access
logging._levelToName[logging.DEBUG] = '\033[34mDEBUG\033[0m'
logging._levelToName[logging.INFO] = '\033[32mINFO\033[0m'
logging._levelToName[logging.WARNING] = '\033[33mWARNING\033[0m'
logging._levelToName[logging.ERROR] = '\033[91mERROR\033[0m'
logging._levelToName[logging.CRITICAL] = '\033[31mCRITICAL\033[0m'

logging.basicConfig(level=config.LOG_LEVEL,
                    format='%(asctime)s [ %(levelname)s ] [%(name)s %(lineno)d] %(message)s')


def init_logger(name):
    """
    Initialize the logger with module name and return it.
    """
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)
    formatter = logging.Formatter(
        "%(asctime)s [ %(levelname)s ] [%(name)s %(lineno)d] %(message)s")
    
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    if len(root_logger.handlers) > 0:
        root_logger.removeHandler(root_logger.handlers[0])

    logger.addHandler(stream_handler)

    return logger