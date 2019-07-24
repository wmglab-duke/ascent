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
import re
import json
from typing import List

# user imports
from src.utils import *


class SlideMap(Exceptionable, Configurable):

    def __init__(self, main_config, exception_config, mode: SetupMode = SetupMode.NEW):
        """
        :param main_config:
        :param exception_config:
        :param mode:
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
                                            '{}.json'.format(dt.datetime.now().strftime('%m_%d_%Y')))

            # init self.slides
            self.slides: List[SlideMap.Slide] = []

            # build, resize, and write to file
            self.__build()
            self.__resize()
            self.__write()

        elif self.mode == SetupMode.OLD:
            self.source_path = self.path(ConfigKey.MASTER, *self.data_root, 'paths', 'old')
            self.output_path = self.source_path

            # make sure ends in ".json" (defined in Configurable)
            self.validate_path(self.source_path)

            self.slides = self.json_to_list()

    def find(self, cassette: str, number: int) -> 'SlideMap.Slide':
        return list(filter(lambda s: (s.cassette == cassette) and (s.number == number), self.slides))[0]

    def __build(self):
        """
        This method is adapted from generate_slide_map.py, which was the original non-OOP version of the algorithm.
        """
        # load in and compute parameters
        cassettes = self.search(ConfigKey.MASTER, *self.data_root, 'cassettes')
        allowed_diffs = self.search(ConfigKey.MASTER, *self.data_root, 'allowed_differences')
        number_regex = re.compile(self.search(ConfigKey.MASTER, *self.data_root, 'number_regex'))  # compile regex
        cassette_start_pos = self.search(ConfigKey.MASTER, *self.data_root, 'start_position')
        position = cassette_start_pos
        large_skip = self.search(ConfigKey.MASTER, *self.data_root, 'skips', 'large')
        cassette_skip = self.search(ConfigKey.MASTER, *self.data_root, 'skips', 'cassette')
        normal_skip = self.search(ConfigKey.MASTER, *self.data_root, 'skips', 'normal')
        is_up = self.search(ConfigKey.MASTER, *self.data_root, 'skips', 'up')

        # if the slides are not being placed in the upwards direction,
        # invert all the steps (they are expected to be negative)
        if not is_up:
            large_skip *= -1
            cassette_skip *= -1
            normal_skip *= -1

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
                        # rule: move 5um for consecutive slice (multiplied by number of skips)
                        position += diff * normal_skip
                    else:
                        # rule: move 100um for skip in slides
                        position += large_skip

                    # if last slide in cassette, set next cassette start position and offset indices
                    if (i + 1) == len(filtered_files):
                        cassette_start_pos = position + cassette_skip  # account for trimming
                # add this to the current 'row' of slides
                cassette.append(SlideMap.Slide(cassette_code,
                                               number,
                                               position))
            # add this cassette to the total list of slides
            self.slides += cassette

    def __resize(self):
        # get the data about the reference slides
        start_slide_data = self.search(ConfigKey.MASTER, *self.data_root, 'resize_reference', 'start_slides')
        end_slide_data = self.search(ConfigKey.MASTER, *self.data_root, 'resize_reference', 'end_slides')

        # get those slides from the data
        start_slides = [self.find(item.get('cassette'), item.get('number')) for item in start_slide_data]
        end_slides = [self.find(item.get('cassette'), item.get('number')) for item in end_slide_data]

        # find reference distance and scale factor
        self.reference = SlideMap.Reference(start_slides, end_slides)
        self.reference_distance = self.search(ConfigKey.MASTER, *self.data_root, 'resize_reference', 'distance')
        self.scale = self.reference.scale_for_distance(self.reference_distance)

        # shift slides to 0 as origin and scale from there
        lowest_position = min([slide.position for slide in self.slides])
        for slide in self.slides:
            slide.position = round((slide.position - lowest_position) * self.scale)

    def __write(self):
        with open(self.output_path, 'w+') as file:
            file.write(self.list_to_json())

    def list_to_json(self) -> str:
        result = []
        for slide in self.slides:
            result.append({
                "cassette": slide.cassette,
                "number": slide.number,
                "position": slide.position
            })

        return json.dumps(result, indent=4)

    def json_to_list(self):
        data = self.load(self.source_path)
        return [SlideMap.Slide(item.get('cassette'),
                               item.get('number'),
                               item.get('position')) for item in data]


    # might just remove this; commenting out for now because super nonessential to basic functionality
    # def rebuild(self, new: bool = False, config_path: str = ):
    #
    #     self.reload(ConfigKey.MASTER)
    #     return self.__build()

    #%% helper classes... self.map will be stored as a list of Slide objects
    # quick class to keep track of slides
    class Slide:
        def __init__(self, cassette, number, position):
            self.cassette = cassette
            self.number = number
            self.position = position

        def __repr__(self):
            return '\tcas: {}\n\tnum: {}\n\tpos: {}\n\n'.format(self.cassette, self.number, self.position)

    # quick class to keep track of a reference distance for resizing (i.e. space between electrodes)
    class Reference:
        def __init__(self, start: List['SlideMap.Slide'], end: List['SlideMap.Slide']):
            # find average start and end positions  and save as instance variables for printing if needed
            self.start = np.mean([slide.position for slide in start])
            self.end = np.mean([slide.position for slide in end])
            # calculate reference distance
            self.abs_distance = abs(self.end - self.start)

        def scale_for_distance(self, distance: int) -> float:
            return distance / float(self.abs_distance)

        def __repr__(self):
            return '\tstart pos:\t{}\n\tend pos:\t{}\n\tabs dist:\t{}\n\n'.format(self.start, self.end, self.abs_distance)
