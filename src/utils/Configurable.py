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
            self.validate_path(self.config_path)
            self.configs[key.value] = self.load(self.config_path)

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
                raise Exception('\n\tcode:\t-2\n'
                                '\ttext:\tInvalid search parameter:\tTYPE: {}\tVALUE: {}\n'
                                '\tsource:\tConfigurable.py'.format(type(arg), arg))
        return result

    def path(self, key: ConfigKey, *args, isdir: bool = False, isabsolute: bool = False):
        """
        Build a path for an item specified in same style as self.search().
        Expects the item returned by self.search(key, *args) to be a list.
        :param isabsolute: flag to make the path absolute
        :param isdir: if true, will add trailing slash (system nonspecific) to path
        :param key: ConfigKey (choice of configurations from discrete enumeration)
        :param args: "path" to desired path
        :return: final path to item (with system formatting!)
        """
        items: list = self.search(key, *args)

        if isdir:
            items.append('')  # to force trailing slash with os.path.join

        if isabsolute:
            items.insert(0, os.path.abspath(os.sep))  # force leading slash and (if Windows) drive letter

        return os.path.join(*items)  # splat list into comma-separated args

    @staticmethod
    def load(config_path: str):
        """
        PRIVATE method to load in data (can access publicly through self.reload)
        :param config_path:
        """
        with open(config_path, "r") as handle:
            # print('load "{}" --> key "{}"'.format(config, key))
            return json.load(handle)

    def reload(self, config_path: str = None):
        """
        Buffer public method to load data from JSON (for naming purposes)
        :param config_path:
        """
        if config_path is not None:  # this MUST be the case if it was loaded up via SetupMode.OLD
            self.config_path = config_path
            self.validate_path(config_path)

        self.load(self.config_path)

    @staticmethod
    def validate_path(config_path: str):
        # if last 5 characters of file path are NOT '.json', raise an Exception
        if not config_path[-5:] == '.json':
            raise Exception('\n\tcode:\t-1'
                            '\ttext:\tFile path must end in .json\n'
                            '\tsource:\tConfigurable.py or SlideMap.py')
