#!/usr/bin/env python3.7

"""
Description:

    OVERVIEW
    Meant to be inherited for configurable functionality. Expandable and allows for quick src to configuration file
    data (in addition to path building method). It is important to note that this class has BUILT IN exceptions that it
    throws (-1 and below) because it is inherently unable to inherit from Exceptionable, which, in turn, is configured.

    INITIALIZER
    See docstring in __init__.

    PROPERTIES
    configs (dict, with the top-level keys being values from the ConfigKeys, which is an Enum)

    METHODS
    search
    path
    load
    reload
    validate_path (ensures that it ends with .json)



"""
# builtins
import json
import os
from typing import Type, List

# access
from .enums import *


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

        else:  # mode == SetupMode.OLD:
            self.configs[key.value] = config

    def search(self, key: ConfigKey, *args):
        """
        Get an item using "path" of args in the json config.
        :param key: type of config to search within
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
                                '\tsource:\tconfigurable.py'.format(type(arg), arg))
        return result

    def path(self, key: ConfigKey, *args, is_dir: bool = False, is_absolute: bool = False):
        """
        Build a path for an item specified in same style as self.search().
        Expects the item returned by self.search(key, *args) to be a list.
        :param is_absolute: flag to make the path absolute
        :param is_dir: if true, will add trailing slash (system nonspecific) to path
        :param key: ConfigKey (choice of configurations from discrete enumeration)
        :param args: "path" to desired path
        :return: final path to item (with system formatting!)
        """
        items: list = self.search(key, *args)

        if is_dir:
            items.append('')  # to force trailing slash with os.path.join

        if is_absolute:
            items.insert(0, os.path.abspath(os.sep))  # force leading slash and (if Windows) drive letter

        return os.path.join(*items)  # splat list into comma-separated args

    @staticmethod
    def load(config_path: str):
        """
        Loads in json data and returns to user, assuming it has already been validated.
        :param config_path: the string path to load up
        :return: json data (usually dict or list)
        """
        with open(config_path, "r") as handle:
            # print('load "{}" --> key "{}"'.format(config, key))
            return json.load(handle)

    def reload(self, key: ConfigKey, config_path: str = None):
        """
        Buffer public method to load data from JSON (for naming purposes)
        :param key: type of config to reload
        :param config_path: the path to the json, assuming already validated
        """
        if config_path is not None:  # this MUST be the case if it was loaded up via SetupMode.OLD
            self.config_path = config_path
            self.validate_path(config_path)

        self.configs[key.value] = self.load(self.config_path)

    def search_mode(self, mode: Type[Enum]):
        """
        :param mode: an Enum mode that is being searched. it MUST have variable config, which is the name
                     to search for in the masterX.json file
        :return: the Enum version of the mode that is specified by the master config
        """

        return self.search_multi_mode(mode=mode, count=1)[0]

    def search_multi_mode(self, mode: Type[Enum] = None, modes: List[Type[Enum]] = None, count: int = None) -> list:
        """

        :param mode:
        :param modes:
        :param count:
        :return:
        """

        list_results = []

        if mode is not None:
            modes = [mode]

        if modes is None:
            raise Exception('\n\tcode:\t-4\n'
                            '\ttext:\tAt least one mode type must be provided.\n'
                            '\tsource:\tsrc.utils.Configurable.search_multi_mode')

        for mode in modes:

            modes_in_config = self.search(ConfigKey.MASTER, 'modes', mode.config.value)

            if not isinstance(modes_in_config, list):
                modes_in_config = [modes_in_config]

            list_results += [option for option in mode
                             if str(option).split('.')[1] in modes_in_config]

        if count is not None:
            if len(list_results) != count:
                raise Exception('\n\tcode:\t-3\n'
                                '\ttext:\t{} matches found when {} were expected.\n'
                                '\tsource:\tsrc.utils.Configurable.search_multi_mode'.format(len(list_results), count))

        return list_results



    @staticmethod
    def validate_path(config_path: str):
        # if last 5 characters of file path are NOT '.json', raise an Exception
        if not config_path[-5:] == '.json':
            raise Exception('\n\tcode:\t-1'
                            '\ttext:\tFile path must end in .json\n'
                            '\tsource:\tconfigurable.py or map.py')
