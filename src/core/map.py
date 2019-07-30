#!/usr/bin/env python3.7

"""
File:       map.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW
    Synthesizes and stores slide information.

    INITIALIZER
    MUST provide main configuration data as well as exception configuration data.
    Optionally, indicate that the setup mode is old, meaning that it will attempt to load existing data from JSON.
    --> Some informal testing with a directory of 224 slides showed that loading up an existing JSON saved about
        22 milliseconds (@ ~0.099s) when compared to building and saving a new JSON (@ ~ 0.121s).
    Note that the functionality of this class is EXTREMELY dependent on the structure of the JSON files it deals with.

    I considered adding path-building functionality to this class, but ultimately decided to defer that functionality
    to a "SlideManager" class (not created as of 7/24/2019). This was done so the configuration can be read and the
    appropriate data store in the master configuration (or similar). That way, a COMSOL-interfacing program will be able
    to easily access the data from one place.

    PROPERTIES
    data_root
    mode
    source_path
    output_path
    slides
    reference
    reference_distance
    scale
    Slide (utility class)
    Reference (utility class)

    METHODS
    __init__
    find (returns slide that matches the provided cassette and number)
    __build
    __resize
    write
    list_to_json
    json_to_list
    clean_file_names (not system-independent)


"""

import datetime as dt
import numpy as np
import os
import re
import json
import warnings
from typing import List

from src.utils import *


