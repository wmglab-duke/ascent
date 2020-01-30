from random import random
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from shapely.affinity import scale
from shapely.geometry import LineString, Point

from src.utils import *
from .sample import Sample


class FiberSet(Exceptionable, Configurable, Saveable):
    """
    Required (Config.) JSON's:
        MODEL
        SIM
    """

    def __init__(self, sample: Sample, exceptions_config: list):
        """
        :param exceptions_config: preloaded exceptions.json data
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # initialize empty lists of fiber points
        self.sample = sample
        self.fibers = None
        self.out_to_fib = None
        self.out_to_in = None
        self.add(SetupMode.NEW, Config.FIBER_Z, os.path.join('config', 'system', 'fiber_z.json'))

    def init_post_config(self):
        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(39)  # TODO NOT WRITTEN - INCORRECT INDEX
        return self

    def generate(self):
        """
        :return:
        """
        fibers_xy = self._generate_xy()
        self.out_to_fib, self.out_to_in = self._generate_maps(fibers_xy)
        self.fibers = self._generate_z(fibers_xy)
        return self

    def write(self, mode: WriteMode, path: str):
        """
        :param mode:
        :param path:
        :return:
        """
        for i, fiber in enumerate(self.fibers if self.fibers is not None else []):
            with open(os.path.join(path, str(i) + WriteMode.file_endings.value[mode.value]), 'w') as f:
                for row in [len(fiber)] + list(fiber):
                    if not isinstance(row, int):
                        for el in row:
                            f.write(str(el) + ' ')
                    else:
                        f.write(str(row) + ' ')
                    f.write("\n")
        return self

    def _generate_maps(self, fibers_xy) -> Tuple[List, List]:
        out_to_fib = []
        out_to_in = []

        inner_ind = 0
        for i, fascicle in enumerate(self.sample.slides[0].fascicles):
            out_to_in.append([])
            out_to_fib.append([])
            for j, inner in enumerate(fascicle.inners):
                out_to_in[i].append(inner_ind)
                out_to_fib[i].append([])
                inner_ind += 1
                for q, fiber in enumerate(fibers_xy):
                    if Point(fiber).within(inner.polygon()):
                        out_to_fib[i][j].append(q)

        return out_to_fib, out_to_in

    def _generate_xy(self) -> np.ndarray:
        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_mode_name: str = self.search(Config.SIM, 'fibers', 'xy_parameters', 'mode')
        xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
        xy_parameters: dict = self.search(Config.SIM, 'fibers', 'xy_parameters')

        # initialize result lists
        points: List[Tuple[float]] = []

        # small behavioral parameters
        buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')
        plot: bool = self.search(Config.SIM, 'fibers', 'plot')

        # perform implemented mode
        if self.search_mode(FiberZMode, Config.MODEL) == FiberZMode.EXTRUSION:

            if xy_mode == FiberXYMode.CENTROID:
                for fascicle in self.sample.slides[0].fascicles:
                    for inner in fascicle.inners:
                        for _ in (0,):
                            points.append(inner.centroid())

            elif xy_mode == FiberXYMode.UNIFORM_DENSITY:
                # DENSITY UNIT: axons / um^2

                # this determines whether the density should be determined top-down or bottom-up
                # case top_down == true: fetch target density and cap minimum axons if too low
                # case top_down == false: (i.e. bottom-up) find density from target number and smallest inner by area
                #   also cap the number at a maximum!
                top_down: bool = xy_parameters['top_down']

                if top_down:  # do top-down approach
                    # get required parameters
                    target_density = xy_parameters['target_density']
                    minimum_number = xy_parameters['minimum_number']

                    for fascicle in self.sample.slides[0].fascicles:
                        for inner in fascicle.inners:
                            fiber_count = target_density * inner.area()
                            if fiber_count < minimum_number:
                                fiber_count = minimum_number
                            for point in inner.random_points(fiber_count, buffer=buffer):
                                points.append(point)

                else:  # do bottom-up approach
                    # get required parameters
                    target_number = xy_parameters.get('target_number')
                    maximum_number = xy_parameters.get('maximum_number')

                    # calculate target density
                    min_area = np.amin([[fascicle.smallest_trace().area()
                                         for fascicle in self.sample.slides[0].fascicles]])
                    target_density = float(target_number) / min_area

                    for fascicle in self.sample.slides[0].fascicles:
                        for inner in fascicle.inners:
                            fiber_count = target_density * inner.area()
                            if fiber_count > maximum_number:
                                fiber_count = maximum_number
                            for point in inner.random_points(fiber_count, buffer=buffer):
                                points.append(point)

            elif xy_mode == FiberXYMode.UNIFORM_COUNT:
                count: int = xy_parameters['count']

                for fascicle in self.sample.slides[0].fascicles:
                    for inner in fascicle.inners:
                        for point in inner.random_points(count, buffer=buffer):
                            points.append(point)

            elif xy_mode == FiberXYMode.WHEEL:
                # get required parameters
                spoke_count: int = xy_parameters["spoke_count"]
                point_count: int = xy_parameters["point_count_per_spoke"]  # this number is PER SPOKE
                find_centroid: bool = xy_parameters["find_centroid"]
                angle_offset_is_in_degrees: bool = xy_parameters["angle_offset_is_in_degrees"]
                angle_offset: float = xy_parameters["angle_offset"]

                # convert angle offset to radians if necessary
                if angle_offset_is_in_degrees:
                    angle_offset *= 2 * np.pi / 360

                # master loop!
                for fascicle in self.sample.slides[0].fascicles:
                    for inner in fascicle.inners:
                        if find_centroid:
                            points.append(inner.centroid())

                        # loop through spoke angles
                        for spoke_angle in (np.linspace(0, 2 * np.pi, spoke_count + 1)[:-1] + angle_offset):
                            # find the mean radius for a reference distance when "casting the spoke ray"
                            new_inner = inner.deepcopy()
                            new_inner.offset(None, -buffer)

                            mean_radius = new_inner.mean_radius()

                            # get a point that is assumed to be outside the trace
                            raw_outer_point = np.array(new_inner.centroid()) + [5 * mean_radius * np.cos(spoke_angle),
                                                                                5 * mean_radius * np.sin(spoke_angle)]

                            # build a vector starting from the centroid of the trace
                            raw_spoke_vector = LineString([new_inner.centroid(),
                                                           tuple(raw_outer_point)])

                            # get that vector's intersection with the trace to find "trimmed" endpoint
                            intersection_with_boundary = raw_spoke_vector.intersection(new_inner.polygon().boundary)

                            # fix type of intersection with boundary
                            if not isinstance(intersection_with_boundary, Point):
                                intersection_with_boundary = list(intersection_with_boundary)[0]

                            # build trimmed vector
                            trimmed_spoke_vector = LineString([new_inner.centroid(),
                                                               tuple(intersection_with_boundary.coords)[0]])

                            # get scale vectors whose endpoints will be the desired points ([1:] to not include 0)
                            scaled_vectors: List[LineString] = [scale(trimmed_spoke_vector, *([factor] * 3),
                                                                      origin=trimmed_spoke_vector.coords[0])
                                                                for factor in np.linspace(0, 1, point_count + 2)[1:-1]]

                            # loop through the end points of the vectors
                            for point in [vector.coords[1] for vector in scaled_vectors]:
                                points.append(point)

            if plot:
                plt.figure()
                self.sample.slides[0].plot(final=False, fix_aspect_ratio=True)
                for point in points:
                    plt.plot(point[0], point[1], 'r*')
                plt.show()
        else:
            self.throw(30)

        return points

    def _generate_z(self, fibers_xy: np.ndarray) -> np.ndarray:

        fibers = []

        def clip(values: list, start, end, myel: bool, is_points: bool = False) -> list:

            step = 1
            if myel:
                step = 11

            while start - (values[0] if not is_points else values[0][-1]) > 0.1:
                values = values[step:]

            while (values[-1] if not is_points else values[-1][-1]) - end > 0.1:
                values = values[:-step]

            return values

        def build_fibers_with_offset(z_values: list, myel: bool, length: float, dz: float,
                                     additional_offset: float = 0):

            # init empty fiber (points) list
            fiber = []

            # get offset param - NOTE: raw value is a FRACTION of dz (explanation for multiplication by dz)
            offset = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'offset') * dz

            random_offset = False
            if offset is None:
                offset = 0.0
                random_offset = True
            z_offset = clip([z + offset + additional_offset for z in z_values], dz, length - dz, myel)
            for x, y in fibers_xy:
                random_offset_value = dz * (random.random() - 0.5) if random_offset else 0
                fiber.append([(x, y, z + random_offset_value) for z in z_offset])

            return fiber

        # %% START ALGORITHM

        # get top-level fiber z generation
        fiber_z_mode: FiberZMode = self.search_mode(FiberZMode, Config.MODEL)

        # all functionality is only defined for EXTRUSION as of now
        if fiber_z_mode == FiberZMode.EXTRUSION:

            # get the correct fiber lengths
            model_length = self.search(Config.MODEL, 'medium', 'bounds', 'length')
            fiber_length = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'length')
            half_fiber_length = fiber_length / 2
            z_shift_to_center = (model_length - fiber_length) / 2.0

            # SUPER IMPORTANT THAT THIS IS TRUE!
            assert model_length >= fiber_length

            fiber_geometry_mode_name: str = self.search(Config.SIM, 'fibers', 'mode')

            # use key from above to get myelination mode from fiber_z
            myelinated: bool = self.search(
                Config.FIBER_Z,
                MyelinationMode.parameters.value,
                fiber_geometry_mode_name,
                "myelinated"
            )

            diameter = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'diameter')

            if myelinated:  # MYELINATED

                delta_z = \
                    paranodal_length_2 = \
                    inter_length = None

                sampling_mode = self.search(Config.FIBER_Z,
                                            MyelinationMode.parameters.value,
                                            fiber_geometry_mode_name,
                                            "sampling")

                node_length, paranodal_length_1, inter_length_str = (
                    self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_geometry_mode_name, key)
                    for key in ('node_length', 'paranodal_length_1', 'inter_length')
                )

                # load in all the required specifications for finding myelinated z coordinates
                if sampling_mode == MyelinatedSamplingType.DISCRETE.value:

                    diameters, delta_zs, paranodal_length_2s = (
                        self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_geometry_mode_name, key)
                        for key in ('diameters', 'delta_zs', 'paranodal_length_2s')
                    )

                    diameter_index = diameters.index(diameter)
                    delta_z = delta_zs[diameter_index]
                    paranodal_length_2 = paranodal_length_2s[diameter_index]
                    inter_length = eval(inter_length_str)

                elif sampling_mode == MyelinatedSamplingType.INTERPOLATION.value:

                    paranodal_length_2_str, delta_z_str, inter_length_str = (
                        self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_geometry_mode_name, key)
                        for key in ('paranodal_length_2', 'delta_z', 'inter_length')
                    )
                    paranodal_length_2 = eval(paranodal_length_2_str)

                    if fiber_geometry_mode_name == FiberGeometry.B_FIBER.value:
                        inter_length = eval(inter_length_str)
                        delta_z = eval(delta_z_str)
                    elif fiber_geometry_mode_name == FiberGeometry.MRG_INTERPOLATION.value:
                        if diameter >= 5.26:
                            delta_z = eval(delta_z_str["diameter_greater_or_equal_5.26um"])
                        else:
                            delta_z = eval(delta_z_str["diameter_less_5.26um"])
                        inter_length = eval(inter_length_str)

                z_steps: List = []
                while (sum(z_steps) - half_fiber_length) < 0.001:
                    z_steps += [(node_length / 2) + (paranodal_length_1 / 2),
                                (paranodal_length_1 / 2) + (paranodal_length_2 / 2),
                                (paranodal_length_2 / 2) + (inter_length / 2),
                                *([inter_length] * 5),
                                (inter_length / 2) + (paranodal_length_2 / 2),
                                (paranodal_length_2 / 2) + (paranodal_length_1 / 2),
                                (paranodal_length_1 / 2) + (node_length / 2)]

                # account for difference between last node z and half fiber length -> must shift extra distance
                z_shift_to_center += abs(sum(z_steps) - half_fiber_length)

                reverse_z_steps = z_steps.copy()
                reverse_z_steps.reverse()

                # concat, cumsum, and other stuff to get final list of z points
                zs = np.array(
                    list(
                        np.cumsum(
                            np.concatenate(
                                ([0], reverse_z_steps, z_steps)
                            )
                        )
                    ),
                )

                fibers = [
                    clip(fiber, 0, model_length, myelinated, is_points=True)
                    for fiber in build_fibers_with_offset(zs, myelinated, fiber_length, delta_z, z_shift_to_center)
                ]

            else:  # UNMYELINATED

                delta_zs = self.search(Config.FIBER_Z,
                                       MyelinationMode.parameters.value,
                                       fiber_geometry_mode_name,
                                       'delta_zs')
                z_top_half = np.arange(fiber_length / 2, fiber_length + delta_zs, delta_zs)
                z_bottom_half = -np.flip(z_top_half) + fiber_length
                while z_top_half[-1] > fiber_length:
                    # trim top of top half
                    z_top_half = z_top_half[:-1]
                    z_bottom_half = z_bottom_half[1:]

                fibers = build_fibers_with_offset(list(np.concatenate((z_bottom_half[:-1], z_top_half))),
                                                  myelinated,
                                                  fiber_length,
                                                  delta_zs,
                                                  z_shift_to_center)

        else:
            self.throw(31)

        return fibers
