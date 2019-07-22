#!/usr/bin/env python3.7

"""
File:       Exceptionable.py
Author:     Jake Cariello
Created:    July 20, 2019

Description:

    OVERVIEW
    Meant to be inherited for configurable functionality. Expandable and allows for quick access
    to configuration file data (in addition to path building method).

    INITIALIZER

    PROPERTIES

    METHODS

"""

import json
import os


class Configurable:

    def __init__(self, config_file_path: str):

        if not config_file_path[-5:] == '.json':
            raise Exception('\n\tcode:\t-2n'
                            '\ttext:\tConfiguration file path must end in .json\n'
                            '\tsource:\tConfigurable.py')

        with open(config_file_path, "r") as json_file:
            self.config: dict = json.load(json_file)

    def get(self, *args):
        """
        Get an item using "path" of args in the json config.
        :param args: list "path" to item within json (str or int)
        :return: final specified item
        """
        result = self.config
        for arg in args:
            if isinstance(arg, str):
                result = result.get(arg)
            else:  # must be integer?
                result = result[arg]
        return result

    def path_get(self, *args):
        """
        Build a path for an item specified in same style as self.get()
        REQUIRES that there be a str "root" on same level as lowest item
        :param args: "path" to desired item
        :return: final path to item (with system formatting!)
        """
        root = self.get(*args[:-1]).get('root')
        spec = self.get(*args)
        return os.path.join(root, spec)
