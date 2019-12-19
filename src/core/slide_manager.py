#!/usr/bin/env python3.7

# builtins
import os
from typing import List

# packages
import cv2
import matplotlib.pyplot as plt
import numpy as np
import shutil

# access
from src.core import Slide, Map, Fascicle, Nerve, Trace
from .deformable import Deformable
from src.utils import *


class SlideManager(Exceptionable, Configurable, Saveable):
    """
    Required (Config.) JSON's:
        SAMPLE
        RUN
    """

    def __init__(self, exception_config: list):
        """
        :param master_config: preloaded configuration data for master
        :param exception_config: preloaded configuration data for exceptions
        :param map_mode: setup mode. If you want to build a new map from a directory, then NEW. Otherwise, or if for
        a single slide, OLD.
        """

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        # Initialize slides
        self.slides: List[Slide] = []

        # Set instance variable map
        self.map = None

    def init_map(self, map_mode: SetupMode) -> 'SlideManager':
        """
        Initialize the map. NOTE: the Config.SAMPLE json must have been externally added.
        :param map_mode: should be old for now, but keeping as parameter in case needed in future
        """
        if Config.SAMPLE.value not in self.configs.keys():
            self.throw(38)

        # Make a slide map
        self.map = Map(self.configs[Config.EXCEPTIONS.value])
        self.map.add(SetupMode.OLD, Config.SAMPLE, self.configs[Config.SAMPLE.value])
        self.map.init_post_config(map_mode)

        return self

    def scale(self, scale_bar_mask_path: str, scale_bar_length: float) -> 'SlideManager':
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

        return self

    def build_file_structure(self, printing: bool = False) -> 'SlideManager':
        """
        :param printing: bool, gives user console output
        """

        sample_index = self.search(Config.RUN, 'sample')

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # go to samples root
        samples_path: str = os.path.join('samples')

        # get sample NAME
        sample: str = self.search(Config.SAMPLE, 'sample')

        # loop through each slide
        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            scale_was_copied = False
            for directory_part in samples_path, str(sample_index), 'slides', cassette, number, 'masks':

                if not os.path.exists(directory_part):
                    os.makedirs(directory_part)
                os.chdir(directory_part)

                if (directory_part == str(sample_index)) and not scale_was_copied:
                    scale_source_file = os.path.join(start_directory,
                                                     *source_directory,
                                                     '_'.join([sample,
                                                               cassette,
                                                               number,
                                                               MaskFileNames.SCALE_BAR.value]))
                    if os.path.exists(scale_source_file):
                        shutil.copy2(scale_source_file, MaskFileNames.SCALE_BAR.value)
                    else:
                        raise Exception('{} not found'.format(scale_source_file))

                    scale_was_copied = True

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

            return self

    def populate(self, deform_animate: bool = False) -> 'SlideManager':

        # get parameters (modes) from configuration file
        mask_input_mode = self.search_mode(MaskInputMode, Config.SAMPLE)
        nerve_mode = self.search_mode(NerveMode, Config.SAMPLE)
        reshape_nerve_mode = self.search_mode(ReshapeNerveMode, Config.SAMPLE)
        deform_mode = self.search_mode(DeformationMode, Config.SAMPLE)

        def exists(mask_file_name: MaskFileNames):
            return os.path.exists(mask_file_name.value)

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get sample name
        sample: str = str(self.search(Config.RUN, 'sample'))

        # create scale bar path
        scale_path = os.path.join('samples', sample, MaskFileNames.SCALE_BAR.value)

        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, position, _ = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            os.chdir(os.path.join('samples', str(sample), 'slides', cassette, number, 'masks'))

            if not exists(MaskFileNames.RAW):
                self.throw(18)

            # init fascicles list
            fascicles: List[Fascicle] = []

            # load fascicles and check that the files exist
            if mask_input_mode == MaskInputMode.INNERS:
                if exists(MaskFileNames.INNERS):
                    fascicles = Fascicle.inner_to_list(MaskFileNames.INNERS.value,
                                                       self.configs[Config.EXCEPTIONS.value],
                                                       scale=1 + self.search(Config.SAMPLE,
                                                                             'scale',
                                                                             'outer_thick_to_inner_diam'))
                else:
                    self.throw(21)

            elif mask_input_mode == MaskInputMode.OUTERS:
                # fascicles = Fascicle.outer_to_list(MaskFileNames.OUTERS.value,
                #                                    self.configs[Config.EXCEPTIONS.value])
                self.throw(20)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_SEPARATE:
                if exists(MaskFileNames.INNERS) and exists(MaskFileNames.OUTERS):
                    fascicles = Fascicle.separate_to_list(MaskFileNames.INNERS.value,
                                                          MaskFileNames.OUTERS.value,
                                                          self.configs[Config.EXCEPTIONS.value])
                else:
                    self.throw(22)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_COMPILED:
                if exists(MaskFileNames.COMPILED):
                    fascicles = Fascicle.compiled_to_list(MaskFileNames.COMPILED.value,
                                                          self.configs[Config.EXCEPTIONS.value])
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
                                        self.configs[Config.EXCEPTIONS.value]))

            slide: Slide = Slide(fascicles,
                                 nerve,
                                 nerve_mode,
                                 self.configs[Config.EXCEPTIONS.value],
                                 will_reposition=(deform_mode != DeformationMode.NONE))

            # shrinkage correction
            slide.scale(1 + self.search(Config.SAMPLE, "scale", "shrinkage_scale"))

            # shift slide about (0,0)
            slide.move_center(np.array([0, 0]))

            self.slides.append(slide)

            os.chdir(start_directory)

        if os.path.exists(scale_path):
            self.scale(scale_path, self.search(Config.SAMPLE, 'scale', 'scale_bar_length'))
        else:
            print(scale_path)
            self.throw(19)

        # repositioning!
        for i, slide in enumerate(self.slides):
            print('\tslide {} of {}'.format(1 + i, len(self.slides)))
            title = ''

            if nerve_mode == NerveMode.NOT_PRESENT and deform_mode is not DeformationMode.NONE:
                self.throw(40)

            if deform_mode == DeformationMode.PHYSICS:
                print('\t\tsetting up physics')
                deformable = Deformable.from_slide(slide, ReshapeNerveMode.CIRCLE)
                morph_count = 36
                # title = 'morph count: {}'.format(morph_count)
                dist = self.search(Config.SAMPLE, "min_fascicle_separation")
                movements, rotations = deformable.deform(morph_count=morph_count,
                                                         render=deform_animate,
                                                         minimum_distance=dist)
                for move, angle, fascicle in zip(movements, rotations, slide.fascicles):
                    fascicle.shift(list(move) + [0])
                    fascicle.rotate(angle)
            elif deform_mode == DeformationMode.JITTER:
                slide.reposition_fascicles(slide.reshaped_nerve(reshape_nerve_mode), 10)
            else:  # must be DeformationMode.NONE
                import warnings
                warnings.warn('NO DEFORMATION is happening!')

            if nerve_mode is not NerveMode.NOT_PRESENT:
                slide.nerve = slide.reshaped_nerve(reshape_nerve_mode)
            # slide.plot(fix_aspect_ratio=True, title=title)

        return self

    def write(self, mode: WriteMode) -> 'SlideManager':
        """
        Write entire list of slides.
         """

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get path to sample slides
        sample_path = os.path.join(self.path(Config.SAMPLE, 'samples_path'),
                                   str(self.search(Config.RUN, 'sample')),
                                   'slides')

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
                if mode == WriteMode.SECTIONWISE2D:
                    directory_to_create = 'sectionwise2d'
                elif mode == WriteMode.SECTIONWISE:
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

        return self

    def make_electrode_input(self) -> 'SlideManager':

        # load template for electrode input
        electrode_input: dict = TemplateOutput.read(TemplateMode.ELECTRODE_INPUT)

        for cuff_inner_mode in CuffInnerMode:

            string_mode = str(cuff_inner_mode).split('.')[1]

            if cuff_inner_mode == CuffInnerMode.CIRCLE:

                (minx, miny, maxx, maxy) = self.slides[0].nerve.polygon().bounds
                electrode_input[string_mode]['r'] = max([(maxx - minx) / 2, (maxy - miny) / 2])

            elif cuff_inner_mode == CuffInnerMode.BOUNDING_BOX:

                (minx, miny, maxx, maxy) = self.slides[0].nerve.polygon().bounds
                electrode_input[string_mode]['x'] = maxx - minx
                electrode_input[string_mode]['y'] = maxy - miny

            else:
                pass

        # write template for electrode input
        TemplateOutput.write(electrode_input, TemplateMode.ELECTRODE_INPUT, self)

        return self

    def output_morphology_data(self) -> 'SlideManager':

        nerve_mode = self.search_mode(NerveMode, Config.SAMPLE)

        fascicles = [fascicle.morphology_data() for fascicle in self.slides[0].fascicles]

        if nerve_mode == NerveMode.PRESENT:
            nerve = Nerve.morphology_data(self.slides[0].nerve)
            morphology_input = {"Nerve": nerve, "Fascicles": fascicles}
        else:
            morphology_input = {"Nerve": None, "Fascicles": fascicles}

        self.configs[Config.SAMPLE.value]["Morphology"] = morphology_input

        sample_path = os.path.join(self.path(Config.SAMPLE, 'samples_path'),
                                   str(self.search(Config.RUN, 'sample')),
                                   'sample.json')

        TemplateOutput.write(self.configs[Config.SAMPLE.value], sample_path)

        return self
