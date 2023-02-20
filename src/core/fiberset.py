#!/usr/bin/env python3.7

"""Defines FiberSet class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
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
    FiberGeometry,
    FiberXYMode,
    FiberZMode,
    IncompatibleParametersError,
    MorphologyError,
    MyelinatedSamplingType,
    MyelinationMode,
    Saveable,
    SetupMode,
    WriteMode,
)

from .sample import Sample


class FiberSet(Configurable, Saveable):
    """Class methods for generating fiber coordinates to use in NEURON simulations."""

    def __init__(self, sample: Sample):
        """Initialize the FiberSet class.

        :param sample: The sample to be used for the nerve model.
        """
        # set up superclasses
        Configurable.__init__(self)

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
        """Make sure Model and Simulation are configured.

        :raises KeyError: If Model or Simulation are not configured.
        :return: self
        """
        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            raise KeyError("Missing Model or Simulation configuration.")
        return self

    def generate(self, sim_directory: str, super_sample: bool = False):
        """Create xy coordinates for the fibers, map them to the fascicles, create z coordinates, and validate them.

        :param sim_directory: The directory to save the simulation files to.
        :param super_sample: Whether to generate a super sample.
        :return: self
        """
        fibers_xy = self._generate_xy(sim_directory)
        self.out_to_fib, self.out_to_in = self._generate_maps(fibers_xy)
        self.fibers = self._generate_z(fibers_xy, super_sample=super_sample)
        self.validate()
        self.plot_fibers_on_sample(fibers_xy, sim_directory)

        return self

    def write(self, mode: WriteMode, path: str):
        """Write the fiberset to file.

        :param mode: Type of file to write to.
        :param path: Path to the file to write to.
        :raises ValueError: If some fibers have diameter attribute and others do not.
        :return: self
        """
        diams = []
        offset_ratios = []
        for i, fiber in enumerate(self.fibers if self.fibers is not None else []):
            diams.append(fiber['diam'])
            z_coords = fiber['fiber']
            offset_ratios.append(fiber['offset_ratio'])
            os.makedirs(path, exist_ok=True)

            with open(
                os.path.join(path, str(i) + WriteMode.file_endings.value[mode.value]),
                'w',
            ) as f:
                for row in [len(z_coords)] + list(z_coords):
                    if not isinstance(row, int):
                        for el in row:
                            f.write(str(el) + ' ')
                    else:
                        f.write(str(row) + ' ')
                    f.write("\n")

        if diams.count(None) == 0:
            diams_key_path = os.path.join(path, 'diams.txt')
            with open(diams_key_path, "w") as f2:
                np.savetxt(f2, diams, fmt='%0.1f')
        elif diams.count(None) == len(diams):
            pass
        else:
            raise ValueError('Some fibers have diameters and some do not.')

        if offset_ratios.count(None) == 0:
            offset_ratios_key_path = os.path.join(path, 'offsets.txt')
            with open(offset_ratios_key_path, "w") as f3:
                np.savetxt(f3, offset_ratios, fmt='%0.2f')
        elif offset_ratios.count(None) == len(offset_ratios):
            pass
        else:
            raise ValueError('Some fibers have offsets and some do not.')

        return self

    def _generate_maps(self, fibers_xy) -> Tuple[List, List]:
        """Generate the out-to-fascicle and out-to-inner maps.

        :param fibers_xy: xy coordinates of the fibers
        :return: mapping from fiber index to outer index and from outer index to inner index
        """
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
        """Generate the xy coordinates of the fibers.

        :param sim_directory: The directory of the simulation.
        :raises NotImplementedError: If a mode is not supported.
        :return: xy coordinates of the fibers
        """
        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_mode_name: str = self.search(Config.SIM, 'fibers', 'xy_parameters', 'mode')
        self.xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
        xy_parameters: dict = self.search(Config.SIM, 'fibers', 'xy_parameters')
        my_xy_seed: int = xy_parameters.get('seed', 0)

        # small behavioral parameters
        buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')

        # perform implemented mode
        if self.search_mode(FiberZMode, Config.MODEL) == FiberZMode.EXTRUSION:
            # error if an invalid mode is selected
            if self.xy_mode not in FiberXYMode:
                raise NotImplementedError("Invalid FiberXYMode in Sim.")

            if self.xy_mode == FiberXYMode.CENTROID:
                points = self.generate_centroid_points()

            elif self.xy_mode == FiberXYMode.UNIFORM_DENSITY:
                points = self.generate_uniform_density_points(buffer, my_xy_seed)

            elif self.xy_mode == FiberXYMode.UNIFORM_COUNT:
                points = self.generate_uniform_count_points(buffer, my_xy_seed)

            elif self.xy_mode == FiberXYMode.WHEEL:
                points = self.generate_wheel_points(buffer)

            elif self.xy_mode == FiberXYMode.EXPLICIT:
                points = self.load_explicit_coords(sim_directory)
        else:
            raise NotImplementedError("That FiberZMode is not yet implemented.")

        return points

    def generate_centroid_points(self):
        """Create the xy coordinates of the fibers using the centroid of the fascicles.

        :return: xy coordinates of the fibers
        """
        points: List[Tuple[float]] = []
        for fascicle in self.sample.slides[0].fascicles:
            for inner in fascicle.inners:
                for _ in (0,):
                    points.append(inner.centroid())
        return points

    def generate_uniform_density_points(self, buffer, my_xy_seed):
        """Create the xy coordinates of the fibers using a uniform density.

        :param buffer: Buffer required between the fibers and the fascicles.
        :param my_xy_seed: Seed for the random number generator.
        :return: The xy coordinates of the fibers.
        """
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
        """Create the xy coordinates of the fibers using a uniform count.

        :param buffer: Buffer required between the fibers and the fascicles.
        :param my_xy_seed: Seed for the random number generator.
        :return: The xy coordinates of the fibers.
        """
        points: List[Tuple[float]] = []
        count: int = self.search(Config.SIM, 'fibers', 'xy_parameters', 'count')
        for fascicle in self.sample.slides[0].fascicles:
            for inner in fascicle.inners:
                for point in inner.random_points(count, buffer=buffer, my_xy_seed=my_xy_seed):
                    points.append(point)
                my_xy_seed += 1
        return points

    def generate_wheel_points(self, buffer):
        """Create the xy coordinates of the fibers using a wheel.

        :param buffer: Buffer required between the fibers and the fascicles.
        :return: The xy coordinates of the fibers.
        """
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
        """Load the xy coordinates of the fibers from an explicit file.

        :param sim_directory: The directory of the simulation.
        :raises FileNotFoundError: If the coordinates file is not found.
        :raises MorphologyError: If any of the coordinates fall outside of the fascicles.
        :return: The xy coordinates of the fibers.
        """
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
            raise FileNotFoundError(
                "FiberXYMode is EXPLICIT in Sim but no explicit.txt file with coordinates is in the Sim directory. "
                "See config/system/templates/explicit.txt for example of this file's required format."
            )
        with open(os.path.join(sim_directory, 'explicit.txt')) as f:
            # advance header
            next(f)
            reader = csv.reader(f, delimiter=" ")
            points = [(float(row[0]), float(row[1])) for row in reader]
        # check that all fibers are within exactly one inner
        for fiber in points:
            if not any(
                [
                    Point(fiber).within(inner.polygon())
                    for fascicle in self.sample.slides[0].fascicles
                    for inner in fascicle.inners
                ]
            ):
                raise MorphologyError(f"Explicit fiber coordinate: {fiber} does not fall in an inner")
        return points

    def plot_fibers_on_sample(self, points, sim_directory):
        """Plot the xy coordinates of the fibers on the sample.

        :param points: The xy coordinates of the fibers.
        :param sim_directory: The directory of the simulation.
        """
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
            plt.close(fig)
        else:
            plt.show()

    def plot(
        self,
        ax: plt.Axes = None,
        scatter_kws: dict = None,
    ):
        """Plot the xy coordinates of the fibers.

        :param ax: The axis to plot on. If None, use the current axis.
        :param scatter_kws: The matplotlib keyword arguments for the scatter plot.
        """
        if ax is None:
            ax = plt.gca()
        if scatter_kws is None:
            scatter_kws = {}
        scatter_kws.setdefault('c', 'red')
        scatter_kws.setdefault('s', 10)
        scatter_kws.setdefault('marker', 'o')
        x, y = self.xy_points(split_xy=True)
        ax.scatter(
            x,
            y,
            **scatter_kws,
        )

    def _generate_z(  # noqa: C901
        self, fibers_xy: np.ndarray, override_length=None, super_sample: bool = False
    ) -> np.ndarray:
        """Generate the z coordinates of the fibers.

        :param fibers_xy: The xy coordinates of the fibers.
        :param override_length: The length of the fibers (forced).
        :param super_sample: Whether to use supersampling.
        :raises NotImplementedError: If the z mode is not supported.
        :return: The z coordinates of the fibers.
        """
        # get top-level fiber z generation
        fiber_z_mode: FiberZMode = self.search_mode(FiberZMode, Config.MODEL)
        # all functionality is only defined for EXTRUSION as of now
        if fiber_z_mode != FiberZMode.EXTRUSION:
            raise NotImplementedError(f"{fiber_z_mode} FiberZMode is not yet implemented.")

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
            """Generate the z coordinates of the fibers for a myelinated nerve.

            :param diameter: The diameter of the myelinated nerve.
            :raises ValueError: If diameter is not within the valid range
            :return: The z coordinates of the fibers.
            """

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
                        raise ValueError(
                            "Diameter entered for MRG_INTERPOLATION must be between 2.0 and 16.0 (inclusive)."
                        )
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
            """Build a fiber with an offset.

            :param z_values: The z values of the fiber.
            :param myel: Whether the fiber is myelinated.
            :param dz: The delta z of the fiber.
            :param my_x: The x coordinate of the fiber.
            :param my_y: The y coordinate of the fiber.
            :param additional_offset: The additional offset of the fiber.
            :raises ValueError: If offset is not within the valid range
            :return: The fiber.
            """
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
                    'Suppress this warning by including the parameter "offset":"random" in fiber z_parameters.',
                    stacklevel=2,
                )
                offset = 'random'
            if offset == 'random':
                offset = 0
                random_offset_value = dz * (random.random() - 0.5)
            else:
                if 0 <= offset <= 1:
                    offset = offset * dz
                else:
                    raise ValueError(
                        "Sim->fibers->z_parameters->offset is a fraction of 1 node length. "
                        "Needs to be a value between 0 and 1 (inclusive)"
                    )

            # compute offset z coordinate
            z_offset = [my_z + offset + random_offset_value + additional_offset for my_z in z_values]

            z_offset = clip(
                z_offset,
                self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'min'),
                self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'max'),
                myel,
            )

            my_fiber = [(my_x, my_y, z) for z in z_offset]
            random_offset_ratio = random_offset_value / dz

            return my_fiber, random_offset_ratio

        def generate_z_unmyel(mydiams):
            """Generate the z values for an unmyelinated fiber.

            :param mydiams: The diameters of the fiber.
            :raises IncompatibleParametersError: If no dz is provided for supersampled bases.
            :raises ValueError: If the fiber generated is too long.
            :return: The z values of the fiber.
            """
            fibers = []
            if super_sample:
                if 'dz' in self.configs[Config.SIM.value]['supersampled_bases']:
                    delta_z = self.search(Config.SIM, 'supersampled_bases', 'dz')
                else:
                    raise IncompatibleParametersError("No dz provided for Sim generating super-sampled bases.")

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

            for (x, y), diam in zip(fibers_xy, diams):
                fiber_pre, offset_ratio = build_fiber_with_offset(
                    list(np.concatenate((z_bottom_half[:-1], z_top_half))),
                    myelinated,
                    delta_z,
                    x,
                    y,
                )
                if np.amax(np.array(fiber_pre)[:, 2]) - np.amin(np.array(fiber_pre)[:, 2]) > fiber_length:
                    raise ValueError("Fiber generated is longer than chosen fiber length")

                fiber = {'diam': diam, 'fiber': fiber_pre, 'offset_ratio': offset_ratio}

                fibers.append(fiber)
            return fibers

        def generate_z_myelinated(mydiams):
            """Generate the z values for a myelinated fiber.

            :param mydiams: The diameters of the fiber.
            :raises ValueError: If the fiber is too long.
            :return: The z values of the fiber.
            """
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

                fiber_pre, offset_ratio = build_fiber_with_offset(
                    zs, myelinated, delta_z, x, y, z_shift_to_center_in_fiber_range
                )
                if np.amax(np.array(fiber_pre)[:, 2]) - np.amin(np.array(fiber_pre)[:, 2]) > fiber_length:
                    raise ValueError("Fiber generated is longer than chosen fiber length")

                fiber = {'diam': diam, 'fiber': fiber_pre, 'offset_ratio': offset_ratio}
                fibers.append(fiber)
            return fibers

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
        diameter = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'diameter')

        diams, my_z_seed, myelinated = self.calculate_fiber_diams(
            diameter, fiber_geometry_mode_name, fibers_xy, super_sample
        )

        if myelinated and not super_sample:  # MYELINATED
            fibers = generate_z_myelinated(diams)

        else:  # UNMYELINATED
            fibers = generate_z_unmyel(diams)

        return fibers

    def calculate_fiber_diams(self, diameter, fiber_geometry_mode_name, fibers_xy, super_sample):
        """Calculate the diameters of the fibers.

        :param diameter: The diameter of the fiber, or a dictionary of parameters for the diameter distribution.
        :param fiber_geometry_mode_name: The name of the fiber geometry mode.
        :param fibers_xy: The xy coordinates of the fibers.
        :param super_sample: Whether to super sample the fibers.
        :raises IncompatibleParametersError: If an improper mode is chosen
        :raises ValueError: If lower_fiber_diam is too low
        :return: The diameters of the fibers.
        """
        diam_distribution: bool = type(diameter) is dict
        diams = []

        if super_sample:
            myelinated = False
            my_z_seed = None
            diams = [None] * len(fibers_xy)
        else:
            myelinated = self.search(
                Config.FIBER_Z,
                MyelinationMode.parameters.value,
                fiber_geometry_mode_name,
                'myelinated',
            )
            my_z_seed = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'seed')

            if not diam_distribution:
                diams = [diameter] * len(fibers_xy)
            else:
                sampling_mode = self.search(
                    Config.FIBER_Z,
                    MyelinationMode.parameters.value,
                    fiber_geometry_mode_name,
                    'sampling',
                )
                if myelinated and (sampling_mode != MyelinatedSamplingType.INTERPOLATION.value):
                    raise IncompatibleParametersError(
                        "To simulate myelinated fibers from a distribution of diameters must use MRG_INTERPOLATION"
                    )
                distribution_mode_name = diameter['mode']

                distribution_mode: DiamDistMode = [
                    mode for mode in DiamDistMode if str(mode).split('.')[-1] == distribution_mode_name
                ][0]
                # seed rng
                my_diam_seed: int = diameter['seed']
                np.random.seed(my_diam_seed)

                fiber_diam_dist = None
                if distribution_mode == DiamDistMode.UNIFORM:
                    # load parameters
                    lower_fiber_diam: float = diameter['lower']
                    upper_fiber_diam: float = diameter['upper']

                    # parameter checking
                    # positive values, order makes sense, etc
                    if lower_fiber_diam < 0:
                        raise ValueError("lower_fiber_diam bound must be positive length for UNIFORM method")
                    if lower_fiber_diam > upper_fiber_diam:
                        raise ValueError("upper_fiber_diam bound must be >= lower_fiber_diam bound for UNIFORM method")

                    fiber_diam_dist = stats.uniform(lower_fiber_diam, upper_fiber_diam - lower_fiber_diam)

                elif distribution_mode == DiamDistMode.TRUNCNORM:
                    # load parameters
                    n_std_fiber_diam_limit: float = diameter['n_std_limit']
                    mu_fiber_diam: float = diameter['mu']
                    std_fiber_diam: float = diameter['std']
                    lower_fiber_diam = mu_fiber_diam - n_std_fiber_diam_limit * std_fiber_diam
                    upper_fiber_diam = mu_fiber_diam + n_std_fiber_diam_limit * std_fiber_diam

                    # parameter checking
                    # positive values, order makes sense, etc
                    if n_std_fiber_diam_limit == 0 and std_fiber_diam != 0:
                        raise IncompatibleParametersError(
                            "Conflicting arguments for std_fiber_diam and n_std_fiber_diam_limit for TRUNCNORM method"
                        )
                    if lower_fiber_diam < 0:
                        raise ValueError("lower_fiber_diam must be defined as >= 0 for TRUNCNORM method")

                    fiber_diam_dist = stats.truncnorm(
                        (lower_fiber_diam - mu_fiber_diam) / std_fiber_diam,
                        (upper_fiber_diam - mu_fiber_diam) / std_fiber_diam,
                        loc=mu_fiber_diam,
                        scale=std_fiber_diam,
                    )
                diams = fiber_diam_dist.rvs(len(fibers_xy))
        return diams, my_z_seed, myelinated

    def calculate_fiber_length_params(self, override_length):
        """Calculate the fiber length parameters.

        :param override_length: Whether or not to override the length.
        :raises IncompatibleParametersError: If parameters are not set properly.
        :return: The fiber length parameters.
        """
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
                    'Suppress this warning by adding "full_nerve_length = true" to your z_parameters.',
                    stacklevel=2,
                )
            self.configs['sims']['fibers'][FiberZMode.parameters.value]['full_nerve_length'] = False

        else:
            if self.configs['sims']['fibers']['z_parameters'].get('full_nerve_length') is True:
                raise IncompatibleParametersError(
                    "If min and max are defined (sim config>fiber>z_parameters), "
                    "then full_nerve_length must either not be defined, or be false"
                )

            min_fiber_z_limit = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'min')
            max_fiber_z_limit = self.search(Config.SIM, 'fibers', FiberZMode.parameters.value, 'max')

            if not max_fiber_z_limit > min_fiber_z_limit:
                raise IncompatibleParametersError(
                    "sims->fibers->z_parameters->min is greater than sims->fibers->z_parameters->max"
                )

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
        """Check to ensure fiberset is valid.

        :raises MorphologyError: if fiber points are too close to an inner boundary.
        """
        # check that all fibers are inside inners, accounting for trace buffer
        all_inners = [inner.deepcopy() for fascicle in self.sample.slides[0].fascicles for inner in fascicle.inners]
        if self.xy_mode != FiberXYMode.CENTROID:
            buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')
            [inner.offset(distance=-buffer) for inner in all_inners]
        else:
            warnings.warn("Ignoring xy_trace_buffer since xy_mode is centroid", stacklevel=2)
        allpoly = unary_union([inner.polygon().buffer(0) for inner in all_inners])
        if not np.all(
            [
                Point(fiber['fiber'][0][:-1]).within(allpoly) if type(fiber) is dict else Point(fiber).within(allpoly)
                for fiber in self.fibers
            ]
        ):
            raise MorphologyError(
                "Fiber points were detected too close to an inner boundary (as defined by xy_trace_buffer in SIM)."
            )
        # add other checks below

    def xy_points(self, split_xy=False):
        """Get the xy points of the fibers.

        :param split_xy: Whether or not to split the xy points into separate arrays.
        :return: The xy points of the fibers.
        """
        if isinstance(self.fibers[0], dict):
            points = [(f['fiber'][0][0], f['fiber'][0][1]) for f in self.fibers]
        else:
            points = [(f[0][0], f[0][1]) for f in self.fibers]

        if split_xy:
            return list(zip(*points))[0], list(zip(*points))[1]
        else:
            return points
