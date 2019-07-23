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
import os

# user imports
from src.utils import *


class SlideMap(Exceptionable, Configurable):

    def __init__(self, main_config, exception_config, mode: SetupMode = SetupMode.NEW):
        """

        :param main_config:
        :param exception_config:
        :param mode:
        :param file:
        """

        # set up super classes
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, main_config)

        # "root" of data within master config
        # stored as list because will be "splatted" later when using self.search and self.path
        self.data_root: list = ['slide_map']

        # store mode if later requested by user (idk why they would want it though?)
        self.mode: SetupMode = mode

        if self.mode == SetupMode.NEW:
            # set paths
            self.source_path = self.path(ConfigKey.MASTER, *self.data_root, 'paths', 'source',
                                         isdir=True, isabsolute=True)
            self.output_path = os.path.join(self.path(ConfigKey.MASTER, *self.data_root, 'paths', 'output'),
                                            self.generate_filename())

            # init self.slides so the IDE doesn't yell at me
            self.slides = []

            # build and resize slide map
            self.__build()
            self.__resize()

        else:

            pass
            # load in data from json

    def __build(self):
        # load in and compute parameters
        cassettes = self.path(ConfigKey.MASTER, *self.data_root, 'cassettes')
        allowed_diffs = self.path(ConfigKey.MASTER, *self.data_root, 'allowed_differences')
        number_regex = self.path(ConfigKey.MASTER, *self.data_root, 'number_regex')
        cassette_start_pos = self.path(ConfigKey.MASTER, *self.data_root, 'start_position')
        position = cassette_start_pos
        scale = self.path(ConfigKey.MASTER, *self.data_root, 'scale')
        large_skip = self.path(ConfigKey.MASTER, *self.data_root, 'skips', 'large') * scale
        cassette_skip = self.path(ConfigKey.MASTER, *self.data_root, 'skips', 'cassette') * scale
        normal_skip = self.path(ConfigKey.MASTER, *self.data_root, 'skips', 'normal') * scale

        # get files (assumes first iteration of os.walk)
        # files are always the 3rd item in a tuple returned by each iteration of os.walk
        files = [result for result in os.walk(self.source_path)][0][2]

        # %% master loop for finding positions
        for k, cassette_code in enumerate(cassettes):
            cassette = []
            # find all files from this cassette
            filtered_files = list(filter(lambda f: re.search(cassette_code, f), files))
            for i, file in enumerate(filtered_files):
                # we know that there MUST be a match now because it matched to the cassette name
                match = number_regex.search(file).group(0)
                # get the number from that match
                number = int(match[:len(match) - 1])

                # if first slide in cassette
                if i == 0:
                    position = cassette_start_pos

                else:
                    # if only a difference of 1 between this slide's number and the last's
                    diff = abs(number - int(cassette[i - 1].number))
                    if diff in allowed_diffs:
                        position += diff * normal_skip  # rule: move 5um for consecutive slice (multiplied by number of skips)
                    else:
                        position += large_skip  # rule: move 100um for skip in slides

                    # if last slide in cassette, set next cassette start position and offset indices
                    if (i + 1) == len(filtered_files):
                        cassette_start_pos = position + cassette_skip  # account for trimming
                # add this to the current 'row' of slides
                cassette.append(SlideMap.Slide(cassette_code,
                                               number,
                                               position))
            # add this cassette to the total list of slides
            self.slides += cassette


        #TODO: SAVING FILE AND RESIZING

        return

    def __resize(self):
        return

    # might just remove this; commenting out for now because super nonessential to basic functionality
    # def rebuild(self, new: bool = False, config_path: str = ):
    #
    #     self.reload(ConfigKey.MASTER)
    #     return self.__build()


    @staticmethod
    def generate_filename():
        """
        :return: newly generated path name with date stamp
        """
        return '{}.json'.format(dt.datetime.now().strftime('%m_%d_%Y'))

    #%% helper classes... self.map will be stored as a list of Slide objects
    # quick class to keep track of slides
    class Slide:
        def __init__(self, cassette, number, position):
            self.cassette = cassette
            self.number = number
            self.position = position

        @staticmethod
        def get(from_list, cassette, number):
            return list(filter(lambda s: (s.cassette == cassette) and (s.number == number), from_list))[0]

    # quick class to keep track of electrodes
    class Electrode:
        """
        start: Slide whose position is start of mark (blue dye)
        end: Slide whose position is end of mark (blue dye)
        """

        def __init__(self, start: 'SlideMap.Slide', end: 'SlideMap.Slide'):
            self.start: SlideMap.Slide = start
            self.end: SlideMap.Slide = end

        def position(self):
            return np.mean([self.start.position,
                            self.end.position])

        def __add__(self, other: 'SlideMap.Electrode'):
            return self.position() + other.position()

        def __sub__(self, other: 'SlideMap.Electrode'):
            return self.position() - other.position()

