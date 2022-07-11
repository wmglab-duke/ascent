#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import inspect

# builtins
import os

import numpy as np

from .configurable import Configurable
from .enums import Config, SetupMode

"""
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


class Exceptionable(Configurable):
    def __init__(self, mode: SetupMode, config=None):
        """
        :param mode: SetupMode, determines if Configurable loads new JSON or uses old data
        :param config: if SetupMode.OLD, this is the data. if SetupMode.NEW, this is str path to JSON
        """

        if mode == SetupMode.OLD:
            Configurable.__init__(self, mode, Config.EXCEPTIONS, config)
        else:  # mode == SetupMode.NEW
            Configurable.__init__(self, mode, Config.EXCEPTIONS, os.path.join('config', 'system', 'exceptions.json'))

    def throw(self, code):
        """
        Use this to throw an exception

        example:
            if FATAL_CONDITION:
                self.throw(CODE)

        :param code: index of exception in json file (i.e. exceptions.json)
        :return: full message (with code and text)
        """

        codelist = [x['code'] for x in self.configs[Config.EXCEPTIONS.value]]

        # force to exception 0 if incorrect bounds
        if code not in codelist:
            code_ind = 0
        else:
            code_ind = np.where(np.array(codelist) == code)[0][0]

        exception = self.configs[Config.EXCEPTIONS.value][code_ind]
        # note that the json purposefully has the redundant entry "code"
        # this is done for ease of use and organizational purposes
        raise Exception(
            '\n\tcode:\t{}\n'
            '\ttext:\t{}\n'
            '\tsource:\t{}'.format(exception.get('code'), exception.get('text'), inspect.stack()[1].filename)
        )
