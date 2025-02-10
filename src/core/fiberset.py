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

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from nd_line.nd_line import nd_line
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
from .slide import Slide


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
        self.xy_mode = None
        self.z_mode = None
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
        if any(config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)):
            raise KeyError("Missing Model or Simulation configuration.")
        return self

    def generate(self, sim_directory: str, super_sample: bool = False):
        """Create xy(z) fiber coordinates, fiber-to-fascicle map, longitudinal coordinates, and validate fiber dataset.

        :param sim_directory: The directory to save the simulation files to.
        :param super_sample: Whether to generate a super sample.
        :raises NotImplementedError: If the z mode is not supported.
        :return: self
        """
        # Load fiber xy and z modes
        xy_mode_name: str = self.search(Config.SIM, 'fibers', 'xy_parameters', 'mode')
        self.xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
        try:
            fiber_z_mode_name: str = self.search(Config.SIM, 'fibers', 'z_parameters', 'mode')
            # If fiber z mode is in SIM file, cast to Enum FiberZMode object to maintain enum code consistency
            # (eventhough this can easily be done without enums & using string equality).
            self.z_mode: FiberZMode = [mode for mode in FiberZMode if str(mode).split('.')[-1] == fiber_z_mode_name][0]
        except KeyError:  # Backwards compatibility.
            # If fiber z mode doesn't exist in new position under Sim > fibers > z_parameters > mode,
            # look for it where it used to be located (in model.json) in previous ascent versions
            warnings.warn(
                'No fiber_z mode specified in sim.json under "fibers" > "z_parameters" > "mode". '
                'Proceeding with fiber_z mode from location in model.json.',
                stacklevel=2,
            )
            self.z_mode = self.search_mode(FiberZMode, Config.MODEL)

        # Generate fibers accordingly depending on fiber z mode.
        if self.z_mode == FiberZMode.EXTRUSION:
            # 3d fibers structure: (fiber #, z-index #, xyz-coordinates)
            # Assigns fiber to fascicle mapping based on xy coordinates of first z-index.
            # We are able to do this because fibers must be contained within a single contiguous fascicle
            # (this is checked when loading fibers in load_explicit_coords function).
            fibers_xy, (self.out_to_fib, self.out_to_in) = self._generate_xy(sim_directory)
            self.fibers = self._generate_longitudinal(fibers_xy, super_sample=super_sample)

        elif self.z_mode == FiberZMode.EXPLICIT:
            # 3d fibers structure: (fiber #, z-index #, xyz-coordinates)
            # Assigns fiber to fascicle mapping based on xy coordinates of first z-index.
            # We are able to do this because fibers must be contained within a single contiguous fascicle
            # (this is checked when loading fibers in load_explicit_coords function).
            fibers_xyz, (self.out_to_fib, self.out_to_in) = self._generate_xyz(sim_directory)
            self.fibers = self._generate_3d_longitudinal(fibers_xyz, sim_directory, super_sample=super_sample)

        else:
            raise NotImplementedError("That FiberZMode is not yet implemented.")

        if self.xy_mode in [FiberXYMode.EXPLICIT_3D, FiberXYMode.EXPLICIT] and hasattr(self.sample, 'init_slides'):
            # Validate fiber locations before transforming to final morphology if fibers were generated from
            # untransformed morphology (FiberXYMode == EXPLICIT or EXPLICIT_3D) and Sample object has saved
            # untransformed morphology (Sample.init_slides).
            self.validate(self.sample.init_slides[0])
            # Get fiber locations at each z position
            fib_is_dict = isinstance(self.fibers[0], dict)
            if fib_is_dict:
                all_z_xy = [self.xy_points(z_index=zi) for zi in range(len(self.fibers[0]['fiber']))]
            else:
                all_z_xy = [self.xy_points(z_index=zi) for zi in range(len(self.fibers[0]))]
            # Transform to final fiber locations and set new locations
            tfm_z_xy = self.sample.point_transform(all_z_xy)[0]
            for zi, z_xy in enumerate(tfm_z_xy):
                self.set_xy_points(z_xy, z_index=zi)

        self.validate()

        # Save fibers_xy figure of first z-index (by default) to visually align with fiber-to-fascicle mapping.
        self.plot_fibers_on_sample(sim_directory)
        if self.z_mode == FiberZMode.EXPLICIT:
            self.plot_3d_fibers_on_sample(self.fibers)  # Visualize 3D fibers

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
                np.savetxt(f2, diams, fmt='%0.6f')
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

    def _generate_xy(self, sim_directory: str) -> tuple[np.ndarray, tuple[list, list]]:
        """Generate the xy coordinates of the fibers.

        :param sim_directory: The directory of the simulation.
        :raises NotImplementedError: If a mode is not supported.
        :return: xy coordinates of the fibers
        """
        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_parameters: dict = self.search(Config.SIM, 'fibers', 'xy_parameters')
        my_xy_seed: int = xy_parameters.get('seed', 0)

        # small behavioral parameters
        buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')

        # perform implemented mode
        # error if an invalid mode is selected
        if self.xy_mode == FiberXYMode.CENTROID:  # noqa: R505
            points = self.generate_centroid_points()

        elif self.xy_mode == FiberXYMode.UNIFORM_DENSITY:
            points = self.generate_uniform_density_points(buffer, my_xy_seed)

        elif self.xy_mode == FiberXYMode.UNIFORM_COUNT:
            points = self.generate_uniform_count_points(buffer, my_xy_seed)

        elif self.xy_mode == FiberXYMode.WHEEL:
            points = self.generate_wheel_points(buffer)

        elif self.xy_mode == FiberXYMode.EXPLICIT:
            points = self.load_explicit_coords(sim_directory)

            # Map to untransformed morphology, else legacy map to transformed morphology
            if hasattr(self.sample, 'init_slides'):
                return points, self.sample.init_slides[0].map_points(points)

        else:
            raise NotImplementedError("Invalid FiberXYMode in Sim.")

        return points, self.sample.slides[0].map_points(points)

    def _generate_xyz(self, sim_directory: str) -> tuple[np.ndarray, tuple[list, list]]:
        """Generate the xyz coordinates of the fibers.

        :param sim_directory: The directory of the simulation.
        :raises NotImplementedError: If a mode is not supported.
        :return: xy coordinates of the fibers
        """
        if self.xy_mode != FiberXYMode.EXPLICIT_3D:
            raise NotImplementedError(
                "Invalid FiberXYMode in Sim. FiberXYMode must be 'EXPLICIT_3D' when FiberZMode is 'EXPLICIT'."
            )
        points = self.load_explicit_coords(sim_directory, is_3d=True)
        # Map to untransformed morphology, else legacy map to transformed morphology
        if hasattr(self.sample, 'init_slides'):
            return points, self.sample.init_slides[0].map_points(points)

        return points, self.sample.slides[0].map_points(points)

    def generate_centroid_points(self) -> list[tuple[float, float]]:
        """Create the xy coordinates of the fibers using the centroid of the fascicles.

        :return: xy coordinates of the fibers
        """
        points = []
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
        points: list[tuple[float]] = []
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
        points: list[tuple[float]] = []
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
        points: list[tuple[float]] = []
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
                    scaled_vectors: list[LineString] = [
                        scale(trimmed_spoke_vector, *([factor] * 3), origin=trimmed_spoke_vector.coords[0])
                        for factor in np.linspace(0, 1, point_count + 2)[1:-1]
                    ]

                    # loop through the end points of the vectors
                    for point in [vector.coords[1] for vector in scaled_vectors]:
                        points.append(point)
        return points

    def load_explicit_coords(self, sim_directory, is_3d=False):
        """Load the xy(z) coordinates of the fibers from an explicit file.

        :param sim_directory: The directory of the simulation.
        :param is_3d: Boolean indicating if explicit file contains 3D xyz-coordinates. Optional. Default: False.
        :raises FileNotFoundError: If the coordinates file is not found.
        :return: The xy coordinates of the fibers.
        """
        explicit_index = self.search(Config.SIM, 'fibers', 'xy_parameters', 'explicit_fiberset_index')
        # 3D fiber file format is stored in .npy pickled files; can't be stored in .txt file.
        file_extension = 'npy' if is_3d else 'txt'
        if explicit_index is not None:
            input_sample_name = self.sample.configs['sample']['sample']
            explicit_source = os.path.join(
                'input', input_sample_name, 'explicit_fibersets', f'{explicit_index}.{file_extension}'
            )
            explicit_dest = os.path.join(sim_directory, f'explicit.{file_extension}')
            shutil.copyfile(explicit_source, explicit_dest)
        else:
            print(
                '\t\tWARNING: Explicit fiberset index not specified.'
                '\n\t\tProceeding with backwards compatible check for explicit.txt in:'
                f'\n\t\t{sim_directory}'
            )
        if not os.path.exists(os.path.join(sim_directory, f'explicit.{file_extension}')):
            raise FileNotFoundError(
                f"FiberXYMode is EXPLICIT or EXPLICIT_3D in Sim, but no explicit.{file_extension} file with "
                "coordinates is in the Sim directory. See config/system/templates/explicit.txt for example "
                "of this file's required format."
            )

        if is_3d:
            points = np.load(explicit_dest, allow_pickle=True)
            # Center 3D coordinates and extrude ends if provided coordinate lengths aren't long enough for model.
            return self.preprocess_3d_coords(points)

        with open(explicit_dest) as f:
            # advance header
            next(f)
            reader = csv.reader(f, delimiter=" ")
            return [(float(row[0]), float(row[1])) for row in reader]

    def preprocess_3d_coords(self, points):
        """Centers 3D coordinates in xy plane to align with nerve morphology and extrudes fibers if applicable.

        :param points: The fiber points.
        :raises ValueError: If any explicit fiber is longer than the model length.
        :return: The preprocessed xyz coordinates of the fibers.
        """
        # Calculate fiber length
        min_fiber_z = self.search(Config.SIM, 'fibers', 'z_parameters', 'min', optional=True)
        max_fiber_z = self.search(Config.SIM, 'fibers', 'z_parameters', 'max', optional=True)
        if not (min_fiber_z and max_fiber_z):
            desired_fiber_length = self.search(Config.MODEL, 'medium', 'proximal', 'length')
        else:
            desired_fiber_length = max_fiber_z - min_fiber_z

        provided_fiber_lengths = np.array([p[-1, 2] - p[0, 2] for p in points])
        if np.any(provided_fiber_lengths > desired_fiber_length):
            raise ValueError(
                'At least one fiber is longer than the desired fiber length '
                '(provided by either the proximal medium length by default, '
                'or the "fibers">"z_parameters">"min"/"max" variables in sim.json.)'
                'Please extend your model length, or shorten your fibers.'
            )

        if np.any(provided_fiber_lengths < desired_fiber_length):
            warnings.warn(
                'Extruding explicit 3d fiber lengths. At least one fiber is shorter than desired fiber length '
                '(provided by either the proximal medium length by default, '
                'or the "fibers">"z_parameters">"min"/"max" variables in sim.json.)',
                stacklevel=2,
            )

        for fib_idx, fiber in enumerate(points):
            fiber_length = provided_fiber_lengths[fib_idx]

            # Extrude fiber to desired length, if applicable
            if fiber_length < desired_fiber_length:
                # Shift z-coordinates based on longest fiber length to maintain fiber z-axis allignment
                # Default to no shift occuring
                fiber_z_shift = self.search(Config.SIM, 'fibers', 'z_parameters', 'fiber_z_shift', optional=True) or 0
                base_extrusion_dist = (desired_fiber_length - provided_fiber_lengths.max()) / 2
                assert abs(fiber_z_shift) <= base_extrusion_dist, (
                    f'fiber_z_shift magnitude ({abs(fiber_z_shift)}) it too large (must be <={base_extrusion_dist}). '
                    'Fibers will get shifted outside of model length.'
                )
                extrusion_dist_superior = base_extrusion_dist + fiber_z_shift  # [um].
                z_shifted = fiber[:, 2] + extrusion_dist_superior

                # Build values for extrusion superior to fiber end point
                inferred_z_spacing = np.mean(np.diff(fiber[:, 2]))  # [um]
                superior_pad_values = np.arange(min_fiber_z, extrusion_dist_superior, inferred_z_spacing)

                # Create extruded z points based on each fiber's individual length
                z_extruded = np.hstack(
                    (superior_pad_values, z_shifted, np.arange(z_shifted[-1], max_fiber_z + 1, inferred_z_spacing))
                )

                # Create corresponding extruded xy points by replicating end-points for each fiber.
                # (Z points by default will be replicated too)
                padded_fiber = np.pad(
                    fiber,
                    (
                        (len(superior_pad_values), len(np.arange(z_shifted[-1], max_fiber_z + 1, inferred_z_spacing))),
                        (0, 0),
                    ),
                    mode='edge',
                )

                points[fib_idx] = np.array(padded_fiber)
                points[fib_idx][:, 2] = np.array(z_extruded)  # Update z points with extruded coordinates

        # Transform from list of arrays to 3D array now that all fibers are the same length
        return np.stack(points)

    def plot_fibers_on_sample(self, sim_directory, z_index=0):
        """Plot the xy coordinates of the fibers on the sample.

        :param sim_directory: The directory of the simulation.
        :param z_index: Optional index to plot fiber points at this z-location
        """
        fig = plt.figure()
        self.sample.slides[0].plot(
            final=False,
            fix_aspect_ratio='True',
            axlabel="\u03bcm",
            title='Fiber locations for nerve model',
        )
        self.plot(z_index=z_index)
        plt.savefig(sim_directory + '/plots/fibers_xy.png', dpi=300)
        if self.search(Config.RUN, 'popup_plots', optional=True) is False:
            plt.close(fig)
        else:
            plt.show()

    def plot_3d_fibers_on_sample(self, fibers, sample_slide=None, title='3D Fibers on Nerve Sample', color=None):
        """Plot the xyz coordinates of the fibers with inner outlines.

        :param fibers: The xyz coordinates of the fibers.
        :param sample_slide: Sample on which to plot fibers.
        :param title: The plot title.
        :param color: List or string of line color.
        """
        if sample_slide is None:
            sample_slide = self.sample.slides[0]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        fascicles = sample_slide.fascicles
        # Plot all inner traces on 3D plot
        for fasc in fascicles:
            for inner in fasc.inners:
                ax.plot(inner.points[:, 0], inner.points[:, 1], inner.points[:, 2], c='black', alpha=0.5)

        # If the sample contains a nerve, plot it
        if sample_slide.nerve:
            nerve_points = sample_slide.nerve.points
            nerve_x, nerve_y, nerve_z = nerve_points.T
            ax.plot(nerve_x, nerve_y, nerve_z, c='black', alpha=0.5)

        # Define fiber colormap and plot fibers
        n_fibers = len(fibers)
        if color is not None:
            if isinstance(color, list):
                assert len(color) == n_fibers
            else:
                color = [color for _ in range(n_fibers)]
        else:
            color = plt.cm.jet(np.linspace(0, 1, len(fibers)))
        for fiber_data, clr in zip(fibers, color):
            fiber = fiber_data['fiber'] if isinstance(fiber_data, dict) else fiber_data
            x, y, z = zip(*fiber)
            ax.plot(x, y, z, color=clr)

        ax.set_xlabel('x (um)')
        ax.set_ylabel('y (um)')
        ax.set_zlabel('z (um)')
        plt.title(title)
        plt.show()

    def plot(
        self,
        ax: plt.Axes = None,
        z_index=0,
        scatter_kws: dict = None,
    ):
        """Plot the xy coordinates of the fibers.

        :param ax: The axis to plot on. If None, use the current axis.
        :param z_index: Optional index to plot fiber data at this specific point on the z-axis.
        :param scatter_kws: The matplotlib keyword arguments for the scatter plot.
        """
        if ax is None:
            ax = plt.gca()
        if scatter_kws is None:
            scatter_kws = {}
        scatter_kws.setdefault('c', 'red')
        scatter_kws.setdefault('s', 10)
        scatter_kws.setdefault('marker', 'o')
        x, y = self.xy_points(split_xy=True, z_index=z_index)
        ax.scatter(
            x,
            y,
            **scatter_kws,
        )

    def _generate_longitudinal(  # noqa: C901
        self, fibers_xy: np.ndarray, override_length=None, super_sample: bool = False
    ) -> np.ndarray:
        """Generate the 1D longitudinal coordinates of the fibers.

        :param fibers_xy: The xy coordinates of the fibers.
        :param override_length: The length of the fibers (forced).
        :param super_sample: Whether to use supersampling.
        :return: The longitudinal coordinates of the fibers.
        """

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
                z_steps: list = []
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

                if fiber_geometry_mode_name == FiberGeometry.SMALL_MRG_INTERPOLATION_V1.value:
                    delta_z = eval(delta_z_str)
                    inter_length = eval(inter_length_str)
                    if diameter > 16.0 or diameter < 1.011:
                        raise ValueError(
                            "Diameter entered for SMALL_MRG_INTERPOLATION_V1 must be"
                            "between 1.011 and 16.0 (inclusive)."
                        )
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
            return generate_z_myelinated(diams)

        # else UNMYELINATED
        return generate_z_unmyel(diams)

    def _generate_3d_longitudinal(  # noqa: C901
        self, fibers_xyz: np.ndarray, sim_directory: str, super_sample: bool = False
    ) -> np.ndarray:
        """Generate the 1D longitudinal coordinates for each invidual 3D fiber.

        :param fibers_xyz: The xyz coordinates of the fibers.
        :param sim_directory: The directory to save the simulation files to.
        :param super_sample: Whether to use supersampling.
        :return: The longitudinal coordinates of the fibers.
        """
        save = self.search(Config.SIM, 'saving', '3D_fiber_intermediate_data', optional=True)
        if save:
            [
                os.makedirs(os.path.join(sim_directory, s), exist_ok=True)
                for s in ['3D_fiber_lengths', '3D_fiber_coords']
            ]

        # Generate the longitudinal coordinate points for sampling potentials, depending on individual fiber's length
        fibers = []
        for idx, fiber in enumerate(fibers_xyz):
            nd = nd_line(fiber)
            le = nd.length  # Euclidean fiber length
            fiber_dict = self._generate_longitudinal([(0, 0)], super_sample=super_sample, override_length=le)[0]
            longitudinal_coords = fiber_dict['fiber']
            longitudinal_coords = np.vstack(longitudinal_coords)[:, -1]  # Reshape
            coords = np.zeros([len(longitudinal_coords), 3])
            coords[:, 2] = longitudinal_coords

            # Map compartment coordinates to points along the 3D nerve to obtain where to sample potentials
            sample_points = [tuple(nd.interp(p)) for p in longitudinal_coords]
            fiber_dict['fiber'] = sample_points
            fibers.append(fiber_dict)

            if save:
                np.savetxt(
                    f'{sim_directory}/3D_fiber_lengths/{idx}.dat',
                    [le],
                )
                np.savetxt(  # Seems unnecessary, but 3D pipeline did it so maintained functionality here.
                    f'{sim_directory}/3D_fiber_coords/{idx}.dat',
                    coords,
                    delimiter=' ',
                    fmt='%.10f',
                    header=str(len(longitudinal_coords)),
                    comments='',
                )
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
        diam_distribution: bool = isinstance(diameter, dict)
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

    def validate(self, slide: Slide = None):
        """Check to ensure fiberset is valid.

        :param slide: slide to validate against. If None, Fiberset.sample.slides[0] will be used.
        :raises MorphologyError: if fiber points are too close to an inner boundary.
        """
        if slide is None:
            slide = self.sample.slides[0]
        # check that all fibers are inside inners, accounting for trace buffer
        all_inners = [inner.deepcopy() for fascicle in slide.fascicles for inner in fascicle.inners]
        if len(all_inners) == 0:
            all_inners = [fascicle.outer.deepcopy() for fascicle in slide.fascicles]
        if self.xy_mode != FiberXYMode.CENTROID:
            buffer: float = self.search(Config.SIM, 'fibers', 'xy_trace_buffer')
            for inner in all_inners:
                inner.offset(distance=-buffer)  # offset is a mutating function
        else:
            warnings.warn("Ignoring xy_trace_buffer since xy_mode is centroid", stacklevel=2)

        # Check that fibers are within exactly one inner
        allpoly = unary_union([inner.polygon().buffer(0) for inner in all_inners])
        invalid_fibers = []
        for fiber in self.fibers:
            fib_data = fiber['fiber'] if isinstance(fiber, dict) else fiber
            if self.z_mode == FiberZMode.EXTRUSION:
                if not Point(fib_data[0]).within(allpoly):
                    invalid_fibers.append(fib_data)
            else:
                if not all(Point(p).within(allpoly) for p in fib_data):
                    invalid_fibers.append(fib_data)

        if len(invalid_fibers) > 0:
            fibs = self.fibers + invalid_fibers
            clrs = ['blue' for _ in self.fibers] + ['red' for _ in invalid_fibers]
            self.plot_3d_fibers_on_sample(
                fibs,
                sample_slide=slide,
                title="Invalid fibers too close to or intersects with inner boundaries",
                color=clrs,
            )
            raise MorphologyError(
                'Fiber points were detected too close to an inner boundary (as defined by xy_trace_buffer in SIM),'
            )

    def xy_points(self, split_xy=False, z_index=0):
        """Get the xy points of the fibers.

        :param split_xy: Whether or not to split the xy points into separate arrays.
        :param z_index: Get xy points at this z index. Wouldn't affect extrusion models. Optional.
        :return: The xy points of the fibers at z_index (if provided) or at the first index by default.
        """
        if isinstance(self.fibers[0], dict):
            points = [(f['fiber'][z_index][0], f['fiber'][z_index][1]) for f in self.fibers]
        else:
            points = [(f[z_index][0], f[z_index][1]) for f in self.fibers]

        if split_xy:
            return list(zip(*points))[0], list(zip(*points))[1]

        return points

    def set_xy_points(self, xy_points, z_index=0):
        """Set the xy points of the fibers.

        This function is only called when FiberXYMode is EXPLICIT or EXPLICIT_3D. Fiber locations will be placed
        on the untransformed sample morphology, then transformed to follow the fascicle deformation, then set again
        in this function.

        :param xy_points: 2D array of xy points to set. First dimension must equal len(FiberSet.fibers)
        :param z_index: Set xy points at this z index. Wouldn't affect extrusion models. Optional.
        """
        if isinstance(self.fibers[0], dict):
            for f, (x, y) in zip(self.fibers, xy_points):
                f['fiber'][z_index] = (x, y, f['fiber'][z_index][2])
        else:
            for f, (x, y) in zip(self.fibers, xy_points):
                f[z_index] = (x, y, f[z_index][2])
