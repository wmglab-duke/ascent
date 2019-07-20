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
from utils.ExceptionManager import ExceptionManager
from utils.Exceptionable import Exceptionable

import os
import re
import datetime
import numpy as np


class Map(Exceptionable):

    def __init__(self, new: bool, path: str, exception_manager: ExceptionManager):
        """
        :param new: indicate whether or not to build new Map
        :param path: MUST exist (to find path to save/load)
        """

        # set up superclass
        Exceptionable.__init__(self, exception_manager)

        #%% assign file name
        if path[-1] in ['/', '\\']:  # path is a directory (only makes sense if new map)
            self.file = os.path.join(path[:-1], self.__path())

            if not new:
                self.throw(1)

        else:  # path given is a file
            self.file = path

        #%% choose
        if new:  # new slide map must be generated
            pass

        else:  # old slide map will be used
            pass

    def __build(self):
        pass
        return

    def __path(self):
        """
        :return: newly generated path name with date stamp
        """
        return 'map_{}.csv'.format(datetime.datetime.now().strftime('%m%d%Y'))


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

    def abs_dist_to(self, other_electrode: 'Electrode'):  # use string to delay type eval
        return abs(self.position() - other_electrode.position())

