# builtins

# packages

# access
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from shapely.affinity import scale
from shapely.geometry import LineString, Point

from .sample import Sample
from src.utils import *


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
        self.fibers = self._generate_z(fibers_xy)
        return self

    def write(self, mode: WriteMode, path: str):
        """
        :param mode:
        :param path:
        :return:
        """
        for i, fiber in enumerate(self.fibers):
            np.savetxt(
                os.path.join(path, str(i) + WriteMode.file_endings.value[mode.value]),
                np.concatenate(([len(fiber)], fiber)),
                fmt='%.5f'
            )
        return self

    def _generate_xy(self) -> np.ndarray:
        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_mode_name: str = self.search(Config.SIM, 'fibers', 'mode')
        xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
        xy_parameters: dict = self.search(Config.SIM, xy_mode.parameters.value)

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
                self.sample.slides[0].plot(final=False, fix_aspect_ratio=True)

                # TODO
                # for point in np.reshape(fascicles, (-1, 2)):
                #     plt.plot(*point, 'r*')

                plt.show()
        else:
            self.throw(30)

        return []

    def _generate_z(self, fibers_xy):
        pass
