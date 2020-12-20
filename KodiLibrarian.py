#!/usr/bin/env python3

import os
import sys

from utils import config, logger, env, updater
from librarian.librarian import Librarian

updater.pull()
log = logger.get_log('KodiLibrarian')
kodi = Librarian(config.hosts)

log.debug('Environment Vars: {}'.format(env.allKnown))

if env.event == 'download':
    if env.calledBy == 'radarr':
        log.info('Radarr has downloaded "{}" {}. Initiating update process.'.format(env.movieTitle, env.moviePath))
        kodi.updateMovie(env.movieTitle, env.movieDirectory, env.moviePath)
        if config.clean_after_update:
            kodi.cleanLibrary('movies')

    elif env.calledBy == 'sonarr':
        log.info('Sonarr has downloaded "{}" {}. Initiating update process.'.format(env.showTitle, env.episodePath))
        kodi.updateTVShow(env.episodePath, env.showDirectory)
        if config.clean_after_update:
            kodi.cleanLibrary('tvshows')

    elif env.calledBy == 'lidarr':
        log.info('Lidarr not supported yet!! Aborting.')

elif env.event == 'test':
    log.debug('Called with test environment')
    sys.exit(0)

else:
    log.critical('Could not find any recognizable environment variables. Aborting.')
