#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import csv
import os
import random
import shutil
import warnings
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from shapely.affinity import scale
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from src.utils import (
    Config,
    Configurable,
    DiamDistMode,
    Exceptionable,
    FiberGeometry,
    FiberXYMode,
    FiberZMode,
    MyelinatedSamplingType,
    MyelinationMode,
    Saveable,
    SetupMode,
    WriteMode,
)

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
        self.add(
            SetupMode.NEW,
            Config.FIBER_Z,
            os.path.join('config', 'system', 'fiber_z.json'),
        )

    def init_post_config(self):
        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(78)
        return self

    def generate(self, sim_directory: str, super_sample: bool = False):
        """
        :return:
        """

        fibers_xy = self._generate_xy(sim_directory)
        self.out_to_fib, self.out_to_in = self._generate_maps(fibers_xy)
        self.fibers = self._generate_z(fibers_xy, super_sample=super_sample)
        self.validate()
        self.plot_fibers_on_sample(sim_directory)

        return self

    def write(self, mode: WriteMode, path: str):
        """
        :param mode:
        :param path:
        :return:
        """

        diams = []
        for i, fiber_pre in enumerate(self.fibers if self.fibers is not None else []):

            if not isinstance(fiber_pre, dict):
                fiber = fiber_pre
            else:
                fiber = fiber_pre['fiber']
                diam = fiber_pre['diam']
                diams.append(diam)

            with open(
                os.path.join(path, str(i) + WriteMode.file_endings.value[mode.value]),
                'w',
            ) as f:
                for row in [len(fiber)] + list(fiber):
                    if not isinstance(row, int):
                        for el in row:
                            f.write(str(el) + ' ')
                    else:
                        f.write(str(row) + ' ')
                    f.write("\n")

        if len(diams) > 0:
            diams_key_path = os.path.join(path, 'diams.txt')
            with open(diams_key_path, "w") as f2:
                np.savetxt(f2, diams, fmt='%0.1f')

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

    def _generate_xy(self, sim_directory: str) -> np.ndarray:
        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_mode_name: str = self.search(Config.SIM, 'fibers', 'xy_parameters', 'mode')
        xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
        xy_parameters: dict = self.search(Config.SIM, 'fibers', 'xy_parameters')
        my_xy_seed: int = xy_parameters.get('seed', 0)

        # small behavioral parameters
        buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')

        # perform implemented mode
        if self.search_mode(FiberZMode, Config.MODEL) == FiberZMode.EXTRUSION:

            # error if an invalid mode is selected
            if xy_mode not in FiberXYMode:
                self.throw(151)

            if xy_mode == FiberXYMode.CENTROID:
                points = self.generate_centroid_points()

            elif xy_mode == FiberXYMode.UNIFORM_DENSITY:
                points = self.generate_uniform_density_points(buffer, my_xy_seed)

            elif xy_mode == FiberXYMode.UNIFORM_COUNT:
                points = self.generate_uniform_count_points(buffer, my_xy_seed)

            elif xy_mode == FiberXYMode.WHEEL:
                points = self.generate_wheel_points(buffer)

            elif xy_mode == FiberXYMode.EXPLICIT:
                points = self.load_explicit_coords(sim_directory)
        else:
            self.throw(30)

        return points

    def generate_centroid_points(self):
        points: List[Tuple[float]] = []
        for fascicle in self.sample.slides[0].fascicles:
            for inner in fascicle.inners:
                for _ in (0,):
                    points.append(inner.centroid())
        return points

    def generate_uniform_density_points(self, buffer, my_xy_seed):
        # DENSITY UNIT: axons / um^2
        # this determines whether the density should be determined top-down or bottom-up
        # case top_down is True: fetch target density and cap minimum axons if too low
        # case top_down is False: (i.e. bottom-up) find density from target number and smallest inner by area
        #   also cap the number at a maximum!
        points: List[Tuple[float]] = []
        top_down: bool = self.search(Config.SIM, 'fibers', 'xy_parameters', 'top_down')
        if top_down:  # do top-down approach
            # get required parameters
            target_density = self.search(Config.SIM, 'fibers', 'xy_parameters', 'target_density')
            minimum_number = self.search(Config.SIM, 'fibers', 'xy_parameters', 'minimum_number')

            for fascicle in self.sample.slides[0].fascicles:
                for inner in fascicle.inners:
                    fiber_count = target_density * inner.area()
                    if fiber_count < minimum_number:
                        fiber_count = minimum_number
                    for point in inner.random_points(fiber_count, buffer=buffer, my_xy_seed=my_xy_seed):
                        points.append(point)
                    my_xy_seed += 1

        else:  # do bottom-up approach
            # get required parameters
            target_number = self.search(Config.SIM, 'fibers', 'xy_parameters', 'target_number')
            maximum_number = self.search(Config.SIM, 'fibers', 'xy_parameters', 'maximum_number')

            # calculate target density
            min_area = np.amin([[fascicle.smallest_trace().area() for fascicle in self.sample.slides[0].fascicles]])
            target_density = float(target_number) / min_area

            for fascicle in self.sample.slides[0].fascicles:
                for inner in fascicle.inners:
                    fiber_count = target_density * inner.area()
                    if fiber_count > maximum_number:
                        fiber_count = maximum_number
                    for point in inner.random_points(fiber_count, buffer=buffer, my_xy_seed=my_xy_seed):
                        points.append(point)
                    my_xy_seed += 1
        return points

    def generate_uniform_count_points(self, buffer, my_xy_seed):
        points: List[Tuple[float]] = []
        count: int = self.search(Config.SIM, 'fibers', 'xy_parameters', 'count')
        for fascicle in self.sample.slides[0].fascicles:
            for inner in fascicle.inners:
                for point in inner.random_points(count, buffer=buffer, my_xy_seed=my_xy_seed):
                    points.append(point)
                my_xy_seed += 1
        return points

    def generate_wheel_points(self, buffer):
        points: List[Tuple[float]] = []
        # get required parameters
        spoke_count: int = self.search(Config.SIM, 'fibers', 'xy_parameters', 'spoke_count')
        point_count: int = self.search(
            Config.SIM, 'fibers', 'xy_parameters', 'point_count_per_spoke'
        )  # this number is PER SPOKE
        find_centroid: bool = self.search(Config.SIM, 'fibers', 'xy_parameters', 'find_centroid')
        angle_offset_is_in_degrees: bool = self.search(
            Config.SIM, 'fibers', 'xy_parameters', 'angle_offset_is_in_degrees'
        )
        angle_offset: float = self.search(Config.SIM, 'fibers', 'xy_parameters', 'angle_offset')
        # convert angle offset to radians if necessary
        if angle_offset_is_in_degrees:
            angle_offset *= 2 * np.pi / 360
        # master loop!
        for fascicle in self.sample.slides[0].fascicles:
            for inner in fascicle.inners:
                if find_centroid:
                    points.append(inner.centroid())

                # loop through spoke angles
                for spoke_angle in np.linspace(0, 2 * np.pi, spoke_count + 1)[:-1] + angle_offset:
                    # find the mean radius for a reference distance when "casting the spoke ray"
                    new_inner = inner.deepcopy()
                    new_inner.offset(None, -buffer)

                    mean_radius = new_inner.mean_radius()

                    # get a point that is assumed to be outside the trace
                    raw_outer_point = np.array(new_inner.centroid()) + [
                        5 * mean_radius * np.cos(spoke_angle),
                        5 * mean_radius * np.sin(spoke_angle),
                    ]

                    # build a vector starting from the centroid of the trace
                    raw_spoke_vector = LineString([new_inner.centroid(), tuple(raw_outer_point)])

                    # get that vector's intersection with the trace to find "trimmed" endpoint
                    intersection_with_boundary = raw_spoke_vector.intersection(new_inner.polygon().boundary)

                    # fix type of intersection with boundary
                    if not isinstance(intersection_with_boundary, Point):
                        intersection_with_boundary = list(intersection_with_boundary)[0]

                    # build trimmed vector
                    trimmed_spoke_vector = LineString(
                        [
                            new_inner.centroid(),
                            tuple(intersection_with_boundary.coords)[0],
                        ]
                    )

                    # get scale vectors whose endpoints will be the desired points ([1:] to not include 0)
                    scaled_vectors: List[LineString] = [
                        scale(trimmed_spoke_vector, *([factor] * 3), origin=trimmed_spoke_vector.coords[0])
                        for factor in np.linspace(0, 1, point_count + 2)[1:-1]
                    ]

                    # loop through the end points of the vectors
                    for point in [vector.coords[1] for vector in scaled_vectors]:
                        points.append(point)
        return points

    def load_explicit_coords(self, sim_directory):
        explicit_index = self.search(
            Config.SIM,
            'fibers',
            'xy_parameters',
            'explicit_fiberset_index',
            optional=True,
        )
        if explicit_index is not None:
            explicit_source = os.path.join(
                sim_directory.split(os.sep)[0],
                os.sep,
                *sim_directory.split(os.sep)[1:-4],
                'explicit_fibersets',
                f'{explicit_index}.txt',
            )
            explicit_dest = os.path.join(sim_directory, 'explicit.txt')
            shutil.copyfile(explicit_source, explicit_dest)
        else:
            print(
                '\t\tWARNING: Explicit fiberset index not specified.'
                '\n\t\tProceeding with backwards compatible check for explicit.txt in:'
                f'\n\t\t{sim_directory}'
            )
        if not os.path.exists(os.path.join(sim_directory, 'explicit.txt')):
            self.throw(83)
        with open(os.path.join(sim_directory, 'explicit.txt')) as f:
            # advance header
            next(f)
            reader = csv.reader(f, delimiter=" ")
            points = [tuple(float(row[0]), float(row[1])) for row in reader]
        # check that all fibers are within exactly one inner
        for fiber in points:
            if not any(
                [
                    Point(fiber).within(inner.polygon())
                    for fascicle in self.sample.slides[0].fascicles
                    for inner in fascicle.inners
                ]
            ):
                print(f"Explicit fiber coordinate: {fiber} does not fall in an inner")
                self.throw(71)
        return points

    def plot_fibers_on_sample(self, sim_directory):
        fig = plt.figure()
        self.sample.slides[0].plot(
            final=False,
            fix_aspect_ratio='True',
            axlabel=u"\u03bcm",
            title='Fiber locations for nerve model',
        )
        self.plot()
        plt.savefig(sim_directory + '/plots/fibers_xy.png', dpi=300)
        if self.search(Config.RUN, 'popup_plots', optional=True) is False:
            fig.clear
            plt.close(fig)
        else:
            plt.show()

    def plot(
        self,
        ax: plt.Axes = None,
        scatter_kws: dict = None,
    ):
        if ax is None:
            ax = plt.gca()
        if scatter_kws is None:
            scatter_kws = {}
        scatter_kws.setdefault('c', 'red')
        scatter_kws.setdefault('s', 20)
        scatter_kws.setdefault('marker', 'o')
        x, y = self.xy_points(split_xy=True)
        ax.scatter(
            x,
            y,
            **scatter_kws,
        )

    def _generate_z(self, fibers_xy: np.ndarray, override_length=None, super_sample: bool = False) -> np.ndarray:
        def clip(values: list, start, end, myel: bool, is_points: bool = False) -> list:

            step = 1
            if myel:
                step = 11

            while 1:
                if (start + 0.1) > (values[0] if not is_points else values[0][-1]):
                    values = values[step:]
                elif (end - 0.1) < (values[-1] if not is_points else values[-1][-1]):
                    values = values[:-step]
                else:
                    break

            return values

        def generate_myel_fiber_zs(diameter):
            def _build_z(inter_length, node_length, paranodal_length_1, paranodal_length_2, delta_z):
                z_steps: List = []
                while (sum(z_steps) - model_length / 2) < 1:
                    z_steps += [
                        (node_length / 2) + (paranodal_length_1 / 2),
                        (paranodal_length_1 / 2) + (paranodal_length_2 / 2),
                        (paranodal_length_2 / 2) + (inter_length / 2),
                        *([inter_length] * 5),
                        (inter_length / 2) + (paranodal_length_2 / 2),
                        (paranodal_length_2 / 2) + (paranodal_length_1 / 2),
                        (paranodal_length_1 / 2) + (node_length / 2),
                    ]
                # account for difference between last node z and half fiber length -> must shift extra distance
                if shift is None:
                    modshift = 0
                else:
                    modshift = shift % delta_z
                my_z_shift_to_center_in_fiber_range = model_length / 2 - sum(z_steps) + modshift
                reverse_z_steps = z_steps.copy()
                reverse_z_steps.reverse()
                # concat, cumsum, and other stuff to get final list of z points
                my_zs = np.array(list(np.cumsum(np.concatenate(([0], reverse_z_steps, z_steps)))))
                return my_z_shift_to_center_in_fiber_range, my_zs

            delta_z = paranodal_length_2 = inter_length = None

            sampling_mode = self.search(
                Config.FIBER_Z,
                MyelinationMode.parameters.value,
                fiber_geometry_mode_name,
                'sampling',
            )

            node_length, paranodal_length_1, inter_length_str = (
                self.search(
                    Config.FIBER_Z,
                    MyelinationMode.parameters.value,
                    fiber_geometry_mode_name,
                    key,
                )
                for key in ('node_length', 'paranodal_length_1', 'inter_length')
            )

            # load in all the required specifications for finding myelinated z coordinates
            if sampling_mode == MyelinatedSamplingType.DISCRETE.value:

                diameters, my_delta_zs, paranodal_length_2s = (
                    self.search(
                        Config.FIBER_Z,
                        MyelinationMode.parameters.value,
                        fiber_geometry_mode_name,
                        key,
                    )
                    for key in ('diameters', 'delta_zs', 'paranodal_length_2s')
                )

                diameter_index = diameters.index(diameter)
                delta_z = my_delta_zs[diameter_index]
                paranodal_length_2 = paranodal_length_2s[diameter_index]
                inter_length = eval(inter_length_str)

            elif sampling_mode == MyelinatedSamplingType.INTERPOLATION.value:

                paranodal_length_2_str, delta_z_str, inter_length_str = (
                    self.search(
                        Config.FIBER_Z,
                        MyelinationMode.parameters.value,
                        fiber_geometry_mode_name,
                        key,
                    )
                    for key in ('paranodal_length_2', 'delta_z', 'inter_length')
                )
                paranodal_length_2 = eval(paranodal_length_2_str)

                if fiber_geometry_mode_name == FiberGeometry.B_FIBER.value:
                    inter_length = eval(inter_length_str)
                    delta_z = eval(delta_z_str)
                elif fiber_geometry_mode_name == FiberGeometry.MRG_INTERPOLATION.value:
                    if diameter > 16.0 or diameter < 2.0:
                        self.throw(77)
                    if diameter >= 5.643:
                        delta_z = eval(delta_z_str["diameter_greater_or_equal_5.643um"])
                    else:
                        delta_z = eval(delta_z_str["diameter_less_5.643um"])
                    inter_length = eval(inter_length_str)

            my_z_shift_to_center_in_fiber_range, my_zs = _build_z(
                inter_length, node_length, paranodal_length_1, paranodal_length_2, delta_z
            )

            return my_zs, delta_z, my_z_shift_to_center_in_fiber_range

        def build_fiber_with_offset(
            z_values: list,
            myel: bool,
            dz: float,
            my_x: float,
            my_y: float,
            additional_offset: float = 0,
        ):

            random_offset_value = 0
            # get offset param - NOTE: raw value is a FRACTION of dz (explanation for multiplication by dz)

            offset = self.search(
                Config.SIM,
                'fibers',
                FiberZMode.parameters.value,
                'offset',
                optional=True,
            )
            if offset is None:
                warnings.warn(
                    'No offset specified. Proceeding with (original default functionality) of randomized offset. '
                    'Suppress this warning by including the parameter "offset":"random" in fiber z_parameters.'
                )
                offset = 'random'
            if offset == 'random':
                offset = 0
                random_offset_value = dz * (random.random() - 0.5)
            else:
                if 0 <= offset <= 1:
                    offset = offset * dz
                else:
                    self.throw(99)

            # compute offset z coordinate
            z_offset = [my_z + offset + random_offset_value + additional_offset for my_z in z_values]

            z_offset = clip(
                z_offset,
                self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'min'),
                self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'max'),
                myel,
            )

            my_fiber = [(my_x, my_y, z) for z in z_offset]

            return my_fiber

        def generate_z_unmyel(mydiams):
            fibers = []
            if super_sample:
                if 'dz' in self.configs[Config.SIM.value]['supersampled_bases']:
                    delta_z = self.search(Config.SIM, 'supersampled_bases', 'dz')
                else:
                    self.throw(79)

            else:
                delta_z = self.search(
                    Config.FIBER_Z,
                    MyelinationMode.parameters.value,
                    fiber_geometry_mode_name,
                    'delta_zs',
                )

            z_top_half = np.arange(model_length / 2, model_length + delta_z, delta_z)
            z_bottom_half = -np.flip(z_top_half) + model_length
            while z_top_half[-1] > model_length:
                # trim top of top half
                z_top_half = z_top_half[:-1]
                z_bottom_half = z_bottom_half[1:]

            if len(mydiams) == 0:
                diams = [
                    self.search(
                        Config.SIM,
                        'fibers',
                        FiberZMode.parameters.value,
                        'diameter',
                    )
                ] * len(fibers_xy)

            for (x, y), diam in zip(fibers_xy, diams):
                fiber_pre = build_fiber_with_offset(
                    list(np.concatenate((z_bottom_half[:-1], z_top_half))),
                    myelinated,
                    delta_z,
                    x,
                    y,
                )
                if np.amax(np.array(fiber_pre)[:, 2]) - np.amin(np.array(fiber_pre)[:, 2]) > fiber_length:
                    self.throw(119)
                if diam_distribution:
                    fiber = {'diam': diam, 'fiber': fiber_pre}
                else:
                    fiber = fiber_pre
                fibers.append(fiber)
            return fibers

        def generate_z_myelinated(mydiams):
            fibers = []
            random.seed(my_z_seed)
            if len(mydiams) == 0:
                mydiams = [diameter] * len(fibers_xy)
            for (x, y), diam in zip(fibers_xy, mydiams):
                (
                    zs,
                    delta_z,
                    z_shift_to_center_in_fiber_range,
                ) = generate_myel_fiber_zs(diam)

                fiber_pre = build_fiber_with_offset(zs, myelinated, delta_z, x, y, z_shift_to_center_in_fiber_range)
                if np.amax(np.array(fiber_pre)[:, 2]) - np.amin(np.array(fiber_pre)[:, 2]) > fiber_length:
                    self.throw(119)
                if diam_distribution:
                    fiber = {'diam': diam, 'fiber': fiber_pre}
                else:
                    fiber = fiber_pre
                fibers.append(fiber)
            return fibers

        # get top-level fiber z generation
        fiber_z_mode: FiberZMode = self.search_mode(FiberZMode, Config.MODEL)

        # all functionality is only defined for EXTRUSION as of now
        if fiber_z_mode == FiberZMode.EXTRUSION:

            fiber_length, model_length = self.calculate_fiber_length_params(override_length)
            shift = self.search(
                Config.SIM,
                'fibers',
                FiberZMode.parameters.value,
                'absolute_offset',
                optional=True,
            )

            fiber_geometry_mode_name: str = self.search(Config.SIM, 'fibers', 'mode')

            # use key from above to get myelination mode from fiber_z
            diams = []
            diameter = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'diameter')
            diam_distribution: bool = type(diameter) is dict

            diams, myelinated = self.calculate_fiber_diams(
                diam_distribution, diams, fiber_geometry_mode_name, fibers_xy, super_sample
            )

            my_z_seed = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'seed')

            if myelinated and not super_sample:  # MYELINATED
                fibers = generate_z_myelinated(diams)

            else:  # UNMYELINATED
                fibers = generate_z_unmyel(diams)

        else:
            self.throw(31)

        return fibers

    def calculate_fiber_diams(self, diam_distribution, diams, fiber_geometry_mode_name, fibers_xy, super_sample):
        if super_sample:
            myelinated = False
        else:
            myelinated: bool = self.search(
                Config.FIBER_Z,
                MyelinationMode.parameters.value,
                fiber_geometry_mode_name,
                'myelinated',
            )

            if diam_distribution:
                sampling_mode = self.search(
                    Config.FIBER_Z,
                    MyelinationMode.parameters.value,
                    fiber_geometry_mode_name,
                    'sampling',
                )
                if myelinated and (sampling_mode != MyelinatedSamplingType.INTERPOLATION.value):
                    self.throw(104)

                distribution_mode_name = self.search(
                    Config.SIM,
                    'fibers',
                    FiberZMode.parameters.value,
                    'diameter',
                    'mode',
                )
                distribution_mode: DiamDistMode = [
                    mode for mode in DiamDistMode if str(mode).split('.')[-1] == distribution_mode_name
                ][0]
                # seed rng
                my_diam_seed: int = self.search(
                    Config.SIM,
                    'fibers',
                    FiberZMode.parameters.value,
                    'diameter',
                    'seed',
                )
                np.random.seed(my_diam_seed)

                fiber_diam_dist = None
                if distribution_mode == DiamDistMode.UNIFORM:

                    # load parameters
                    lower_fiber_diam: float = self.search(
                        Config.SIM,
                        'fibers',
                        FiberZMode.parameters.value,
                        'diameter',
                        'lower',
                    )
                    upper_fiber_diam: float = self.search(
                        Config.SIM,
                        'fibers',
                        FiberZMode.parameters.value,
                        'diameter',
                        'upper',
                    )

                    # parameter checking
                    # positive values, order makes sense, etc
                    if lower_fiber_diam < 0:
                        self.throw(100)
                    if lower_fiber_diam > upper_fiber_diam:
                        self.throw(101)

                    fiber_diam_dist = stats.uniform(lower_fiber_diam, upper_fiber_diam - lower_fiber_diam)

                elif distribution_mode == DiamDistMode.TRUNCNORM:

                    # load parameters
                    n_std_fiber_diam_limit: float = self.search(
                        Config.SIM,
                        'fibers',
                        FiberZMode.parameters.value,
                        'diameter',
                        'n_std_limit',
                    )
                    mu_fiber_diam: float = self.search(
                        Config.SIM,
                        'fibers',
                        FiberZMode.parameters.value,
                        'diameter',
                        'mu',
                    )
                    std_fiber_diam: float = self.search(
                        Config.SIM,
                        'fibers',
                        FiberZMode.parameters.value,
                        'diameter',
                        'std',
                    )
                    lower_fiber_diam = mu_fiber_diam - n_std_fiber_diam_limit * std_fiber_diam
                    upper_fiber_diam = mu_fiber_diam + n_std_fiber_diam_limit * std_fiber_diam

                    # parameter checking
                    # positive values, order makes sense, etc
                    if n_std_fiber_diam_limit == 0 and std_fiber_diam != 0:
                        self.throw(102)
                    if lower_fiber_diam < 0:
                        self.throw(103)

                    fiber_diam_dist = stats.truncnorm(
                        (lower_fiber_diam - mu_fiber_diam) / std_fiber_diam,
                        (upper_fiber_diam - mu_fiber_diam) / std_fiber_diam,
                        loc=mu_fiber_diam,
                        scale=std_fiber_diam,
                    )

                diams = fiber_diam_dist.rvs(len(fibers_xy))
        return diams, myelinated

    def calculate_fiber_length_params(self, override_length):
        model_length = (
            self.search(Config.MODEL, 'medium', 'proximal', 'length') if (override_length is None) else override_length
        )
        if (
            'min' not in self.configs['sims']['fibers']['z_parameters'].keys()
            or 'max' not in self.configs['sims']['fibers']['z_parameters'].keys()
            or override_length is not None
        ):
            fiber_length = model_length if override_length is None else override_length
            self.configs['sims']['fibers'][FiberZMode.parameters.value]['min'] = 0
            self.configs['sims']['fibers'][FiberZMode.parameters.value]['max'] = fiber_length

            if (
                override_length is None
                and self.configs['sims']['fibers']['z_parameters'].get('full_nerve_length') is not True
            ):
                warnings.warn(
                    'Program assumed fiber length same as proximal length since "min" and "max" fiber '
                    'length not defined in Config.Sim "fibers" -> "z_parameters". '
                    'Suppress this warning by adding "full_nerve_length = true" to your z_parameters.'
                )
            self.configs['sims']['fibers'][FiberZMode.parameters.value]['full_nerve_length'] = False

        else:
            if self.configs['sims']['fibers']['z_parameters'].get('full_nerve_length') is True:
                self.throw(127)

            min_fiber_z_limit = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'min')
            max_fiber_z_limit = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'max')

            if not max_fiber_z_limit > min_fiber_z_limit:
                self.throw(105)

            fiber_length = (max_fiber_z_limit - min_fiber_z_limit) if override_length is None else override_length
        if (
            self.search(
                Config.SIM,
                'fibers',
                FiberZMode.parameters.value,
                'longitudinally_centered',
                optional=True,
            )
            is False
        ):
            print(
                'WARNING: the sim>fibers>z_parameters>longitudinally_centered parameter is deprecated.\
                  \nFibers will be centered to the model.'
            )
        assert model_length >= fiber_length, f'proximal length: ({model_length}) < fiber length: ({fiber_length})'
        return fiber_length, model_length

    def validate(self):
        """Check to ensure fiberset is valid"""
        # check that all fibers are inside inners, accounting for trace buffer
        buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')
        all_inners = [inner.deepcopy() for fascicle in self.sample.slides[0].fascicles for inner in fascicle.inners]
        [inner.offset(distance=-buffer) for inner in all_inners]
        allpoly = unary_union([inner.polygon() for inner in all_inners])
        if not np.all([Point(fiber).within(allpoly) for fiber in self.fibers]):
            self.throw(147)
        # add other checks below

    def xy_points(self, split_xy=False):
        points = [(f[0][0], f[0][1]) for f in self.fibers]
        if split_xy:
            return list(zip(*points))[0], list(zip(*points))[1]
        else:
            return points
