#!/usr/bin/env python3

import kodijsonrpc

class Kodi():

    TIMEOUT = 20

    def __init__(self, name, hostname, port, username, password, always_on, show_notifications):
        self._client = kodijsonrpc.KodiJSONClient(hostname, port, username, password)
        self.name = name
        self.host = '{}:{}'.format(hostname, port)
        self.always_on = always_on
        self.show_notifications = show_notifications
        self.scanned = False

    @property
    def isAlive(self):
        try:
            return self._client.JSONRPC.Ping() == 'pong'
        except:
            return False

    def notify(self, message, title='', image=None):
        baseURL = 'https://github.com/jsaddiction/SharedLibraryManager/raw/main/img/'
        if self.show_notifications:
            if image:
                imageURL = '{}{}.png'.format(baseURL, image)
            else:
                imageURL = '{}librarymanager.png'.format(baseURL)
            # if image == 'radarr':
            #     imageURL = '{}Radarr.png'.format(baseURL)
            # elif image == 'sonarr':
            #     imageURL = 'https://github.com/jsaddiction/SharedLibraryManager/raw/main/img/Sonarr.png'
            # elif image == 'lidarr':
            #     imageURL = 'https://github.com/jsaddiction/SharedLibraryManager/raw/main/img/Lidarr.png'
            # else:
            #     imageURL = 'https://github.com/jsaddiction/SharedLibraryManager/raw/main/img/LibraryManager.png'

            if not title:
                notificationTitle = 'Shared Library Manager'
            else:
                notificationTitle = title

            self._client.GUI.ShowNotification(title=notificationTitle, message=message, displaytime=5000, image=imageURL)  # pylint: disable=no-member