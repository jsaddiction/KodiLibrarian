#!/usr/bin/env python3
import os
class Env():

    ENV_LABELS = ['radarr', 'sonarr', 'lidarr']

    def __init__(self):

        # radarr environment variables
        self.radarrMovieFilePath = self._getVar('radarr_moviefile_path')
        self.radarrMovieDirectory = self._getVar('radarr_movie_path')
        self.radarrTitle = self._getVar('radarr_movie_title')

        # sonarr environment variables
        self.sonarrSeriesTitle = self._getVar('sonarr_series_title')
        self.sonarrSeriesPath = self._getVar('sonarr_series_path')
        self.sonarrEpisodeSeasonNumber = self._getVar('sonarr_episodefile_seasonnumber')
        self.sonarrEpisodeCount = self._getNum('sonarr_release_episodecount')
        if self.sonarrEpisodeCount > 1:
            self.sonarrEpisodeNumber = self._getVar('sonarr_release_episodenumbers').replace(',', '').replace(' ', '')
        elif self.sonarrEpisodeCount == 1:
            self.sonarrEpisodeNumber = self._getVar('sonarr_release_episodenumbers').split(',')[0]
        self.sonarrEpisoedFilePath = self._getVar('sonarr_episodefile_path')

        # lidarr environment variables TODO

    def _getVar(self, variableName):
        for k, v in os.environ.items():
            if k.lower() == variableName.lower():
                return v

        return ''

    def _getNum(self, variableName):
        try:
            return int(self._getVar(variableName))
        except:
            return 0

    @property
    def test(self):
        if self._getVar('radarr_eventtype').lower() == 'test':
            return True
        elif self._getVar('sonarr_eventtype').lower() == 'test':
            return True
        elif self._getVar('lidarr_eventtype').lower() == 'test':
            return True
        else:
            return False

    @property
    def downloadedWith(self):
        if self._getVar('radarr_eventtype').lower() == 'download':
            return 'radarr'
        elif self._getVar('sonarr_eventtype').lower() == 'download':
            return 'sonarr'
        elif self._getVar('lidarr_eventtype').lower() == 'download':
            return 'lidarr'
        else:
            return None

    @property
    def allKnown(self):
        # radarrVars = {k:v for k, v in os.environ.items() if k.startswith('RADARR')}
        # sonarrVars = {k:v for k, v in os.environ.items() if k.startswith('SONARR')}
        # lidarrVars = {k:v for k, v in os.environ.items() if k.startswith('LIDARR')}
        # # return radarrVars + sonarrVars + lidarrVars
        # return dict(**radarrVars, **sonarrVars, **lidarrVars)
        return dict(os.environ.items())