#!/usr/bin/env python3.7

"""
File:       ExceptionManager.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""

from src.utils.Configurable import Configurable


class ExceptionManager(Configurable):

    def __init__(self, path):
        # set up superclass(es)
        Configurable.__init__(self, path)

    def message(self, code):
        """
        :param code: index of exception in json file (i.e. exceptions.json)
        :return: full message (with code and text)
        """

        # force to exception 0 if incorrect bounds
        if code not in range(1, len(self.config)):
            code = 0

        exception = self.config[code]
        # note that the json purposefully has the redundant entry "code"
        # this is done for ease of use and organizational purposes
        return '\n\tcode:\t{}\n' \
               '\ttext:\t{}\n' \
               '\tsource:\t{}'.format(exception.get('code'),
                                      exception.get('text'),
                                      exception.get('source'))
