#!/usr/bin/env python3.7

# builtins
import os
from typing import List, Tuple
import random

# packages
import cv2
import matplotlib.pyplot as plt
import numpy as np
import shutil
from shapely.affinity import scale
from shapely.geometry import LineString, Point

# SPARCpy
from src.core import Slide, Map, Fascicle, Nerve, Trace
from .deformable import Deformable
from src.utils import *


class Manager(Exceptionable, Configurable):

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
                for move, angle, fascicle in zip(movements, rotations, slide.fascicles):
                    fascicle.shift(list(move) + [0])
                    fascicle.rotate(angle)
            elif deform_mode == DeformationMode.JITTER:
                slide.reposition_fascicles(slide.reshaped_nerve(reshape_nerve_mode), 5)
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

    def fiber_xy_coordinates(self, plot: bool = False) -> Tuple[List[tuple], List[tuple]]:
        """
        :return: tuple containg two lists of tuples,
                    1) first list of tuples is points [(x, y)]
                    2) second list of tuples is metadata [(fascicle_index, inner_index, fiber_index)]
        """

        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_mode: FiberXYMode = self.search_mode(FiberXYMode)
        mode_name = str(xy_mode).split('.')[1]
        xy_parameters: dict = self.search(ConfigKey.MASTER, xy_mode.parameters.value, mode_name)

        # initialize result lists
        xy_coordinates: List[tuple] = []
        metadata: List[tuple] = []

        # perform implemented mode
        if self.search_mode(FiberZMode) == FiberZMode.EXTRUSION:

            if xy_mode == FiberXYMode.CENTROID:
                for fascicle_index, fascicle in enumerate(self.slides[0].fascicles):
                    for inner_index, inner in enumerate(fascicle.inners):

                        xy_coordinates.append(inner.centroid())
                        metadata.append((fascicle_index, inner_index, 0))  # 0 is axon index

            elif xy_mode == FiberXYMode.UNIFORM_DENSITY:

                # this determines whether the density should be determined top-down or bottom-up
                # case top_down == true: fetch target density and cap minimum axons if too low
                # case top_down == false: (i.e. bottom-up) find density from target number and smallest inner by area
                #   also cap the number at a maximum!
                top_down: bool = xy_parameters.get('top_down')

                if top_down:  # do top-down approach
                    # get required parameters
                    target_density = xy_parameters.get('target_density')
                    minimum_number = xy_parameters.get('minimum_number')

                    for fascicle_index, fascicle in enumerate(self.slides[0].fascicles):
                        for inner_index, inner in enumerate(fascicle.inners):
                            fiber_count = target_density * inner.area()
                            if fiber_count < minimum_number:
                                fiber_count = minimum_number

                            for fiber_index, point in enumerate(inner.random_points(fiber_count)):
                                xy_coordinates.append(point)
                                metadata.append((fascicle_index, inner_index, fiber_index))

                else:  # do bottom-up approach
                    # get required parameters
                    target_number = xy_parameters.get('target_number')
                    maximum_number = xy_parameters.get('maximum_number')

                    # calculate target density
                    min_area = np.amin([[fascicle.smallest_trace().area() for fascicle in self.slides[0].fascicles]])
                    target_density = float(target_number) / min_area

                    for fascicle_index, fascicle in enumerate(self.slides[0].fascicles):
                        for inner_index, inner in enumerate(fascicle.inners):
                            fiber_count = target_density * inner.area()
                            if fiber_count > maximum_number:
                                fiber_count = maximum_number

                            for fiber_index, point in enumerate(inner.random_points(fiber_count)):
                                xy_coordinates.append(point)
                                metadata.append((fascicle_index, inner_index, fiber_index))

            elif xy_mode == FiberXYMode.UNIFORM_COUNT:
                count: int = xy_parameters.get('count')

                for fascicle_index, fascicle in enumerate(self.slides[0].fascicles):
                    for inner_index, inner in enumerate(fascicle.inners):
                        for fiber_index, point in enumerate(inner.random_points(count)):
                            xy_coordinates.append(point)
                            metadata.append((fascicle_index, inner_index, fiber_index))

            elif xy_mode == FiberXYMode.WHEEL:
                # get required parameters
                spoke_count: int = xy_parameters.get("spoke_count")
                point_count: int = xy_parameters.get("point_count_per_spoke")  # this number is PER SPOKE
                find_centroid: bool = xy_parameters.get("find_centroid")
                angle_offset_is_in_degrees: bool = xy_parameters.get("angle_offset_is_in_degrees")
                angle_offset: float = xy_parameters.get("angle_offset")

                # convert angle offset to radians if necessary
                if angle_offset_is_in_degrees:
                    angle_offset *= 2 * np.pi / 360

                # master loop!
                for fascicle_index, fascicle in enumerate(self.slides[0].fascicles):
                    for inner_index, inner in enumerate(fascicle.inners):
                        # initialize last_fiber_index (to track indices between spokes)
                        start_fiber_index = 0
                        # loop through spoke angles
                        for spoke_angle in (np.linspace(0, 2 * np.pi, spoke_count + 1)[:-1] + angle_offset):
                            # find the mean radius for a reference distance when "casting the spoke ray"
                            mean_radius = inner.mean_radius()

                            # get a point that is assumed to be outside the trace
                            raw_outer_point = np.array(inner.centroid()) + [5 * mean_radius * np.cos(spoke_angle),
                                                                            5 * mean_radius * np.sin(spoke_angle)]

                            # build a vector starting from the centroid of the trace
                            raw_spoke_vector = LineString([inner.centroid(),
                                                           tuple(raw_outer_point)])

                            # get that vector's intersection with the trace to find "trimmed" endpoint
                            intersection_with_boundary = raw_spoke_vector.intersection(inner.polygon().boundary)

                            # fix type of intersection with boundary
                            if not isinstance(intersection_with_boundary, Point):
                                intersection_with_boundary = list(intersection_with_boundary)[0]

                            # build trimmed vector
                            trimmed_spoke_vector = LineString([inner.centroid(),
                                                              tuple(intersection_with_boundary.coords)[0]])

                            # get scale vectors whose endpoints will be the desired points ([1:] to not include 0)
                            scaled_vectors: List[LineString] = [scale(trimmed_spoke_vector, *([factor] * 3),
                                                                      origin=trimmed_spoke_vector.coords[0])
                                                                for factor in np.linspace(0, 1, point_count + 2)[1:-1]]

                            # loop through the end points of the vectors
                            for fiber_index, point in enumerate([vector.coords[1] for vector in scaled_vectors]):
                                xy_coordinates.append(point)
                                metadata.append((fascicle_index, inner_index, fiber_index))

                            # update start fiber index for next spoke
                            start_fiber_index = len(scaled_vectors) + start_fiber_index

            if plot:
                self.slides[0].plot()
                for point in xy_coordinates:
                    plt.plot(*point, 'r*')
        else:
            self.throw(30)

        return xy_coordinates, metadata

    def fiber_z_coordinates(self, xy_coordinates, metadata):
        """
        :param xy_coordinates:
        :param metadata:
        :return:
        """
        myelination_mode = self.search_mode(MyelinationMode)
        if  myelination_mode == MyelinationMode.MYELINATED:
            myelinated_fiber_type = self.search_mode(MyelinatedFiberType)
            fiber_length = self.search(ConfigKey.MASTER, 'geometry', 'z_nerve')

            

        else:  # must be unmyelinated
            unmyelinated_fiber_type = self.search_mode(UnmyelinatedFiberType)

            fiber_length = self.search(ConfigKey.MASTER, 'geometry', 'z_nerve')
            delta_z = self.search(ConfigKey.MASTER,
                                  MyelinationMode.parameters.value,
                                  str(myelination_mode).split('.')[-1],
                                  str(unmyelinated_fiber_type).split('.')[-1],
                                  'delta_z')

            z_top = np.arange(fiber_length / 2, fiber_length + delta_z, delta_z)




            # offset

            z_offset_mode: ZOffsetMode = self.search_mode(ZOffsetMode)
            z_offset_parameters: dict = self.search(ConfigKey.MASTER, xy_mode.parameters.value)

            if z_offset_mode == ZOffsetMode.UNIFORM:
                # get offset, assuming units are micrometers
                offset = z_offset_parameters.get('offset')
                # append offset to all the point tuples
                xy_coordinates = [(x, y, offset) for x, y in xy_coordinates]
            elif








