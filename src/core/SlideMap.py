#!/usr/bin/env python3.7

"""
File:       SlideMap.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""

# builtin imports
import datetime as dt

import numpy as np

# user imports
from src.utils import *


class SlideMap(Exceptionable, Configurable):

    def __init__(self, main_config, exception_config):
        """
        :param new: indicate whether or not to build new Map
        :param path: MUST exist (to find path to save/load)
        """

        # set up super classes
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, 'main', main_config)

    def __build(self):
        return

    def __path(self):
        """
        :return: newly generated path name with date stamp
        """
        return 'map_{}.csv'.format(dt.datetime.now().strftime('%m%d%Y'))


# %% quick class to keep track of slides
class Slide:
    def __init__(self, cassette, number, position):
        self.cassette = cassette
        self.number = number
        self.position = position

    @staticmethod
    def get(from_list, cassette, number):
        return list(filter(lambda s: (s.cassette == cassette) and (s.number == number), from_list))[0]


# %% quick class to keep track of electrodes
class Electrode:
    """
    start: Slide whose position is start of mark (blue dye)
    end: Slide whose position is end of mark (blue dye)
    """

    def __init__(self, start: Slide, end: Slide):
        self.start: Slide = start
        self.end: Slide = end

    def position(self):
        return np.mean([self.start.position,
                        self.end.position])

    def __add__(self, other: 'Electrode'):
        return self.position() + other.position()

    def __sub__(self, other: 'Electrode'):
        return self.position() - other.position()

