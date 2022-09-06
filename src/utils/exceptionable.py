#!/usr/bin/env python3.7

"""Defines the Exceptionable Class.

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


class Exceptionable(Configurable):
    """Used to handle exceptions in ASCENT code."""

    def __init__(self, mode: SetupMode, config=None):
        """Initialize the Exceptionable class instance.

        :param mode: SetupMode, determines if Configurable loads new JSON or uses old data
        :param config: if SetupMode.OLD, this is the data. if SetupMode.NEW, this is str path to JSON
        """
        if mode == SetupMode.OLD:
            Configurable.__init__(self, mode, Config.EXCEPTIONS, config)
        else:  # mode == SetupMode.NEW
            Configurable.__init__(
                self,
                mode,
                Config.EXCEPTIONS,
                os.path.join('config', 'system', 'exceptions.json'),
            )

    def throw(self, code):
        """Use this to throw an exception.

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
            f'\n\tcode:\t{exception.get("code")}\n'
            f'\ttext:\t{exception.get("text")}\n'
            f'\tsource:\t{inspect.stack()[1].filename}'
        )
