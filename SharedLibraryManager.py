#!/usr/bin/env python3

import updates
# updates.update(verbose=True)
from utils.environment import Env
from utils.config import Config
from kodiLibrary.libraryManager import LibraryManager

config = Config()
env = Env()
kodi = LibraryManager(config.hosts, config.synchronized, config.fallback_to_full_scan)

kodi.notifyAll('Testing')



