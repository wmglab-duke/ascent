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

from src.utils import SetupMode
from src.utils.Configurable import Configurable


class Exceptionable(Configurable):

    def __init__(self, mode: SetupMode, config):
        self.exceptions_key = 'exceptions'

        Configurable.__init__(self, mode, self.exceptions_key, config)

    def throw(self, code):
        """
        :param code: index of exception in json file (i.e. exceptions.json)
        :return: full message (with code and text)
        """

        # force to exception 0 if incorrect bounds
        if code not in range(1, len(self.configs[self.exceptions_key])):
            code = 0

        exception = self.configs[self.exceptions_key][code]
        # note that the json purposefully has the redundant entry "code"
        # this is done for ease of use and organizational purposes
        raise Exception('\n\tcode:\t{}\n'
                        '\ttext:\t{}\n'
                        '\tsource:\t{}'.format(exception.get('code'),
                                               exception.get('text'),
                                               exception.get('source')))
