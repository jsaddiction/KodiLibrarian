#!/usr/bin/env python3

import os
import sys
import shutil
from configparser import ConfigParser

class Config(object):
    def __init__(self, configPath):
        self._raw_config = None
        self.path = configPath
        self.parse()

    def parse(self):
        if os.path.isfile(self.path):
            parser = ConfigParser()
            try:
                parser.read(self.path)
                self._raw_config = parser
            except Exception as e:
                print('Could not read settings.ini ERROR: {}'.format(e))
        else:
            print('Could not find the settings.ini file. Creating one using the example "settings.ini.example"')
            exampleFile = os.path.join(os.path.dirname(self.path), 'settings.ini.example')
            try:
                shutil.copyfile(exampleFile, self.path)
            except Exception:
                print('Could not create your settings file. Create it manually.')
            else:
                print('Please configure settings.ini and rerun this script.')
            sys.exit(1)

    @property
    def log_level(self):
        if not self._raw_config is None:
            if 'LOGS' in self._raw_config.sections():
                return self._raw_config['LOGS'].get('log_level', 'info')
        return 'info'

    @property
    def log_to_file(self):
        if not self._raw_config is None:
            if 'LOGS' in self._raw_config.sections():
                return self._raw_config['LOGS'].getboolean('log_to_file', False)
        return False

    @property
    def clean_after_update(self):
        if not self._raw_config is None:
            if 'LIBRARY' in self._raw_config.sections():
                return self._raw_config['LIBRARY'].getboolean('clean_after_update', False)
        return False

    @property
    def hosts(self):
        hosts = []
        for section in self._raw_config:
            if section.lower().startswith('kodi.'):
                host = {
                    'name': section[5:],
                    'hostname': self._raw_config.get(section, 'host'),
                    'port': self._raw_config.get(section, 'port'),
                    'username': self._raw_config.get(section, 'user'),
                    'password': self._raw_config.get(section, 'pass'),
                    'always_on': self._raw_config.getboolean(section, 'alwaysOn'),
                    'show_notifications': self._raw_config.getboolean(section, 'showNotifications'),
                }
                hosts.append(host)
        hosts.sort(reverse=True, key=lambda host: host['always_on'])
        return hosts