class Map(Exceptionable, Configurable):

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

        # output path for new slide map (and allows for old slide map to be edited and rewritten!)
        self.output_path = os.path.join(self.path(ConfigKey.MASTER, *self.data_root, 'paths', 'output'),
                                        '{}.json'.format(dt.datetime.now().strftime('%m_%d_%Y')))

        # get sample string to pass to Map.Slide
        self.sample = self.search(ConfigKey.MASTER, 'sample')

        # init self.slides
        self.slides: List[Map.Slide] = []

        if self.mode == SetupMode.NEW:
            # source DIRECTORY
            self.source_path = self.path(ConfigKey.MASTER, *self.data_root, 'paths', 'source',
                                         is_dir=True, is_absolute=True)

            # build, resize, and write to file
            self.__build()
            self.__resize()
            self.write()

        elif self.mode == SetupMode.OLD:
            # source FILE
            self.source_path = self.path(ConfigKey.MASTER, *self.data_root, 'paths', 'old')

            # make sure ends in ".json" (defined in Configurable)
            self.validate_path(self.output_path)

            # build slides list from json file
            self.slides = self.json_to_list()

        else:
            # the above if statements are exhaustive, so this should be unreachable
            print('how the hell?')

    def find(self, cassette: str, number: int) -> 'Map.Slide':
        """
        Returns first slide that matches search parameters (there should only be one, though).
        :param cassette: cassette to narrow search
        :param number: number within that cassette (should narrow search to 1 slide)
        :return: the Slide object (note that the list is being indexed into at the end: [0])
        """
        return list(filter(lambda s: (s.cassette == cassette) and (s.number == number), self.slides))[0]

    def __build(self):
        """
        This method is adapted from generate_slide_map.py, which was the original non-OOP version of the algorithm.
        In addition, there aren't checks for throwing exceptions, which may be useful to add later before distribution.

        Note: private method because this should only be called from the constructor
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
                cassette.append(Map.Slide(cassette_code,
                                               number,
                                               position,
                                               os.path.join(self.source_path, file)))
            # add this cassette to the total list of slides
            self.slides += cassette

    def __resize(self):
        """
        Note: private method because user should not need to resize once built?
        """

        # get the data about the reference slides
        start_slide_data = self.search(ConfigKey.MASTER, *self.data_root, 'resize_reference', 'start_slides')
        end_slide_data = self.search(ConfigKey.MASTER, *self.data_root, 'resize_reference', 'end_slides')

        # get those slides from the data
        start_slides = [self.find(item.get('cassette'), item.get('number')) for item in start_slide_data]
        end_slides = [self.find(item.get('cassette'), item.get('number')) for item in end_slide_data]

        # find reference distance and scale factor
        self.reference = Map.Reference(start_slides, end_slides)
        self.reference_distance = self.search(ConfigKey.MASTER, *self.data_root, 'resize_reference', 'distance')
        self.scale = self.reference.scale_for_distance(self.reference_distance)

        # shift slides to 0 as origin and scale from there
        lowest_position = min([slide.position for slide in self.slides])
        for slide in self.slides:
            slide.position = round((slide.position - lowest_position) * self.scale)

    def write(self):
        """
        Note: not private to allow user to make changes if required, then write those changes to file.
        """
        with open(self.output_path, 'w+') as file:
            file.write(self.list_to_json())

    #%% conversion methods... might make these static in the future?
    # definitely won't put these in some json utility class because they aren't involved in writing/reading
    # instead, they are for interpreting Map-specific data, so nothing outside this class should need to use them

    def list_to_json(self) -> str:
        result = []
        for slide in self.slides:
            result.append({
                "cassette": slide.cassette,
                "number": slide.number,
                "position": slide.position,
                "raw_source": slide.raw_source,
            })

        return json.dumps(result, indent=2)

    def json_to_list(self) -> list:
        data = self.load(self.source_path)
        return [Map.Slide(item.get('cassette'),
                               item.get('number'),
                               item.get('position'),
                               item.get('raw_source')) for item in data]

    def build_target_filesystem(self):
        """
        Build filesystem under data/SAMPLE/ and copy required files (i.e. raw.tif, fascicle.tif, nerve.tif). This
        function uses self.slides as a guide for the files to copy, so the Map can be customized if data is loaded
        in from a custom (even hand-typed) configuration (when SetupMode.OLD is flagged).
        """

        pass

    #%% utility
    @staticmethod
    def clean_file_names():
        """
        Jake Cariello
        July 24, 2019
        Utility method for cleaning file names.
        It is not dynamic or system-independent at the time because it is a specific thing that I required.
        If it becomes clear that this is required for core functionality, I will rewrite the method.
        """
        warnings.warn('METHOD clean_file_names IS NOT SYSTEM-INDEPENDENT!')

        dir_to_parse = '/Users/jakecariello/Box/SPARCpy/data/input/samples/Cadaver54-3'

        prefixes = ['Cadaver54-3']

        remove_keys = ['.dxf']

        for root, dirs, files in os.walk(dir_to_parse):
            for file in files:
                for prefix in prefixes:
                    if re.match(prefix, file) is not None:
                        # remove leading code (separated by '_') and any extra '_'
                        new_file = '_'.join([f for f in file.split('_')[1:] if f is not ''])
                        os.rename('{}/{}'.format(root, file),
                                  '{}/{}'.format(root, new_file))

                for key in remove_keys:
                    if re.search(key, file) is not None:
                        os.remove('{}/{}'.format(root, file))

    #%% helper classes... self.map will be stored as a list of Slide objects
    # quick class to keep track of slides
    class Slide:
        def __init__(self, cassette: str, number: int, position: int, raw_source: str):
            self.cassette = cassette
            self.number = number
            self.position = position
            self.raw_source = raw_source

            # (directory, file) = os.path.split(raw_source)  # returns tuple
            # (name, extension) = tuple(file.split('.'))
            #
            # # build source paths
            # self.fascicle_source = os.path.join(directory,
            #                                     'fascicles',
            #                                     '.'.join(['_'.join([name, 'fascicle']), extension]))
            # self.nerve_source = os.path.join(directory,
            #                                  'nerves',
            #                                  '.'.join(['_'.join([name, 'nerve']), extension]))

        def __repr__(self):
            return '\tcas:\t{}\tnum:\t{}\n\tpos:\t{}\n\n'.format(self.cassette,
                                                                 self.number,
                                                                 self.position)

    # quick class to keep track of a reference distance for resizing (i.e. space between electrodes)
    class Reference:
        def __init__(self, start: List['Map.Slide'], end: List['Map.Slide']):
            # find average start and end positions  and save as instance variables for printing if needed
            self.start = np.mean([slide.position for slide in start])
            self.end = np.mean([slide.position for slide in end])
            # calculate reference distance
            self.abs_distance = abs(self.end - self.start)

        def scale_for_distance(self, distance: int) -> float:
            return distance / float(self.abs_distance)

        def __repr__(self):
            return '\tstart pos:\t{}\n\tend pos:\t{}\n\tabs dist:\t{}\n\n'.format(self.start,
                                                                                  self.end,
                                                                                  self.abs_distance)
