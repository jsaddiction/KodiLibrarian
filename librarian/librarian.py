#!/usr/bin/env python3

import time

from kodijsonrpc import KodiJSONClient
from jsonrpcclient.exceptions import ReceivedErrorResponse, ReceivedNoResponse
from utils import logger

class KodiHost(KodiJSONClient):
    def __init__(self, name, hostname, port, username, password, always_on, show_notifications):
        self.name = name
        self.scanned = False
        self.always_on = always_on
        self.show_notifications = show_notifications
        super().__init__(hostname, port, username, password)

    @property
    def isAlive(self):
        try:
            return self.JSONRPC.Ping() == 'pong' # pylint: disable=no-member
        except Exception:
            return False

    @property
    def inUse(self):
        try:
            response = self.Player.GetActivePlayers() # pylint: disable=no-member
        except ReceivedErrorResponse:
            return True

        if len(response) > 0:
            return True
        return False

    def notify(self, msg, title='Kodi Library Manager'):
        imageURL = 'https://github.com/jsaddiction/KodiLibrarian/raw/main/img/'
        if title.lower() == 'sonarr':
            imageURL += 'Sonarr.png'
        elif title.lower() == 'radarr':
            imageURL += 'Radarr.png'
        elif title.lower() == 'lidarr':
            imageURL += 'Lidarr.png'
        else:
            imageURL += 'KodiLibrarian.png'

        params = {
            'title': title,
            'message': msg,
            'displaytime': 5000,
            'image': imageURL
        }
        self.GUI.ShowNotification(params)  # pylint: disable=no-member


