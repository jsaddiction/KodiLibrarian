#!/usr/bin/env python3

from kodiLibrary.kodi import Kodi

class LibraryManager():
    def __init__(self, hostList, synchronized=True, fallBackToFullScan=True):
        self.hosts = []

        for host in hostList:
            client = Kodi(
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

    def notifyAll(self, msg, image=''):
        for host in self.hosts:
            host.notify(msg, image)