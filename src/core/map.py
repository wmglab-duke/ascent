#!/usr/bin/env python3.7

"""Defines Map class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

Description:

    OVERVIEW
    Synthesizes and stores slide information.

    INITIALIZER
    MUST provide main configuration data as well as exception configuration data.
    Optionally, indicate that the setup mode is old, meaning that it will attempt to load existing data from JSON.
    --> Some informal testing with a directory of 224 slides showed that loading up an existing JSON saved about
        22 milliseconds (@ ~0.099s) when compared to building and saving a new JSON (@ ~ 0.121s).
    Note that the functionality of this class is EXTREMELY dependent on the structure of the JSON files it deals with.

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


import json
import os
import re
import warnings

import numpy as np

from src.utils import Config, Configurable, SetupMode


class Map(Configurable):
    """Required (Config.) JSON's SAMPLE."""

    def __init__(self):
        """Initialize Map object."""

        # set up super class
        Configurable.__init__(self)
        self.slides = None
        self.output_path = None
        self.source_path = None
        self.mode = None
        self.sample = None
        self.data_root = None

    def init_post_config(self, mode: SetupMode = SetupMode.NEW):
        # "root" of data within SAMPLE config
        # stored as list because will be "splatted" later when using self.search and self.path
        self.data_root = 'slide_map'

        # store mode
        self.mode: SetupMode = mode

        # get sample string to pass to Map.Slide
        self.sample = self.search(Config.SAMPLE, 'sample')

        # init self.slides
        self.slides: list[SlideInfo] = []

        # change mode to SYNTHETIC if no map path provided
        if 'map_path' not in self.search(Config.SAMPLE).keys():
            self.mode = SetupMode.SYNTHETIC

        if self.mode == SetupMode.NEW:  # noqa R506
            raise NotImplementedError("Map with SetupMode.NEW not yet implemented")

        elif self.mode == SetupMode.OLD:
            # source FILE
            self.source_path = self.path(Config.SAMPLE, "map_path")

            self.output_path = self.source_path

            # make sure ends in ".json" (defined in Configurable)
            self.validate_path(self.output_path)

            # build slides list from json file
            self.slides = self.json_to_list()

        elif self.mode == SetupMode.SYNTHETIC:
            # must create a "synthetic" map

            inputpath = os.path.join('input', self.sample)
            if not os.path.exists(inputpath):
                raise FileNotFoundError(f'Input folder specified in sample.json does not exist ({inputpath})')

            # assume path to synthetic map is input/<SAMPLE>/map.json
            self.source_path = os.path.join(inputpath, 'map.json')

            # load/edit map template
            mapper = self.load(os.path.join('config', 'templates', 'map.json'))
            mapper[0]['directory'] = self.source_path.split(os.sep)[:-1]

            # write synthetic map
            with open(os.path.join(self.source_path), "w") as handle:
                handle.write(json.dumps(mapper, indent=2))

            # historical?
            self.output_path = self.source_path

            # build the slides list from this map
            self.slides = self.json_to_list()

        else:
            # the above if statements are exhaustive, so this should be unreachable
            raise ValueError("Invalid SetupMode for Map object")

    def find(self, cassette: str, number: int) -> 'SlideInfo':
        """Returns first slide that matches search parameters (there should
        only be one, though).

        :param cassette: cassette to narrow search
        :param number: number within that cassette (should narrow search to 1 slide)
        :return: the Slide object (note that the list is being indexed into at the end: [0])
        """
        result = list(filter(lambda s: (s.cassette == cassette) and (s.number == number), self.slides))
        return result[0] if len(result) != 0 else None

    def write(self):
        """
        Note: not private to allow user to make changes if required, then write those changes to file.
        """
        with open(self.output_path, 'w+') as file:
            file.write(self.list_to_json())

    def list_to_json(self) -> str:
        result = []
        for slide in self.slides:
            result.append(
                {
                    "cassette": int(slide.cassette),
                    "number": slide.number,
                    "position": slide.position,
                    "directory": slide.directory[:-1].split(os.sep),
                }
            )

        return json.dumps(result, indent=2)

    def json_to_list(self) -> list:
        data = self.load(self.source_path)
        return [
            SlideInfo(
                item.get('cassette'),
                item.get('number'),
                item.get('position'),
                item.get('directory'),
            )
            for item in data
        ]

    # %% utility
    @staticmethod
    def clean_file_names():
        """Jake Cariello July 24, 2019 Utility method for cleaning file names.

        It is not dynamic or system-independent at the time because it
        is a specific thing that I required. If it becomes clear that
        this is required for core functionality, I will rewrite the
        method.
        """
        warnings.warn('METHOD clean_file_names IS NOT SYSTEM-INDEPENDENT!', stacklevel=2)

        dir_to_parse = '/Users/jakecariello/Box/SPARCpy/data/input/samples/Pig11-3'

        prefixes = ['sub-11_sam-3']

        remove_keys = ['.dxf']

        for root, _, files in os.walk(dir_to_parse):
            for file in files:
                for prefix in prefixes:
                    if re.match(prefix, file) is not None:
                        # remove leading code (separated by '_') and any extra '_'
                        new_file = '_'.join([f for f in file.split('_')[1:] if f != ''])
                        os.rename(f'{root}/{file}', f'{root}/{new_file}')

                for key in remove_keys:
                    if re.search(key, file) is not None:
                        os.remove(f'{root}/{file}')


# %% helper classes... self.map will be stored as a list of Slide objects
# quick class to keep track of slides
class SlideInfo:
    def __init__(self, cassette: str, number: int, position: int, directory: str):
        self.cassette = cassette
        self.number = number
        self.position = position
        self.directory = directory

    def data(self) -> tuple:
        return self.cassette, self.number, self.position, self.directory

    def __repr__(self):
        return f'cas:\t{self.cassette}\nnum:\t{self.number}\npos:\t{self.position}\ndir:\t{self.directory}'


# quick class to keep track of a reference distance for resizing (i.e. space between electrodes)
class Reference:
    def __init__(self, start: list[SlideInfo], end: list[SlideInfo]):
        # find average start and end positions  and save as instance variables for printing if needed
        self.start = np.mean([slide.position for slide in start])
        self.end = np.mean([slide.position for slide in end])
        # calculate reference distance
        self.abs_distance = abs(self.end - self.start)

    def scale_for_distance(self, distance: int) -> float:
        return distance / float(self.abs_distance)

    def __repr__(self):
        return f'\tstart pos:\t{self.start}\n\tend pos:\t{self.end}\n\tabs dist:\t{self.abs_distance}\n\n'
