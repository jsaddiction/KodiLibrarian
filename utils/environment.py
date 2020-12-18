#!/usr/bin/env python3
import os
class Env():
    def __init__(self):
        # radarr environment variables
        self.radarrMovieFilePath = os.environ.get('RADARR_MOVIE_FILE_PATH')
        self.radarrMovieDirectory = os.environ.get('RADARR_MOVIE_PATH')
        self.radarrTitle = os.environ.get('RADARR_MOVIE_TITLE')

        # sonarr environment variables
        self.sonarrSeriesTitle = os.environ.get('SONARR_SERIES_TITLE')
        self.sonarrSeriesPath = os.environ.get('SONARR_SERIES_PATH')
        self.sonarrEpisodeSeasonNumber = os.environ.get('SONARR_EPISODEFILE_SEASONNUMBER')
        self.sonarrEpisodeCount = int(os.environ.get('SONARR_RELEASE_EPISODECOUNT', 0))
        if self.sonarrEpisodeCount > 1:
            self.sonarrEpisodeNumber = os.environ.get('SONARR_RELEASE_EPISODENUMBERS', '').replace(',', '').replace(' ', '')
        elif self.sonarrEpisodeCount == 1:
            self.sonarrEpisodeNumber = os.environ.get('SONARR_RELEASE_EPISODENUMBERS', '').split(',')[0]
        self.sonarrEpisoedFilePath = os.environ.get('SONARR_EPISODEFILE_PATH')

        # lidarr environment variables TODO

    @property
    def test(self):
        if os.environ.get('RADARR_EVENTTYPE', '') == 'Test':
            return True
        elif os.environ.get('SONARR_EVENTTYPE', '') == 'Test':
            return True
        elif os.environ.get('LIDARR_EVENTTYPE', '') == 'Test':
            return True
        else:
            return False

    @property
    def downloadedWith(self):
        if os.environ.get('RADARR_EVENTTYPE', '') == 'download':
            return 'radarr'
        elif os.environ.get('SONARR_EVENTTYPE', '') == 'download':
            return 'sonarr'
        elif os.environ.get('LIDARR_EVENTTYPE', '') == 'download':
            return 'lidarr'
        else:
            return None

    @property
    def allKnown(self):
        radarrVars = {k:v for k, v in os.environ.items() if k.startswith('RADARR')}
        sonarrVars = {k:v for k, v in os.environ.items() if k.startswith('SONARR')}
        lidarrVars = {k:v for k, v in os.environ.items() if k.startswith('LIDARR')}
        # return radarrVars + sonarrVars + lidarrVars
        return dict(**radarrVars, **sonarrVars, **lidarrVars)