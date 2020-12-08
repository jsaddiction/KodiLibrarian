#!/usr/bin/env python3

import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.ini')
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'KodiCoupler.log')

# Test mode options ['TV', 'Movie', 'Music']
# Set test mode to none if not testing
TEST_MODE = 'Movie'

if TEST_MODE == 'TV':
    os.environ['SONARR_EVENTTYPE'] = 'download'
    os.environ['SONARR_SERIES_TITLE'] = ''
    os.environ['SONARR_SERIES_PATH'] = ''
    os.environ['SONARR_EPISODEFILE_SEASONNUMBER'] = ''
    os.environ['SONARR_RELEASE_EPISODECOUNT'] = ''
    os.environ['SONARR_RELEASE_EPISODENUMBERS'] = ''
    os.environ['SONARR_EPISODEFILE_PATH'] = ''


elif TEST_MODE == 'Movie':
    os.environ['RADARR_EVENTTYPE'] = 'download'
    os.environ['RADARR_MOVIE_FILE_PATH'] = '/var/nfs/movies/8MM (1999)/8MM (tt0134273).mkv'
    os.environ['RADARR_MOVIE_PATH'] = '/var/nfs/movies/8MM (1999)'
    os.environ['RADARR_MOVIE_TITLE'] = '8MM'


elif TEST_MODE == 'Music':
    os.environ['LIDARR_ALBUM_TITLE'] = ''