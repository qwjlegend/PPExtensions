import logging
from pathlib import Path


logger_name = "extension_logger"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

log_path = str(Path.home()) + "/.extensionlog.log"
fh = logging.FileHandler(log_path)
fh.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt)

fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)
