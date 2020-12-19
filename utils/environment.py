#!/usr/bin/env python3
import os
class Env():

    ENV_LABELS = ['radarr', 'sonarr', 'lidarr']

    def __init__(self):
        self._vars = {k.lower():v for (k, v) in os.environ.items() if 'radarr' in k.lower() or 'sonarr' in k.lower() or 'lidarr' in k.lower()}

    @property
    def allKnown(self):
        return self._vars

    @property
    def calledBy(self):
        for k, _ in self._vars:
            if 'radarr' in k:
                return 'radarr'
            elif 'sonarr' in k:
                return 'sonarr'
            elif 'lidarr' in k:
                return 'lidarr'
            else:
                return None

    @property
    def event(self):
        return self._vars.get('{}_eventtype'.format(self.calledBy), None)

    @property
    def test(self):
        event = self.event
        if event:
            return self.event.lower() == 'test'
        else:
            return None

    @property
    def episodePath(self):
        episodePathKeys = ['sonarr_episodefile_path']
        for k, v in self._vars.items():
            if k in episodePathKeys:
                return v
        return None

    @property
    def episodeNumber(self):
        episodeNumberKeys = ['sonarr_release_episodenumbers']
        for k, v in self._vars.items():
            if k in episodeNumberKeys:
                return v.split(',')[0]
        return None

    @property
    def episodeCount(self):
        episodeCountKeys = ['sonarr_release_episodecount']
        for k, v in self._vars.items():
            if k in episodeCountKeys:
                return int(v)
        return None

    @property
    def seasonNumber(self):
        seasonNumberKeys = ['sonarr_episodefile_seasonnumber']
        for k, v in self._vars.items():
            if k in seasonNumberKeys:
                return v
        return None

    @property
    def showDirectory(self):
        showDirectoryKeys = ['sonarr_series_path']
        for k, v in self._vars.items():
            if k in showDirectoryKeys:
                return v
        return None

    @property
    def showTitle(self):
        showTitleKeys = ['sonarr_series_title']
        for k, v in self._vars.items():
            if k in showTitleKeys:
                return v
        return None

    @property
    def moviePath(self):
        moviePathKeys = ['radarr_moviefile_path']
        for k, v in self._vars.items():
            if k in moviePathKeys:
                return v
        return None

    @property
    def movieDirectory(self):
        movieDirectoryKeys = ['radarr_movie_path']
        for k, v in self._vars.items():
            if k in movieDirectoryKeys:
                return v
        return None

    @property
    def movieTitle(self):
        movieTitleKeys = ['radarr_movie_title']
        for k, v in self._vars.items():
            if k in movieTitleKeys:
                return v
        return None
