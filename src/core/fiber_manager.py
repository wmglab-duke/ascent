# builtins
import json
import random
from typing import Dict, List, Tuple, Union

# packages
import numpy as np
import matplotlib.pyplot as plt
from shapely.affinity import scale
from shapely.geometry import LineString, Point

# access
from .slide_manager import SlideManager
from src.utils import *


class FiberManager(Exceptionable, Configurable, Saveable):
    """
    Required (Config.) JSON's
        MODEL
        SIM
        FIBER_Z
    """

    def __init__(self, slide_manager: SlideManager, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        # set self manager
        self.manager = slide_manager

        # initialize empty lists of fiber points
        self.xy_coordinates = None
        self.full_coordinates = None

        # empty metadata
        self.fiber_metadata: Dict[str, list] = {}

    def fiber_xy_coordinates(self, plot: bool = False, save: bool = False, buffer: float = 5.0) \
            -> List[List[List[tuple]]]:
        """
        :return: tuple containing two lists of tuples,
                    1) first list of tuples is points [(x, y)]
                    2) second list of tuples is metadata [(fascicle_index, inner_index, fiber_index)]
        """

        # get required parameters from configuration JSON (using inherited Configurable methods)
        xy_mode: FiberXYMode = self.search_mode(FiberXYMode, Config.SIM)
        mode_name = str(xy_mode).split('.')[1]
        xy_parameters: dict = self.search(Config.SIM, xy_mode.parameters.value, mode_name)

        # initialize result lists
        fascicles: List[List[List[tuple]]] = []

        # perform implemented mode
        if self.search_mode(FiberZMode, Config.MODEL) == FiberZMode.EXTRUSION:

            if xy_mode == FiberXYMode.CENTROID:
                for fascicle in self.manager.slides[0].fascicles:
                    inners = []
                    for inner in fascicle.inners:
                        fibers = []
                        for _ in (0,):
                            fibers.append(inner.centroid())
                        inners.append(fibers)
                    fascicles.append(inners)

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

                    for fascicle in self.manager.slides[0].fascicles:
                        inners = []
                        for inner in fascicle.inners:
                            fiber_count = target_density * inner.area()
                            if fiber_count < minimum_number:
                                fiber_count = minimum_number
                            fibers = []
                            for point in inner.random_points(fiber_count, buffer=buffer):
                                fibers.append(point)
                            inners.append(fibers)
                        fascicles.append(inners)

                else:  # do bottom-up approach
                    # get required parameters
                    target_number = xy_parameters.get('target_number')
                    maximum_number = xy_parameters.get('maximum_number')

                    # calculate target density
                    min_area = np.amin([[fascicle.smallest_trace().area()
                                         for fascicle in self.manager.slides[0].fascicles]])
                    target_density = float(target_number) / min_area

                    for fascicle in self.manager.slides[0].fascicles:
                        inners = []
                        for inner in fascicle.inners:
                            fiber_count = target_density * inner.area()
                            if fiber_count > maximum_number:
                                fiber_count = maximum_number

                            fibers = []
                            for point in inner.random_points(fiber_count, buffer=buffer):
                                fibers.append(point)
                            inners.append(fibers)
                        fascicles.append(inners)

            elif xy_mode == FiberXYMode.UNIFORM_COUNT:
                count: int = xy_parameters.get('count')

                for fascicle in self.manager.slides[0].fascicles:
                    inners = []
                    for inner in fascicle.inners:
                        fibers = []
                        for point in inner.random_points(count, buffer=buffer):
                            fibers.append(point)
                        inners.append(fibers)
                    fascicles.append(inners)

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
                for fascicle in self.manager.slides[0].fascicles:
                    inners = []
                    for inner in fascicle.inners:
                        fibers = []

                        if find_centroid:
                            fibers.append(inner.centroid())

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
                                fibers.append(point)

                        inners.append(fibers)
                    fascicles.append(inners)

            if plot:
                self.manager.slides[0].plot(final=False, fix_aspect_ratio=True)

                # TODO
                # for point in np.reshape(fascicles, (-1, 2)):
                #     plt.plot(*point, 'r*')

                plt.show()
        else:
            self.throw(30)

        if save:
            self.xy_coordinates = fascicles

        return fascicles

    def fiber_z_coordinates(self, xy_coordinates: List[List[List[Tuple[float]]]], save: bool = False):
        """
        Finds coordinates to top of axon (1/2 to 1) then flips down to find bottom half
        :param save:
        :param xy_coordinates: list of tuple (x,y) points. this is a parameter, not saved as instance variable so the
        user is able to filter points to only find z coordinates for desired fascicles/inners/fibers
        :return: see param return_points
        """

        # reset fiber metadata
        self.fiber_metadata = {
            "fiber_z_modes": [],
            "fiber_types": [],
            "subsets": [],
            "offsets": self.search(Config.SIM, FiberZMode.parameters.value, 'offsets'),
            "fascicles": [],
            "inners": [],
            "fibers": []
        }

        def clip(values: list, start, end, myel: MyelinationMode) -> list:

            step = 1
            if myel == MyelinationMode.MYELINATED:
                step = 11

            while values[0] < start:
                values = values[step:]

            while values[-1] > end:
                values = values[:-step]

            return values

        def inner_loop(zs: list, myel_mode: MyelinationMode, length: float, dz: float):
            # init next dimension
            offsets_dimension = []
            # find base z values
            offsets = self.search(Config.SIM, FiberZMode.parameters.value, 'offsets')
            for offset in offsets:
                random_offset = False
                if offset is None:
                    offset = 0.0
                    random_offset = True

                z_subsets_offset = clip([z + offset for z in zs], dz, length - dz, myel_mode)

                fascicles_dimension = []
                self.fiber_metadata['fascicles'].append(list(range(len(xy_coordinates))))
                for fascicle in xy_coordinates:
                    self.fiber_metadata['inners'].append(list(range(len(fascicle))))
                    inners_dimension = []
                    for inner in fascicle:
                        self.fiber_metadata['fibers'].append(list(range(len(inner))))
                        fibers_dimension = []
                        for x, y in inner:  # get specific fiber (x, y point)

                            points = [(x, y, z) for z in z_subsets_offset]

                            if random_offset:
                                random_offset_value = dz * (random.random() - 0.5)
                                points = [(x, y, z + random_offset_value) for x, y, z in points]

                            fibers_dimension.append(points)
                        inners_dimension.append(fibers_dimension)
                    fascicles_dimension.append(inners_dimension)
                offsets_dimension.append(fascicles_dimension)
            return offsets_dimension

        #%% START ALGORITHM

        # get top-level fiber z generation
        fiber_z_mode: FiberZMode = self.search_mode(FiberZMode, Config.MODEL)
        self.fiber_metadata['fiber_z_modes'].append(fiber_z_mode)

        # all functionality is only defined for EXTRUSION as of now
        if fiber_z_mode == FiberZMode.EXTRUSION:

            # get the correct fiber lengths
            fiber_length = self.search(Config.MODEL, 'medium', 'length')
            half_fiber_length = fiber_length / 2

            # search for all myelination modes (length of this corresponds to length of total modes looped through)
            # TODO: set values in FIBER TYPES ENUM to associated myel mode
            myelination_modes = self.search_multi_mode(Config.SIM, MyelinationMode)

            # TODO: INTERPOLATION FOR MYELINATED

            # get all the fiber modes (BOTH myel and unmyel)
            fiber_modes: List[Union[MyelinatedFiberType, UnmyelinatedFiberType]] =\
                self.search_multi_mode(Config.SIM, modes=[MyelinatedFiberType, UnmyelinatedFiberType])

            # init first dimension
            fiber_mode_dimension = []
            # loop through paired fiber mode and myelination modes
            for fiber_mode, myelination_mode in zip(fiber_modes, myelination_modes):

                self.fiber_metadata['fiber_types'].append(fiber_mode)

                fiber_mode_search_params = [MyelinationMode.parameters.value,
                                            *[str(m).split('.')[-1] for m in (myelination_mode, fiber_mode)]]

                if myelination_mode == MyelinationMode.MYELINATED:

                    # load in all the required specifications for finding myelinated z coordinates
                    subset, \
                        node_length,\
                        paranodal_length_1,\
                        diameters,\
                        delta_zs,\
                        paranodal_length_2s = (self.search(Config.FIBER_Z, *fiber_mode_search_params, key) for key in
                                               ['subset',
                                                'node_length',
                                                'paranodal_length_1',
                                                'diameters',
                                                'delta_zs',
                                                'paranodal_length_2s'])

                    self.fiber_metadata['subsets'].append(subset)

                    # init next dimension
                    subsets_dimension = []
                    for subset_index, (diameter, delta_z, paranodal_length_2) in enumerate(zip(diameters,
                                                                                               delta_zs,
                                                                                               paranodal_length_2s)):

                        inter_length = (delta_z - node_length - (2 * paranodal_length_1) - (2 * paranodal_length_2)) / 6

                        if diameter in subset:
                            z_steps: List = []
                            while sum(z_steps) < half_fiber_length:
                                z_steps += [(node_length / 2) + (paranodal_length_1 / 2),
                                            (paranodal_length_1 / 2) + (paranodal_length_2 / 2),
                                            (paranodal_length_2 / 2) + (inter_length / 2),
                                            *([inter_length] * 5),
                                            (inter_length / 2) + (paranodal_length_2 / 2),
                                            (paranodal_length_2 / 2) + (paranodal_length_1 / 2),
                                            (paranodal_length_1 / 2) + (node_length / 2)]

                            reverse_z_steps = z_steps.copy()
                            reverse_z_steps.reverse()

                            # concat, cumsum, and other stuff to get final list of z points
                            z_subset = np.array(
                                clip(
                                    list(
                                        np.cumsum(
                                            np.concatenate(
                                                ([0], reverse_z_steps, z_steps)
                                            )
                                        )
                                    ),
                                    0,
                                    fiber_length,
                                    myelination_mode
                                )
                            )

                            subsets_dimension.append(inner_loop(list(z_subset),
                                                                myelination_mode,
                                                                fiber_length,
                                                                delta_z))

                    fiber_mode_dimension.append(subsets_dimension)

                else:  # UNMYELINATED

                    delta_zs: list = self.search(Config.FIBER_Z, *fiber_mode_search_params, 'delta_zs')

                    subsets_dimension = []
                    for delta_z in delta_zs:

                        z_top_half = np.arange(fiber_length/2, fiber_length+delta_z, delta_z)
                        z_bottom_half = -np.flip(z_top_half)+fiber_length

                        while z_top_half[-1] > fiber_length:
                            # trim top of top half
                            z_top_half = z_top_half[:-1]
                            z_bottom_half = z_bottom_half[1:]

                        z_subset = np.concatenate((z_bottom_half[:-1], z_top_half))

                        subsets_dimension.append(inner_loop(list(z_subset),
                                                            myelination_mode,
                                                            fiber_length,
                                                            delta_z))

                    fiber_mode_dimension.append(subsets_dimension)

            # return and save top dimension of z points list
            if save:
                self.full_coordinates = fiber_mode_dimension
            return fiber_mode_dimension

        else:
            self.throw(31)

    class Encoder(json.JSONEncoder):
        """
        This is a helper class for converting a NumPy array (ndarray) to a JSON file
        """
        EXPORTABLE_ENUMS = {
            'FiberZMode': FiberZMode,
            'MyelinatedFiberType': MyelinatedFiberType,
            'UnmyelinatedFiberType': UnmyelinatedFiberType
        }

        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif type(obj) in self.EXPORTABLE_ENUMS.values():
                return {"__enum__": str(obj)}
            return json.JSONEncoder.default(self, obj)

    def save_full_coordinates(self, path: str):
        """
        :return:
        """

        with open(path, "w") as handle:
            print('writing file')
            self.json_data = json.dumps({
                'order': [
                    'fiber modes',
                    'subsets',
                    'offsets',
                    'fascicles',
                    'inners',
                    'fibers',
                    'points'
                ],
                'metadata': self.fiber_metadata,
                'fibers': self.full_coordinates
            }, cls=self.Encoder)
            handle.write(self.json_data)
        print('done writing file')
        # raise Exception('forcing this to DIE')

