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
    Pass in a string path to the JSON configuration file. Will raise an exception if incorrect format (just checks the
    file extension). Loads that configuration file into a property self.config using standard convention.

    PROPERTIES

    METHODS
    search(key, *args): takes a key for the desired configs

"""

import json
import os

from src.utils.SetupMode import SetupMode


class Configurable:

    def __init__(self, mode: SetupMode, key: str, config):
        """
        :param key:
        :param config: if mode is NEW, this is file path, else (mode is OLD) this is config data
        """

        # if self.configs does not already exist (i.e. this is first Configurable call), create it
        if not hasattr(self, 'configs'):
            self.configs = dict()

        # either load up new data or used old, passed in data
        if mode == SetupMode.NEW:
            # if last 5 characters of file path are NOT '.json', raise an Exception
            if not config[-5:] == '.json':
                raise Exception('\n\tcode:\t-1'
                                '\ttext:\tConfiguration file path must end in .json\n'
                                '\tsource:\tConfigurable.py')

            with open(config, "r") as handle:
                print('loading a JSON config')
                self.configs[key] = json.load(handle)

        elif mode == SetupMode.OLD:

            self.configs[key] = config

        else:

            raise Exception('dude, what?')

    def search(self, key: str, *args):
        """
        Get an item using "path" of args in the json config.
        :param key:
        :param args: list "path" to item within json (str or int)
        :return: final specified item
        """
        result = self.configs[key]
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

    def path(self, key: str, *args):
        """
        Build a path for an item specified in same style as self.get() ...
        REQUIRES that there be a str "root" on same level as lowest item
        :param key:
        :param args: "path" to desired item
        :return: final path to item (with system formatting!)
        """
        return os.path.join(self.search(key, *args[:-1]).get('root'),
                            self.search(key, *args))
