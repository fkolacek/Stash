#
# Author: Frantisek Kolacek <work@kolacek.it
# Version: 1.0
#

import configparser

from .exception import StashConfigException


class StashConfig:

    config = {
        'main': {
            'debug': False,
            'host': '127.0.0.1',
            'port': 5000,
        },
        'database': {
            'name': 'database.db',
            'token': '',
        },
        'web': {
            'title': 'Stash',
            'description': 'Store your favorite Git repositories in Stash.',
            'secret_key': 'super_secret_key',
        },
    }

    def __init__(self, config_name):
        conf = configparser.ConfigParser()

        try:
            conf.read(config_name)
        except configparser.Error:
            raise StashConfigException('Unable to parse config "{}"'.format(config_name)) from None

        for section in conf.sections():
            if section == 'main':
                self._parse_main(conf, section)
            elif section == 'database':
                self._parse_database(conf, section)
            elif section == 'web':
                self._parse_web(conf, section)
            else:
                raise StashConfigException('Invalid section in config file: "{}"'.format(section))

    def _parse_main(self, conf, section):
        for key in conf[section]:
            if key == 'debug':
                self.config[section][key] = conf[section][key].lower() == 'true'
            elif key == 'host':
                self.config[section][key] = conf[section][key]
            elif key == 'port':
                self.config[section][key] = int(conf[section][key])
            else:
                raise StashConfigException('Found invalid key "{}" in "{}" section'.format(key, section))

    def _parse_database(self, conf, section):
        for key in conf[section]:
            if key == 'name':
                self.config[section][key] = conf[section][key]
            elif key == 'token':
                self.config[section][key] = conf[section][key]
            else:
                raise StashConfigException('Found invalid key "{}" in "{}" section'.format(key, section))

    def _parse_web(self, conf, section):
        for key in conf[section]:
            if key == 'title':
                self.config[section][key] = conf[section][key]
            elif key == 'secret_key':
                self.config[section][key] = conf[section][key]
            else:
                raise StashConfigException('Found invalid key "{}" in "{}" section'.format(key, section))

    def __getitem__(self, name):
        return self.config.get(name)
