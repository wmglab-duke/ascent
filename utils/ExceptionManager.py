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

import json


class ExceptionManager:

    def __init__(self, path):

        with open(path, "r") as json_file:
            self.data = json.load(json_file)

    def message(self, code):
        """
        :param code: index of exception in json file (i.e. exceptions.json)
        :return: full message (with code and text)
        """

        # force to exception 0 if incorrect bounds
        if code not in range(1, len(self.data)):
            code = 0

        exception = self.data[code]
        # note that the json purposefully has the redundant entry "code"
        # this is done for ease of use and organizational purposes
        return 'Exception\n' \
               '\tcode:\t{}\n' \
               '\ttext:\t{}\n' \
               '\tsource:\t{}'.format(exception.get('code'),
                                        exception.get('text'),
                                        exception.get('source'))
