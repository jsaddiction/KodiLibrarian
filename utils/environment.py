#!/usr/bin/env python3
import os
class Env():

    ENV_LABELS = ['radarr', 'sonarr', 'lidarr']

    def __init__(self):
        self.radarrVars = {k.lower():v for k, v in os.environ.items() if 'radarr' in k.lower()}
        self.sonarrVars = {k.lower():v for k, v in os.environ.items() if 'radarr' in k.lower()}
        self.lidarrVars = {k.lower():v for k, v in os.environ.items() if 'lidarr' in k.lower()}

        # radarr environment variables
        self.radarrMovieFilePath = self.radarrVars.get('radarr_movie_file_path')
        self.radarrMovieDirectory = self.radarrVars.get('radarr_movie_path')
        self.radarrTitle = self.radarrVars.get('radarr_movie_title')

        # sonarr environment variables
        self.sonarrSeriesTitle = self.sonarrVars.get('sonarr_series_title')
        self.sonarrSeriesPath = self.sonarrVars.get('sonarr_series_path')
        self.sonarrEpisodeSeasonNumber = self.sonarrVars.get('sonarr_episodefile_seasonnumber')
        self.sonarrEpisodeCount = int(self.sonarrVars.get('sonarr_release_episodecount', 0))
        if self.sonarrEpisodeCount > 1:
            self.sonarrEpisodeNumber = self.sonarrVars.get('sonarr_release_episodenumbers', '').replace(',', '').replace(' ', '')
        elif self.sonarrEpisodeCount == 1:
            self.sonarrEpisodeNumber = self.sonarrVars.get('sonarr_release_episodenumbers', '').split(',')[0]
        self.sonarrEpisoedFilePath = self.sonarrVars.get('sonarr_episodefile_path')

        # lidarr environment variables TODO

    @property
    def test(self):
        if self.radarrVars.get('radarr_eventtype', '').lower() == 'test':
            return True
        elif self.sonarrVars.get('sonarr_eventtype', '').lower() == 'test':
            return True
        elif self.lidarrVars.get('lidarr_eventtype', '').lower() == 'test':
            return True
        else:
            return False

    @property
    def downloadedWith(self):
        if self.radarrVars.get('radarr_eventtype', '') == 'download':
            return 'radarr'
        elif os.environ.get('sonarr_eventtype', '') == 'download':
            return 'sonarr'
        elif os.environ.get('lidarr_eventtype', '') == 'download':
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