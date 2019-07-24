#!/usr/bin/env python3.7

"""
File:       Exceptionable.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW
    Centralized way to organize and "throw" exceptions.

    INITIALIZER
    See docstring of __init__.

    PROPERTIES
    none, but creates key/value in configs (inherited form Configurable) that pertains to exception data

    METHODS
    throw

"""

from src.utils import SetupMode, Configurable, ConfigKey


class Exceptionable(Configurable):

    def __init__(self, mode: SetupMode, config):
        """
        :param mode: SetupMode, determines if Configurable loads new JSON or uses old data
        :param config: if SetupMode.OLD, this is the data. if SetupMode.NEW, this is str path to JSON
        """

        Configurable.__init__(self, mode, ConfigKey.EXCEPTIONS, config)

    def throw(self, code):
        """
        Use this to throw an exception

        example:
            if FATAL_CONDITION:
                self.throw(CODE)

        :param code: index of exception in json file (i.e. exceptions.json)
        :return: full message (with code and text)
        """

        # force to exception 0 if incorrect bounds
        if code not in range(1, len(self.configs[ConfigKey.EXCEPTIONS.value])):
            code = 0

        exception = self.configs[ConfigKey.EXCEPTIONS.value][code]
        # note that the json purposefully has the redundant entry "code"
        # this is done for ease of use and organizational purposes
        raise Exception('\n\tcode:\t{}\n'
                        '\ttext:\t{}\n'
                        '\tsource:\t{}'.format(exception.get('code'),
                                               exception.get('text'),
                                               exception.get('source')))
