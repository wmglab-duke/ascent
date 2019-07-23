#!/usr/bin/env python3.7

"""
File:       Exceptionable.py
Author:     Jake Cariello
Created:    July 20, 2019

Description:

    OVERVIEW
    Meant to be inherited for configurable functionality. Expandable and allows for quick access to configuration file
    data (in addition to path building method). It is important to note that this class has BUILT IN exceptions that it
    throws (-1 and below) because it is inherently unable to inherit from Exceptionable, which, in turn, is configured.

    INITIALIZER
    See docstring in __init__.

    PROPERTIES

    METHODS
    search(key, *args): takes a key for the desired configs, then "path" to the item in the JSON (all strings and ints)



"""

import json
import os

from src.utils.SetupMode import SetupMode
from src.utils.ConfigKey import ConfigKey


class Configurable:

    def __init__(self, mode: SetupMode, key: ConfigKey, config):
        """
        :param mode: SetupMode, determines if loads new JSON or uses old data
        :param key: choice of MASTER or EXCEPTIONS (or any other added separate configs)
        :param config: if mode is NEW, this is file path str, else (mode is OLD) this is already loaded config data
        """
        # if self.configs does not already exist (i.e. this is first Configurable call), create it
        if not hasattr(self, 'configs'):
            self.configs = dict()

        # either load up new data or used old, passed in data
        if mode == SetupMode.NEW:
            self.config_path = config

            # if last 5 characters of file path are NOT '.json', raise an Exception
            if not self.config_path[-5:] == '.json':
                raise Exception('\n\tcode:\t-1'
                                '\ttext:\tConfiguration file path must end in .json\n'
                                '\tsource:\tConfigurable.py')
            self.__load(key)

        elif mode == SetupMode.OLD:
            self.configs[key.value] = config

        else:
            raise Exception('dude, what?')

    def search(self, key: ConfigKey, *args):
        """
        Get an item using "path" of args in the json config.
        :param key:
        :param args: list "path" to item within json (str or int)
        :return: final specified item
        """
        result = self.configs[key.value]
        for arg in args:
            if isinstance(arg, str):
                result = result.get(arg)
            elif isinstance(arg, int):
                result = result[arg]
            else:
                raise Exception('\n\tcode:\t-2'
                                '\ttext:\tInvalid search parameter (\n\t\tTYPE: {}\t VALUE: {})\n'
                                '\tsource:\tConfigurable.py'.format(type(arg), arg))
        return result

    def path(self, key: ConfigKey, *args):
        """
        Build a path for an item specified in same style as self.get() ...
        REQUIRES that there be a str "root" on same level as lowest item
        :param key:
        :param args: "path" to desired item
        :return: final path to item (with system formatting!)
        """
        return os.path.join(self.search(key, *args[:-1]).get('root'),
                            self.search(key, *args))

    def __load(self, key: ConfigKey):
        """
        PRIVATE method to load in data (can access publicly through self.reload)
        :param key: choice of config to load up
        """
        with open(self.config_path, "r") as handle:
            # print('load "{}" --> key "{}"'.format(config, key))
            self.configs[key.value] = json.load(handle)

    def reload(self, key: ConfigKey):
        """
        Buffer public method to load data from JSON (for naming purposes)
        :param key: choice of config to load up
        """
        self.__load(key)
