#!/usr/bin/env python3.7

# builtins
import os
from typing import List

# packages
import cv2
import matplotlib.pyplot as plt
import numpy as np
import shutil

# SPARCpy
from src.core import Slide, Map, Fascicle, Nerve, Trace
from .deformable import Deformable
from src.utils import *


class SlideManager(Exceptionable, Configurable, Saveable):

    def __init__(self, master_config: dict, exception_config: list, map_mode: SetupMode):
        """
        :param master_config: preloaded configuration data for master
        :param exception_config: preloaded configuration data for exceptions
        :param map_mode: setup mode. If you want to build a new map from a directory, then NEW. Otherwise, or if for
        a single slide, OLD.
        """

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)

        # Initialize slides
        self.slides: List[Slide] = []

        # Make a slide map
        self.map = Map(self.configs[ConfigKey.MASTER.value],
                       self.configs[ConfigKey.EXCEPTIONS.value],
                       map_mode)

    def scale(self, scale_bar_mask_path: str, scale_bar_length: float):
        """
        Scale all slides to the correct unit.
        :param scale_bar_mask_path: path to binary mask with white straight scale bar
        :param scale_bar_length: length (in global units as determined by config/user) of the scale bar
        """
        # load in image
        image_raw: np.ndarray = plt.imread(scale_bar_mask_path)
        # get maximum of each column (each "pixel" is a 4-item vector)
        row_of_column_maxes: np.ndarray = image_raw.max(0)
        # find the indices of columns in original image where the first pixel item was maxed (i.e. white)
        indices = np.where(row_of_column_maxes[:, 0] == max(row_of_column_maxes[:, 0]))[0]
        # find the length of the scale bar by finding total range of "max white" indices
        scale_bar_pixels = max(indices) - min(indices) + 1
        # calculate scale factor as unit/pixel
        factor = scale_bar_length / scale_bar_pixels
        # for each slide, scale to units
        for slide in self.slides:
            slide.scale(factor)

    def build_file_structure(self, printing: bool = False):
        """
        :param printing: bool, gives user console output
        """

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # go to samples root
        samples_path: str = self.path(ConfigKey.MASTER, 'samples_path')

        # get sample name
        sample: str = self.search(ConfigKey.MASTER, 'sample')

        # loop through each slide
        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            for directory_part in samples_path, sample, cassette, number, 'masks':

                if not os.path.exists(directory_part):
                    os.makedirs(directory_part)
                os.chdir(directory_part)

                if directory_part == sample:
                    scale_source_file = os.path.join(start_directory,
                                                     *source_directory,
                                                     '_'.join([sample,
                                                               cassette,
                                                               number,
                                                               MaskFileNames.SCALE_BAR.value]))
                    if os.path.exists(scale_source_file):
                        shutil.copy2(scale_source_file,  MaskFileNames.SCALE_BAR.value)
                    else:
                        raise Exception('{} not found'.format(scale_source_file))

            for target_file in [item.value for item in MaskFileNames if item != MaskFileNames.SCALE_BAR]:
                source_file = os.path.join(start_directory,
                                           *source_directory,
                                           '_'.join([sample, cassette, number, target_file]))
                if printing:
                    print('source: {}\ntarget: {}'.format(source_file, target_file))
                if os.path.exists(source_file):
                    if printing:
                        print('\tFOUND\n')
                    shutil.copy2(source_file, target_file)
                else:
                    if printing:
                        print('\tNOT FOUND\n')

            os.chdir(start_directory)

    def populate(self, deform_animate: bool = False):

        # get parameters (modes) from configuration file
        mask_input_mode = self.search_mode(MaskInputMode)
        nerve_mode = self.search_mode(NerveMode)
        reshape_nerve_mode = self.search_mode(ReshapeNerveMode)
        deform_mode = self.search_mode(DeformationMode)

        def exists(mask_file_name: MaskFileNames):
            return os.path.exists(mask_file_name.value)

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        samples_path = self.path(ConfigKey.MASTER, 'samples_path')

        # get sample name
        sample: str = self.search(ConfigKey.MASTER, 'sample')

        # create scale bar path
        scale_path = os.path.join(samples_path, sample, MaskFileNames.SCALE_BAR.value)

        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, position, _ = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            os.chdir(os.path.join(samples_path, sample, cassette, number, 'masks'))

            if not exists(MaskFileNames.RAW):
                self.throw(18)

            # init fascicles list
            fascicles: List[Fascicle] = []

            # load fascicles and check that the files exist
            if mask_input_mode == MaskInputMode.INNERS:
                if exists(MaskFileNames.INNERS):
                    fascicles = Fascicle.inner_to_list(MaskFileNames.INNERS.value,
                                                       self.configs[ConfigKey.EXCEPTIONS.value],
                                                       scale=1 + self.search(ConfigKey.MASTER,
                                                                             'scale',
                                                                             'outer_thick_to_inner_diam'))
                else:
                    self.throw(21)

            elif mask_input_mode == MaskInputMode.OUTERS:
                # fascicles = Fascicle.outer_to_list(MaskFileNames.OUTERS.value,
                #                                    self.configs[ConfigKey.EXCEPTIONS.value])
                self.throw(20)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_SEPARATE:
                if exists(MaskFileNames.INNERS) and exists(MaskFileNames.OUTERS):
                    fascicles = Fascicle.separate_to_list(MaskFileNames.INNERS.value,
                                                          MaskFileNames.OUTERS.value,
                                                          self.configs[ConfigKey.EXCEPTIONS.value])
                else:
                    self.throw(22)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_COMPILED:
                if exists(MaskFileNames.COMPILED):
                    fascicles = Fascicle.compiled_to_list(MaskFileNames.COMPILED.value,
                                                          self.configs[ConfigKey.EXCEPTIONS.value])
                else:
                    self.throw(23)

            else:  # exhaustive
                pass

            nerve = None

            if nerve_mode == NerveMode.PRESENT:
                # check and load in nerve, throw error if not present
                if exists(MaskFileNames.NERVE):
                    contour, _ = cv2.findContours(np.flipud(cv2.imread(MaskFileNames.NERVE.value, -1)),
                                                  cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
                    nerve = Nerve(Trace([point + [0] for point in contour[0][:, 0, :]],
                                        self.configs[ConfigKey.EXCEPTIONS.value]))

            else:  # nerve_mode == NerveMode.NOT_PRESENT:
                self.throw(24)

            slide: Slide = Slide(fascicles,
                                 nerve,
                                 self.configs[ConfigKey.EXCEPTIONS.value],
                                 will_reposition=(deform_mode != DeformationMode.NONE))

            # shrinkage correction
            slide.scale(1+self.search(ConfigKey.MASTER, "scale", "shrinkage_scale"))

            # shift slide about (0,0)
            slide.move_center(np.array([0, 0]))

            self.slides.append(slide)

            os.chdir(start_directory)

        if os.path.exists(scale_path):
            self.scale(scale_path, self.search(ConfigKey.MASTER, 'scale', 'scale_bar_length'))
        else:
            print(scale_path)
            self.throw(19)

        # repositioning!
        for i, slide in enumerate(self.slides):
            print('\tslide {} of {}'.format(1 + i, len(self.slides)))
            title = ''

            if deform_mode == DeformationMode.PHYSICS:
                print('\t\tsetting up physics')
                deformable = Deformable.from_slide(slide, ReshapeNerveMode.CIRCLE)
                morph_count = 36
                title = 'morph count: {}'.format(morph_count)
                movements, rotations = deformable.deform(morph_count=morph_count,
                                                         render=deform_animate,
                                                         minimum_distance=10.0)
                # TODO make the separation distance between fascicles and fascicles with nerve a
                #  parameter from configuration
                for move, angle, fascicle in zip(movements, rotations, slide.fascicles):
                    fascicle.shift(list(move) + [0])
                    fascicle.rotate(angle)
            elif deform_mode == DeformationMode.JITTER:
                slide.reposition_fascicles(slide.reshaped_nerve(reshape_nerve_mode), 5)
                # TODO isnt this value (5) supposed to be 10 to be consistent with physics?
            else:  # must be DeformationMode.NONE
                import warnings
                warnings.warn('NO DEFORMATION is happening!')

            slide.nerve = slide.reshaped_nerve(reshape_nerve_mode)
            slide.plot(fix_aspect_ratio=True, title=title)

    def write(self, mode: WriteMode):
        """
        Write entire list of slides.
        """

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get path to sample
        sample_path = os.path.join(self.path(ConfigKey.MASTER, 'samples_path'),
                                   self.search(ConfigKey.MASTER, 'sample'))

        # loop through the slide info (index i SHOULD correspond to slide in self.slides)
        # TODO: ensure self.slides matches up with self.map.slides
        for i, slide_info in enumerate(self.map.slides):
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            # build path to slide and ensure that it exists before proceeding
            slide_path = os.path.join(sample_path, cassette, number)
            if not os.path.exists(slide_path):
                self.throw(27)
            else:
                # change directories to slide path
                os.chdir(slide_path)

                # build the directory for output (name is the write mode)
                directory_to_create = ''
                if mode == WriteMode.SECTIONWISE:
                    directory_to_create = 'sectionwise'
                else:
                    self.throw(28)

                if not os.path.exists(directory_to_create):
                    os.makedirs(directory_to_create)
                os.chdir(directory_to_create)

                # WRITE
                self.slides[i].write(mode, os.getcwd())

            # go back up to start directory, then to top of loop
            os.chdir(start_directory)

    def make_electrode_input(self):

        # load template for electrode input
        electrode_input: dict = TemplateOutput.read(TemplateMode.ELECTRODE_INPUT)

        for cuff_inner_mode in CuffInnerMode:

            string_mode = str(cuff_inner_mode).split('.')[1]

            if cuff_inner_mode == CuffInnerMode.CIRCLE:

                (minx, miny, maxx, maxy) = self.slides[0].nerve.polygon().bounds
                electrode_input[string_mode]['r'] = max([(maxx - minx)/2, (maxy - miny)/2])

            elif cuff_inner_mode == CuffInnerMode.BOUNDING_BOX:

                (minx, miny, maxx, maxy) = self.slides[0].nerve.polygon().bounds
                electrode_input[string_mode]['x'] = maxx - minx
                electrode_input[string_mode]['y'] = maxy - miny

            else:
                pass

        # write template for electrode input
        TemplateOutput.write(electrode_input, TemplateMode.ELECTRODE_INPUT, self)

