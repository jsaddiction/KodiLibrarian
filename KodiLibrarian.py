#!/usr/bin/env python3

import os

from utils import config, logger, env, updater
from librarian.librarian import Librarian

updater.pull()
log = logger.get_log('KodiLibrarian')
kodi = Librarian(config.hosts)

if env.downloadedWith == 'radarr':
    log.info('Radarr has downloaded "{}" {}. Initiating update process.'.format(env.radarrTitle, env.radarrMovieFilePath))
    kodi.updateMovie(env.radarrTitle, env.radarrMovieDirectory, env.radarrMovieFilePath)
    if config.clean_after_update:
        kodi.cleanLibrary('movies')

elif env.downloadedWith == 'sonarr':
    log.info('Sonarr has downloaded "{}" {}. Initiating update process.'.format(env.sonarrSeriesTitle, env.sonarrEpisoedFilePath))
    kodi.updateTVShow(env.sonarrEpisoedFilePath, env.sonarrSeriesPath)
    if config.clean_after_update:
        kodi.cleanLibrary('tvshows')

elif env.downloadedWith == 'lidarr':
    log.info('Lidarr not supported yet!! Aborting.')

else:
    log.critical('Could not find any recognizable environment variables. Aborting.')
    log.debug('ENVIRONMENT VARS: \n{}'.format(env.allKnown))