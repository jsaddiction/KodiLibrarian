import logging
import logging.handlers
import os

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LibraryManager.log')

class Logger():
    '''
    Creates loggers for the various modules
    '''
    def __init__(self, log_path, log_level, log_to_file=False):
        self._format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        self._log_level = logging.getLevelName(log_level.upper())
        self._log_to_file = log_to_file
        self._log_path = log_path

    def get_log(self, name):
        log = logging.getLogger(name)
        log.setLevel(self._log_level)
        
        sh = logging.StreamHandler()
        sh.setFormatter(self._format)
        log.addHandler(sh)

        if self._log_to_file:
            fh = logging.handlers.RotatingFileHandler(self._log_path, mode='a', maxBytes=1000000, backupCount=5)
            fh.setLevel(self._log_level)
            fh.setFormatter(self._format)
            log.addHandler(fh)

        return log