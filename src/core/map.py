#!/usr/bin/env python3.7

"""
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
    to a "SlideManager" class. This was done so the configuration can be read and the appropriate data store in the
    SAMPLE configuration (or similar). That way, a COMSOL-interfacing program will be able to easily src the data from
    one place.

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

# builtins
import datetime as dt
import numpy as np
import os
import re
import json
import warnings
from typing import List

# access
from src.utils import *


class Map(Exceptionable, Configurable):
    """
    Required (Config.) JSON's
        SAMPLE
    """

    def __init__(self, exception_config):
        """
        :param main_config:
        :param exception_config:
        :param mode:
        """

        # set up super classes
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

    def init_post_config(self, mode: SetupMode = SetupMode.NEW):

        # "root" of data within SAMPLE config
        # stored as list because will be "splatted" later when using self.search and self.path
        self.data_root = 'slide_map'

        # store mode if later requested by user (idk why they would want it though?)
        self.mode: SetupMode = mode

        # get sample string to pass to Map.Slide
        self.sample = self.search(Config.SAMPLE, 'sample')

        # init self.slides
        self.slides: List[SlideInfo] = []

        if self.mode == SetupMode.NEW:
            raise Exception('NOT IMPLEMENTED')
            
            # self.output_path = os.path.join(self.path(Config.SAMPLE, self.data_root, 'paths', 'output'))
            # 
            # # source DIRECTORY
            # self.source_path = self.path(Config.SAMPLE, self.data_root, 'paths', 'source',
            #                              is_dir=True, is_absolute=False)
            # 
            # # build, resize, and write to file
            # self.__build()
            # # self.__resize()
            # self.write()

        elif self.mode == SetupMode.OLD:
            # source FILE
            self.source_path = self.path(Config.SAMPLE, "map_path")
            # self.source_path = self.path(Config.SAMPLE, self.data_root, 'paths', 'old')

            self.output_path = self.source_path

            # make sure ends in ".json" (defined in Configurable)
            self.validate_path(self.output_path)

            # build slides list from json file
            self.slides = self.json_to_list()

        else:
            # the above if statements are exhaustive, so this should be unreachable
            print('how the hell?')

    def find(self, cassette: str, number: int) -> 'SlideInfo':
        """
        Returns first slide that matches search parameters (there should only be one, though).
        :param cassette: cassette to narrow search
        :param number: number within that cassette (should narrow search to 1 slide)
        :return: the Slide object (note that the list is being indexed into at the end: [0])
        """
        result = list(filter(lambda s: (s.cassette == cassette) and (s.number == number), self.slides))
        return result[0] if len(result) != 0 else None

    def __build(self):
        """
        This method is adapted from generate_slide_map.py, which was the original non-OOP version of the algorithm.
        In addition, there aren't checks for throwing exceptions, which may be useful to add later before distribution.

        Note: private method because this should only be called from the constructor
        """
        raise Exception('NOT IMPLEMENTED')

        #
        # # load in and compute parameters
        # cassettes = self.search(Config.SAMPLE, self.data_root, 'cassettes')
        # allowed_diffs = self.search(Config.SAMPLE, self.data_root, 'allowed_differences')
        # number_regex = re.compile(self.search(Config.SAMPLE, self.data_root, 'number_regex'))  # compile regex
        # cassette_start_pos = self.search(Config.SAMPLE, self.data_root, 'start_position')
        # position = cassette_start_pos
        # large_skip = self.search(Config.SAMPLE, self.data_root, 'skips', 'large')
        # cassette_skip = self.search(Config.SAMPLE, self.data_root, 'skips', 'cassette')
        # normal_skip = self.search(Config.SAMPLE, self.data_root, 'skips', 'normal')
        # is_up = self.search(Config.SAMPLE, self.data_root, 'skips', 'up')
        #
        # # if the slides are not being placed in the upwards direction,
        # # invert all the steps (they are expected to be negative)
        # if not is_up:
        #     large_skip *= -1
        #     cassette_skip *= -1
        #     normal_skip *= -1
        #
        # # get files (assumes first iteration of os.walk)
        # # files are always the 3rd item in a tuple returned by each iteration of os.walk
        # files = [result for result in os.walk(self.source_path)][0][2]
        #
        # # %% SAMPLE loop for finding positions
        # for k, cassette_code in enumerate(cassettes):
        #     cassette = []
        #     # find all files from this cassette
        #     filtered_files = list(filter(lambda f: re.search(cassette_code, f), files))
        #     for i, file in enumerate(filtered_files):
        #         # we know that there MUST be a match now because it matched to the cassette name
        #         match = number_regex.search(file).group(0)
        #         # get the number from that match
        #         number = int(match[:match.index('_')])
        #
        #         # NOTE: THIS FINDS POSITION ALONG Z-AXIS; COMMENTING OUT FOR NOW
        #         # if first slide in cassette
        #         # if i == 0:
        #         #     position = cassette_start_pos
        #         #
        #         # else:
        #         #     # if only a difference of 1 between this slide's number and the last's
        #         #     diff = abs(number - int(cassette[i - 1].number))
        #         #     if diff in allowed_diffs:
        #         #         # rule: move 5um for consecutive slice (multiplied by number of skips)
        #         #         position += diff * normal_skip
        #         #     else:
        #         #         # rule: move 100um for skip in slides
        #         #         position += large_skip
        #         #
        #         #     # if last slide in cassette, set next cassette start position and offset indices
        #         #     if (i + 1) == len(filtered_files):
        #         #         cassette_start_pos = position + cassette_skip  # account for trimming
        #         # add this to the current 'row' of slides
        #
        #         position = 0
        #         if len(list(filter(lambda c: c.number == number, cassette))) == 0:
        #             cassette.append(SlideInfo(cassette_code,
        #                                       number,
        #                                       position,
        #                                       self.source_path))
        #     # add this cassette to the total list of slides
        #     self.slides += cassette

    def __resize(self):
        """
        Note: private method because user should not need to resize once built?
        """
        
        raise Exception('NOT IMPLEMENTED')


        # # get the data about the reference slides
        # start_slide_data = self.search(Config.SAMPLE, self.data_root, 'resize_reference', 'start_slides')
        # end_slide_data = self.search(Config.SAMPLE, self.data_root, 'resize_reference', 'end_slides')
        # 
        # # get those slides from the data
        # start_slides = [self.find(item.get('cassette'), item.get('number')) for item in start_slide_data]
        # end_slides = [self.find(item.get('cassette'), item.get('number')) for item in end_slide_data]
        # 
        # # find reference distance and scale factor
        # self.reference = Reference(start_slides, end_slides)
        # self.reference_distance = self.search(Config.SAMPLE, self.data_root, 'resize_reference', 'distance')
        # self.scale = self.reference.scale_for_distance(self.reference_distance)
        # 
        # # shift slides to 0 as origin and scale from there
        # lowest_position = min([slide.position for slide in self.slides])
        # for slide in self.slides:
        #     slide.position = round((slide.position - lowest_position) * self.scale)

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
                "cassette": int(slide.cassette),
                "number": slide.number,
                "position": slide.position,
                "directory": slide.directory[:-1].split(os.sep)
            })

        return json.dumps(result, indent=2)

    def json_to_list(self) -> list:
        data = self.load(self.source_path)
        return [SlideInfo(item.get('cassette'),
                          item.get('number'),
                          item.get('position'),
                          item.get('directory')) for item in data]

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

        dir_to_parse = '/Users/jakecariello/Box/SPARCpy/data/input/samples/Pig11-3'

        prefixes = ['sub-11_sam-3']

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
class SlideInfo:
    def __init__(self, cassette: str, number: int, position: int, directory: str):
        self.cassette = cassette
        self.number = number
        self.position = position
        self.directory = directory

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

    def data(self) -> tuple:
        return self.cassette, self.number, self.position, self.directory

    def __repr__(self):
        return 'cas:\t{}\nnum:\t{}\npos:\t{}\ndir:\t{}'.format(self.cassette,
                                                               self.number,
                                                               self.position,
                                                               self.directory)


# quick class to keep track of a reference distance for resizing (i.e. space between electrodes)
class Reference:
    def __init__(self, start: List[SlideInfo], end: List[SlideInfo]):
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
