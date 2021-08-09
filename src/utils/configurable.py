#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# builtins
import json
from typing import Type, List, Union

# ascent
from .enums import *

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
    add
    remove
    search
    path
    load
    search_mode
    search_multi_mode
    validate_path (ensures that it ends with .json)
"""


class Configurable:

    def __init__(self, mode: SetupMode = None, key: Config = None, config: Union[str, dict, list] = None):
        """
        :param mode: SetupMode, determines if loads new JSON or uses old data
        :param key: Config (choice of configurations from discrete enumeration); choice of SAMPLE, MODEL, SIM (these are the big ones), EXCEPTIONS, or any other added configs
        :param config: if mode is NEW, this is file path str, else (mode is OLD) this is already loaded config data
        """
        # if self.configs does not already exist (i.e. this is first Configurable call), create it
        if not hasattr(self, 'configs'):
            self.configs = dict()

        if len([item for item in [mode, key, config] if item is None]) == 0:
            self.add(mode, key, config)

    def add(self, mode: SetupMode, key: Config, config: Union[str, dict]):
        """
        :param mode: OLD (data already loaded in the form of a dict) or NEW (data is in a file, loading from path)
        :param key: Config (choice of configurations from discrete enumeration)
        :param config: in case of OLD mode (this is THE dict), in case of NEW mode (this is the path in form of string)
        :return: the dict
        """

        # either load up new data or used old, passed in data
        if mode == SetupMode.NEW:
            self.validate_path(config)
            self.configs[key.value] = self.load(config)

        else:  # mode == SetupMode.OLD:
            self.configs[key.value] = config

        return self

    def remove(self, key: Config) -> dict:
        """
        :param key: Config (choice of configurations from discrete enumeration)
        :return: configs with the passed in key dict removed. If the key did not exist, None is returned.
        https://stackoverflow.com/questions/1990802/in-python-what-does-dict-popa-b-mean
        """
        return self.configs.pop(key.value, None)

    def search(self, key: Config, *args, optional: bool = False):
        """
        Get an item using "path" of args in the json config.
        :param optional: true if the value can have empty value (i.e., []), default to NOT optional
        :param key: Config (choice of configurations from discrete enumeration)
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

        if result is None and not optional:
            raise Exception('\n\tcode:\t-5\n'
                            '\ttext:\tValue {} not defined in {}\n'
                            '\tsource:\tsrc.utils.Configurable.search'.format(
                ''.join([arg + '->' for arg in args[:-1]]) + args[-1], key))

        if isinstance(result, list):
            if len(result) < 1 and not optional:
                raise Exception('\n\tcode:\t-6\n'
                                '\ttext:\tValue for {} is empty in {}\n'
                                '\tsource:\tsrc.utils.Configurable.search'.format(
                    ''.join([arg + '->' for arg in args[:-1]]) + args[-1], key))

        return result

    def path(self, key: Config, *args, is_dir: bool = False, is_absolute: bool = False):
        """
        Build a path for an item specified in same style as self.search().
        Expects the item returned by self.search(key, *args) to be a list.
        :param is_absolute: flag to make the path absolute
        :param is_dir: if true, will add trailing slash (system nonspecific) to path
        :param key: Config (choice of configurations from discrete enumeration)
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
        :param config_path: the string path to load
        :return: json data (dict or list)
        """
        with open(config_path, "r") as handle:
            # print('load "{}" --> key "{}"'.format(config, key))
            return json.load(handle)

    def search_mode(self, mode: Type[Enum], key: Config, optional: bool = False):
        """
        :param mode: an Enum mode that is being searched. it MUST have variable config, which is the name
                     to search for in the X.json file
        :return: the Enum version of the mode that is specified by the config
        """

        return self.search_multi_mode(key=key, mode=mode, count=1,optional=optional)[0]

    def search_multi_mode(self, key: Config, mode: Type[Enum] = None, modes: List[Type[Enum]] = None,
                          count: int = None, optional: bool = False) -> list:
        """
        :param key: Config (choice of configurations from discrete enumeration)
        :param mode: Option for pipeline functionality (see Enums)
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

            modes_in_config = self.search(key, 'modes', mode.config.value,optional=optional)

            if not isinstance(modes_in_config, list):
                modes_in_config = [modes_in_config]

            list_results += [option for option in mode
                             if str(option).split('.')[1] in modes_in_config]

        if count is not None:
            if len(list_results) != count and not optional:
                raise Exception('\n\tcode:\t-3\n'
                                '\ttext:\t{} matches found when {} were expected.\n'
                                '\tsource:\tsrc.utils.Configurable.search_multi_mode'.format(len(list_results), count))
            if len(list_results)==0 and optional:
                list_results = [None]
    
        return list_results

    @staticmethod
    def validate_path(config_path: str):
        """
        :param config_path: path to config we will load, this makes sure it is a JSON
        :return:
        """
        # if last 5 characters of file path are NOT '.json', raise an Exception
        if not config_path[-5:] == '.json':
            raise Exception('\n\tcode:\t-1'
                            '\ttext:\tFile path must end in .json\n'
                            '\tsource:\tconfigurable.py or map.py')
