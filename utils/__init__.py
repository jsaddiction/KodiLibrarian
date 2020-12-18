#!/usr/bin/env python3

import os
from utils.logger import Logger
from utils.config import Config
from utils.environment import Env
from utils.updater import Updater

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.ini')
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'KodiLibrarian.log')
env = Env()
config = Config(CONFIG_PATH)
logger = Logger(LOG_PATH, config.log_level, config.log_to_file)
updater = Updater(logger.get_log('Updater'))
