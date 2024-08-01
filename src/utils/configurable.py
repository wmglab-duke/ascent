#!/usr/bin/env python3.7

"""Defines the Configurable class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import json

from .enums import Config, Enum, SetupMode, os


class Configurable:
    """Handles loading and writing of JSON config files.

    Meant to be inherited for configurable functionality.
    Expandable and allows for quick src to configuration file data (in addition to path building method).
    """

    def __init__(
        self,
        mode: SetupMode = None,
        key: Config = None,
        config: str | dict | list = None,
    ):
        """Initilize the configurable class.

        :param mode: SetupMode, determines if loads new JSON or uses old data
        :param key: Config (choice of configurations from discrete enumeration);
            choice of SAMPLE, MODEL, SIM (these are the big ones), EXCEPTIONS, or any other added configs
        :param config: if mode is NEW, this is file path str, else (mode is OLD) this is already loaded config data
        """
        # if self.configs does not already exist (i.e. this is first Configurable call), create it
        if not hasattr(self, 'configs'):
            self.configs = {}

        if len([item for item in [mode, key, config] if item is None]) == 0:
            self.add(mode, key, config)

    def add(self, mode: SetupMode, key: Config, config: str | dict):
        """Add a config to self.configs.

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
        """Remove a config from self.configs.

        :param key: Config (choice of configurations from discrete enumeration)
        :return: configs with the passed in key dict removed. If the key did not exist, None is returned.
        """
        return self.configs.pop(key.value, None)

    def search(self, key: Config, *args, optional: bool = False):
        """Get an item using "path" of args in the json config.

        :param optional: true if the value can have empty value (i.e., []), default to NOT optional
        :param key: Config (choice of configurations from discrete enumeration)
        :param args: list "path" to item within json (str or int)
        :raises TypeError: If the search parameter is not of type str or int
        :raises KeyError: If the key is not found in the config
        :raises IndexError: If a list value has length of 0
        :return: final specified item
        """
        result = self.configs[key.value]
        for arg in args:
            if isinstance(result, list):
                pass
            if isinstance(arg, (str, int)):
                result = result.get(arg)
            else:
                raise TypeError(f'Invalid search parameter type:\tTYPE: {type(arg)}\tVALUE: {arg}\n')

            if result is None:
                if not optional:
                    raise KeyError(
                        f'Value {"".join([arg + "->" for arg in args[:-1]]) + args[-1]} not defined in {key}'
                    )
                return result

        if isinstance(result, list) and len(result) < 1 and not optional:
            raise IndexError(f'Value {"".join([arg + "->" for arg in args[:-1]]) + args[-1]} is empty in {key}')

        return result

    def path(self, key: Config, *args, is_dir: bool = False, is_absolute: bool = False):
        """Build a path for an item specified in same style as self.search().

        Expects the item returned by ``self.search(key, *args)`` to be a list.

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
        """Load in json data and returns to user, assuming it has already been validated.

        :param config_path: the string path to load
        :return: json data (dict or list)
        """
        with open(config_path) as handle:
            return json.load(handle)

    @staticmethod
    def write(data: list | dict, dest_path):
        """Write JSON object to file.

        :param data: The data to write.
        :param dest_path: The destination path.
        """
        with open(dest_path, "w") as handle:
            handle.write(json.dumps(data, indent=2))

    def search_mode(self, mode: type[Enum], key: Config, optional: bool = False):
        """Search for a single mode.

        :param mode: an Enum mode that is being searched. it MUST have variable config, which is the name
                     to search for in the X.json file
        :param key: Config type to look in
        :param optional: if False, will raise an exception if the mode is not found
        :return: the Enum version of the mode that is specified by the config
        """
        return self.search_multi_mode(key=key, mode=mode, count=1, optional=optional)[0]

    def search_multi_mode(
        self,
        key: Config,
        mode: type[Enum] = None,
        modes: list[type[Enum]] = None,
        count: int = None,
        optional: bool = False,
    ) -> list:
        """Search for multiple modes.

        :param key: Config (choice of configurations from discrete enumeration)
        :param mode: mode to search for
        :param modes: modes to search for
        :param count: count of results
        :param optional: if false, error on missing mode
        :raises ValueError: no mode or modes specified
        :raises IndexError: count does not match the number of results found
        :return: list of modes found
        """
        list_results = []

        if mode is not None:
            modes = [mode]

        if modes is None:
            raise ValueError('At least one mode type must be provided.')

        for mode in modes:
            modes_in_config = self.search(key, 'modes', mode.config.value, optional=optional)

            if not isinstance(modes_in_config, list):
                modes_in_config = [modes_in_config]

            list_results += [option for option in mode if str(option).split('.')[1] in modes_in_config]

        if count is not None:
            if len(list_results) == 0 and optional:
                list_results = [None]
            elif len(list_results) != count:
                raise IndexError(f'{len(list_results)} matches found when {count} were expected.\n')

        return list_results

    @staticmethod
    def validate_path(config_path: str):
        """Validate the config file path.

        :param config_path: path to config we will load, this makes sure it is a JSON
        :raises ValueError: if the path is not a JSON file
        """
        # if last 5 characters of file path are NOT '.json', raise an Exception
        if not config_path[-5:] == '.json':
            raise ValueError(f'File path {config_path} does not end in .json')