class Librarian():
    TIMEOUT = 20
    log = logger.get_log('Librarian')
    def __init__(self, hostList):
        self.hosts = []
        for host in hostList:
            client = KodiHost(
            name=host['name'],
            hostname=host['hostname'],
            port=host['port'],
            username=host['username'],
            password=host['password'],
            always_on=host['always_on'],
            show_notifications=host['show_notifications'],
            )
            if client.isAlive:
                self.hosts.append(client)
            else:
                self.log.warning('Failed to establish connection with {}.'.format(client.name))

    def _modifyWatchedState(self, watchedState):
        # Create modified watched state
        newWatchedState = dict(watchedState)
        newWatchedState['lastplayed'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        newWatchedState['playcount'] += 1
        return newWatchedState

    def cleanLibrary(self, content=None):
        params = {
            'showdialogs': False,
            'content': content
        }
        if not content or not content in ['movies', 'tvshows']:
            del params['content']

        for host in self.hosts:
            self.log.info('Initiating clean of {} on host: {}'.format(content, host.name))
            try:
                response = host.VideoLibrary.Clean(params)
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass

            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            return



    ########################  TV Show methods  #######################

    def _getTVShowID(self, path):
        # returns int tvshow id of show located within path
        if not path.endswith('/'):
            path += '/'

        showList = self._getTVShows()
        for show in showList:
            if show['file'] == path:
                return show['tvshowid']
        return None

    def _getTVShows(self):
        # returns list of all tvshows in the library
        params = {
            'properties': ['file']
        }
        for host in self.hosts:
            try:
                response = host.VideoLibrary.GetTVShows(params) # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse) as e:
                self.log.warning('Host: {} Failed to get TVShow list. Error: {}'.format(host.name, e))
                response = None
            
            if response and 'tvshows' in response:
                return response['tvshows']
        return []

    def _getEpisodeID(self, tvshowID, episodePath):
        # returns episodeID of episode located at episodePath
        if not tvshowID:
            return None
        episodes = self._getEpisodes(tvshowID)
        for episode in episodes:
            if episode['file'] == episodePath:
                return episode['episodeid']
        return None

    def _getEpisodes(self, tvshowID):
        # returns list of all episodes of a tvshow
        params = {
            'tvshowid': int(tvshowID),
            'properties': ['file']
        }
        for host in self.hosts:
            try:
                response = host.VideoLibrary.GetEpisodes(params) # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse) as e:
                self.log.warning('Host: {} Failed to get episodes for tvshowID: {} Error: {}'.format(host.name, tvshowID, e))
                response = None

            if response and 'episodes' in response:
                return response['episodes']
        return []

    def _getEpisodeDetails(self, episodeID):
        if not episodeID:
            return None
        params = {
            'episodeid': int(episodeID),
            'properties': ['lastplayed', 'playcount', 'file', 'season', 'episode', 'tvshowid', 'showtitle']
        }

        for host in self.hosts:
            try:
                response = host.VideoLibrary.getEpisodeDetails(params) # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse) as e:
                self.log.warning('Host: {} Failed to get episode details for episodeID: {} Error: {}'.format(host.name, episodeID, e))
                response = None
            
            if response and 'episodedetails' in response:
                return response['episodedetails']
        return None

    def _getEpisodeWatchedState(self, episodeID):
        # returns object contianing watches status of an episode
        if not episodeID:
            return None
        episodeDetails = self._getEpisodeDetails(episodeID)
        if episodeDetails:
            return {k:v for k, v in episodeDetails.items() if k in ['playcount', 'lastplayed', 'episodeid']}
        return None

    def _toggleEpisodeWatchedState(self, episodeID):
        # toggle watchedstate on each nonscanned host
        watchedState = self._getEpisodeWatchedState(episodeID)
        newWatchedState = self._modifyWatchedState(watchedState)

        for host in self.hosts:
            if not host.scanned:
                self._setEpisodeWatchedState(host, newWatchedState)
                self._setEpisodeWatchedState(host, watchedState)

    def _setEpisodeWatchedState(self, host, watchedState):
        if not watchedState:
            return None
        
        self.log.debug('Setting episode watched state to {}'.format(watchedState))

        # Get what is currently in the library
        oldWatchedState = self._getEpisodeWatchedState(watchedState['episodeid'])

        # Initiate the changes
        try:
            response = host.VideoLibrary.SetEpisodeDetails(watchedState) # pylint: disable=no-member
        except (ReceivedErrorResponse, ReceivedNoResponse) as e:
            self.log.warning('Failed to set watched state watchedState: {} Error: {}'.format(watchedState, e))

        if not response == 'OK':
            self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
            return

        t = 0
        while t < self.TIMEOUT * 10:
            time.sleep(0.1)
            t += 1
            newWatchedState = self._getEpisodeWatchedState(watchedState['episodeid'])
            if newWatchedState and not newWatchedState == oldWatchedState:
                self.log.debug('Setting watched state complete. Took {}s'.format(t/10))
                return
        self.log.warning('Host: {} Timed out after {}s while setting episode watched state. Trying next host.'.format(host.name, t/10))

    def _refreshEpisode(self, episodeID):
        # Refresh given episode and return updated episodeID
        self.log.debug('Refreshing episodeID: {}'.format(episodeID))
        episodeDetails = self._getEpisodeDetails(episodeID)
        params = {
            'episodeid': episodeID
        }
        for host in self.hosts:
            try:
                response = host.VideoLibrary.RefreshEpisode(params) # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass
            
            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            t = 0
            while t < self.TIMEOUT * 10:
                time.sleep(0.1)
                t += 1
                newEpisodeID = self._getEpisodeID(episodeDetails['tvshowid'], episodeDetails['file'])
                if newEpisodeID and not newEpisodeID == episodeID:
                    self.log.debug('Refresh complete. New episodeID: {} Took {}s'.format(newEpisodeID, t/10))
                    host.scanned = True
                    return newEpisodeID
            self.log.warning('Host: {} Timed out after {}s while refreshing episode. Trying next host.'.format(host.name, t/10))

    def _scanTVShowDirectory(self, showDirectory, episodePath):
        # Scan tvshow directory and return new episodeID
        self.log.debug('Scanning new episode {}'.format(episodePath))
        showID = self._getTVShowID(showDirectory)
        for host in self.hosts:
            try:
                response = host.VideoLibrary.Scan(directory=showDirectory) # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass

            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            t = 0
            while t < self.TIMEOUT * 10:
                time.sleep(0.1)
                t += 1
                episodeID = self._getEpisodeID(showID, episodePath)
                if episodeID:
                    host.scanned = True
                    self.log.debug('Scan complete. EpisodeID: {} Took {}s'.format(episodeID, t/10))
                    return episodeID
            self.log.warning('Host: {} Timed out after {}s while scanning show directory. Trying next host.'.format(host.name, t/10))

    def _scanNewTVShow(self, showDirectory, episodePath):
        # Full library scan and return new episodeID
        self.log.debug('Scanning new Tv Show {}. This may take a while.'.format(showDirectory))

        for host in self.hosts:
            try:
                response = host.VideoLibrary.Scan() # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass

            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            t = 0
            while t < self.TIMEOUT * 60:
                time.sleep(1)
                t += 1
                episodeID = self._getEpisodeID(self._getTVShowID(showDirectory), episodePath)
                if episodeID:
                    host.scanned = True
                    self.log.debug('Scan complete. EpisodeID: {} Took {}s'.format(episodeID, t))
                    return episodeID
            self.log.warning('Host: {} Timed out after {}s while scanning entire library. Trying next host.'.format(host.name, t/10))

    # Main method used to update / add new episode / tvshow
    def updateTVShow(self, episodePath, showDirectory):
        showID = self._getTVShowID(showDirectory)
        episodeID = self._getEpisodeID(showID, episodePath)

        # Refresh or add this episode to the library
        if episodeID:
            # Episode and show exists. Refresh episode. Return updated episodeID.
            episodeID = self._refreshEpisode(episodeID)
            notificationStr = 'Updated Episode '
        elif showID:
            # Show exists but not episode. Scaning show directory for new content. Return new episodeID.
            episodeID = self._scanTVShowDirectory(showDirectory, episodePath)
            notificationStr = 'Added Episode '
        else:
            # Neither show nor episode exist. Preform full library scan. Return new episodeID.
            episodeID = self._scanNewTVShow(showDirectory, episodePath)
            notificationStr = 'Added TV Show '

        # Toggle watched state of this new/updated episode
        self._toggleEpisodeWatchedState(episodeID)

        # Send notifications
        episodeDetails = self._getEpisodeDetails(episodeID)
        notificationStr += '"{}" S{}E{} "{}"'.format(episodeDetails['showtitle'], episodeDetails['season'], episodeDetails['episode'], episodeDetails['label'])
        for host in self.hosts:
            if host.show_notifications:
                self.log.info('Sending notification to {}. Message: "{}"'.format(host.name, notificationStr))
                host.notify(notificationStr, 'Sonarr')

    ########################  Movie methods  #######################

    def _getMovieID(self, title, path):
        if not title or not path:
            return

        params = {
            'filter': {'operator': 'is', 'field': 'title', 'value': title},
            'properties': ['file']
            }
        for host in self.hosts:
            try:
                response = host.VideoLibrary.GetMovies(params)
            except (ReceivedErrorResponse, ReceivedNoResponse) as e:
                self.log.warning('Host: {} Failed to get movieid for {}. Error: {}'.format(host.name, title, e))
                response = None

            if response and 'movies' in response:
                for movie in response['movies']:
                    if movie['file'] == path:
                        return movie['movieid']
        return None

    def _getMovieDetails(self, movieID):
        if not movieID:
            return None

        params = {
            'movieid': int(movieID),
            'properties': ['file', 'lastplayed', 'playcount', 'year']
        }

        for host in self.hosts:
            try:
                response = host.VideoLibrary.getMovieDetails(params)
            except (ReceivedErrorResponse, ReceivedNoResponse) as e:
                self.log.warning('Host: {} Failed to get Movie details movieID: {} Error: {}'.format(host.name, movieID, e))
                response = None

            if response and 'moviedetails' in response:
                return response['moviedetails']
        return None

    def _refreshMovie(self, movieID):
        if not movieID:
            return
        movieDetails = self._getMovieDetails(movieID)
        self.log.info('Refreshing "{}" ({})'.format(movieDetails['label'], movieDetails['year']))
        params = {
            'movieid': int(movieID)
        }

        for host in self.hosts:
            try:
                response = host.VideoLibrary.RefreshMovie(params) # pylint: disable=no-member
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass
            
            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            t = 0
            while t < self.TIMEOUT * 10:
                time.sleep(0.1)
                t += 1
                newMovieID = self._getMovieID(movieDetails['label'], movieDetails['file'])
                if newMovieID and not movieID == newMovieID:
                    self.log.debug('Refresh complete. New movieID: {} Took {}s'.format(newMovieID, t/10))
                    host.scanned = True
                    return newMovieID
            self.log.warning('Host: {} Timed out after {}s while refreshing movie. Trying next host.'.format(host.name, t/10))

    def _scanNewMovie(self, title, movieDirectory, moviePath):
        self.log.debug('Initiating directory scan for new movie. directory: "{}"'.format(movieDirectory))
        if not movieDirectory.endswith('/'):
            movieDirectory += '/'
        for host in self.hosts:
            try:
                response = host.VideoLibrary.Scan(directory=movieDirectory)
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass

            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            t = 0
            while t < self.TIMEOUT * 10:
                time.sleep(0.1)
                t += 1
                movieID = self._getMovieID(title, moviePath)
                if movieID:
                    self.log.debug('Directroy Scan complete. New movieID: {} Took {}s'.format(movieID, t/10))
                    host.scanned = True
                    return movieID
            self.log.warning('Host: {} Timed out after {}s while scanning new movie. Trying next host.'.format(host.name, t/10))
        
        self.log.warning('All hosts failed to scan by directory. Initiating full library scan.')
        for host in self.hosts:
            try:
                response = host.VideoLibrary.Scan()
            except (ReceivedErrorResponse, ReceivedNoResponse):
                pass

            if not response == 'OK':
                self.log.warning('Incorrect response received from Host: {} Response: {}. Trying next host.'.format(host.name, response))
                continue

            t = 0
            while t < self.TIMEOUT * 60:
                time.sleep(1)
                t += 1
                movieID = self._getMovieID(title, moviePath)
                if movieID:
                    self.log.debug('Full scan complete. New movieID: {} Took {}s'.format(movieID, t))
                    host.scanned = True
                    return movieID
            self.log.warning('Host: {} Timed out after {}s while scanning new movie. Trying next host.'.format(host.name, t))
        self.log.warning('All hosts failed to scan "{}" {}. Aborting.'.format(title, moviePath))

    def _getMovieWatchedState(self, movieID):
        if not movieID:
            return None
        movieDetails = self._getMovieDetails(movieID)
        if movieDetails:
            return {k:v for k, v in movieDetails.items() if k in ['playcount', 'lastplayed', 'movieid']}
        return None

    def _setMovieWatchedState(self, host, watchedState):
        if not watchedState:
            return None
        
        self.log.debug('Setting movie watched state to {}'.format(watchedState))

        # Get what is currently in the library
        oldWatchedState = self._getMovieWatchedState(watchedState['movieid'])

        # Initiate the changes
        try:
            response = host.VideoLibrary.SetMovieDetails(watchedState) # pylint: disable=no-member
        except (ReceivedErrorResponse, ReceivedNoResponse) as e:
            self.log.warning('Failed to set watched state watchedState: {} Error: {}'.format(watchedState, e))

        if not response == 'OK':
            self.log.warning('Incorrect response received from Host: {} Response: {}.'.format(host.name, response))
            return

        t = 0
        while t < self.TIMEOUT * 10:
            time.sleep(0.1)
            t += 1
            newWatchedState = self._getMovieWatchedState(watchedState['movieid'])
            if newWatchedState and not oldWatchedState == newWatchedState:
                self.log.debug('Setting watched state complete. Took {}s'.format(t/10))
                return
        self.log.warning('Host: {} Timed out after {}s while setting movie watched state.'.format(host.name, t/10))

    def _toggleMovieWatchedState(self, movieID):
        watchedState = self._getMovieWatchedState(movieID)
        newWatchedState = self._modifyWatchedState(watchedState)

        for host in self.hosts:
            if not host.scanned:
                self.log.info('Toggling watched state on host: {}'.format(host.name))
                self._setMovieWatchedState(host, newWatchedState)
                self._setMovieWatchedState(host, watchedState)

    # Main method used to update / add new movie
    def updateMovie(self, title, movieDirectory, moviePath):
        movieID = self._getMovieID(title, moviePath)

        if not movieID:
            movieID = self._scanNewMovie(title, movieDirectory, moviePath)
            notificationStr = 'Added New Movie '
        else:
            movieID = self._refreshMovie(movieID)
            notificationStr = 'Updated Movie '

        # Toggle watched state on remaining hosts
        self._toggleMovieWatchedState(movieID)

        # Send notifications
        movieDetails = self._getMovieDetails(movieID)
        notificationStr += '"{}" ({})'.format(movieDetails['label'], movieDetails['year'])
        for host in self.hosts:
            if host.show_notifications:
                self.log.info('Sending notification to {}. Message: "{}"'.format(host.name, notificationStr))
                host.notify(notificationStr, 'Radarr')