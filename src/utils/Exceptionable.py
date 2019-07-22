#!/usr/bin/env python3.7

"""
File:       Exceptionable.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""
import json


class Exceptionable:

    def __init__(self, config_file_path: str):
        # NOTE: BUILTIN Configurable FUNCTIONALITY TO NOT OVERRIDE WHEN BOTH ARE INHERITED

        with open(config_file_path, "r") as json_file:
            self.exception_config: dict = json.load(json_file)

    def throw(self, code):
        """
        :param code: index of exception in json file (i.e. exceptions.json)
        :return: full message (with code and text)
        """

        # force to exception 0 if incorrect bounds
        if code not in range(1, len(self.exception_config)):
            code = 0

        exception = self.exception_config[code]
        # note that the json purposefully has the redundant entry "code"
        # this is done for ease of use and organizational purposes
        raise Exception('\n\tcode:\t{}\n' \
                        '\ttext:\t{}\n' \
                        '\tsource:\t{}'.format(exception.get('code'),
                                               exception.get('text'),
                                               exception.get('source')))
