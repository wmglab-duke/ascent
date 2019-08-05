#!/usr/bin/env python3.7

# builtins
import itertools
import os
from typing import List, Union
import random

# packages
from shapely.geometry import LineString, Point
from shapely.affinity import scale
import numpy as np
import matplotlib.pyplot as plt

# SPARCpy
from .fascicle import Fascicle
from .nerve import Nerve
from .trace import Trace
from src.utils import *


class Slide(Exceptionable):

    def __init__(self, fascicles: List[Fascicle], nerve: Nerve, exception_config: list, will_reposition: bool = False):
        """
        :param fascicles: List of fascicles
        :param nerve: Nerve (effectively is a Trace)
        :param exception_config: pre-loaded configuration data
        :param will_reposition: boolean flag that tells the initializer whether or not it should be validating the
        geometries - if it will be reposition then this is not a concern
        """

        # init superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.nerve: Nerve = nerve
        self.fascicles: List[Fascicle] = fascicles

        if not will_reposition:
            # do validation (default is specific!)
            self.validation()

    def validation(self, specific: bool = True, die: bool = True, tolerance: float = None) -> bool:
        """
        Checks to make sure nerve geometry is not overlapping itself
        :param specific: if you want to know what made it fail first
        :param die: if non-specific, decides whether or not to throw an error if it fails
        :param tolerance: minimum separation distance for unit you are currently in
        :return: Boolean for True (no intersection) or False (issues with geometry overlap)
        """

        if specific:
            if self.fascicle_fascicle_intersection():
                self.throw(10)

            if self.fascicle_nerve_intersection():
                self.throw(11)

            if self.fascicles_outside_nerve():
                self.throw(12)

        else:
            if any([self.fascicle_fascicle_intersection(), self.fascicle_nerve_intersection(),
                    self.fascicles_outside_nerve(), self.fascicles_too_close(tolerance)]):
                if die:
                    self.throw(13)
                else:
                    return False
            else:
                return True

    def fascicles_too_close(self, tolerance: float = None) -> bool:
        """
        :param tolerance: Minimum separation distance
        :return: Boolean for True for fascicles too close as defined by tolerance
        """

        if tolerance is None:
            return False
        else:
            pairs = itertools.combinations(self.fascicles, 2)
            return any([first.min_distance(second) < tolerance for first, second in pairs]) or \
                any([fascicle.min_distance(self.nerve) < tolerance for fascicle in self.fascicles])

    def fascicle_fascicle_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects another fascicle, otherwise False
        """

        pairs = itertools.combinations(self.fascicles, 2)
        return any([first.intersects(second) for first, second in pairs])

    def fascicle_nerve_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects the nerve, otherwise False
        """

        return any([fascicle.intersects(self.nerve) for fascicle in self.fascicles])

    def fascicles_outside_nerve(self) -> bool:
        """
        :return: True if any fascicle lies outside the nerve, otherwise False
        """

        return any([not fascicle.within_nerve(self.nerve) for fascicle in self.fascicles])

    def move_center(self, point: np.ndarray):
        """
        :param point: the point of the new slide center
        """

        # get shift from nerve centroid and point argument
        shift = list(point - np.array(self.nerve.centroid())) + [0]

        # apply shift to nerve trace and all fascicles
        self.nerve.shift(shift)
        for fascicle in self.fascicles:
            fascicle.shift(shift)

    def reshaped_nerve(self, mode: ReshapeNerveMode) -> Nerve:
        """
        :param mode: Final form of reshaped nerve, either circle or ellipse
        :return: a copy of the nerve with reshaped nerve boundary, preserves point count which is SUPER critical for
        fascicle repositioning
        """

        if mode == ReshapeNerveMode.CIRCLE:
            return self.nerve.to_circle()
        elif mode == ReshapeNerveMode.ELLIPSE:
            return self.nerve.to_ellipse()
        else:
            self.throw(16)

    def reposition_fascicles(self, new_nerve: Nerve, minimum_distance: float = 10, seed: int = None):
        """
        :param new_nerve:
        :param minimum_distance:
        :param seed:
        :return:
        """

        self.plot(final=False, fix_aspect_ratio=True)

        # seed the random number generator
        if seed is not None:
            random.seed(seed)

        def random_permutation(iterable, r: int = None):
            """
            :param iterable:
            :param r: size for permutations (defaults to number of elements in iterable)
            :return: a random permutation of the elements in iterable
            """

            pool = tuple(iterable)
            r = len(pool) if r is None else r
            return tuple(random.sample(pool, r))

        def jitter(first: Fascicle, second: Union[Fascicle, Nerve], rotation: bool = False):
            """
            :param rotation: whether or not to randomly rotate
            :param first:
            :param second:
            :return:
            """

            # create list of fascicles to jitter, defaulting to just the first fascicle
            fascicles_to_jitter = [first]

            # is second argument is a Fascicles, append it to list of fascicles to jitter
            # also, use second argument's type to decide how to find angle between arguments
            if isinstance(second, Fascicle):
                fascicles_to_jitter.append(second)
                angle = first.angle_to(second)
            else:
                _, points = first.min_distance(second, return_points=True)
                angle = Trace.angle(*[point.coords[0] for point in points])

            # will be inverted on each iteration to move in opposite directions
            factor = -1
            for f in fascicles_to_jitter:
                step_scale = 1

                # if the second elements is a Fascicle, and this fascicle is within the other, grow step size
                # this helps fascicles that were moved into others move out quickly
                if isinstance(second, Fascicle) and [f.outer.within(h.outer) for h in (first, second) if h is not f][0]:
                    step_scale *= -20

                # find random step magnitude and build a step vector from that
                step_magnitude = random.random() * minimum_distance
                step = list(np.array([np.cos(angle), np.sin(angle)]) * step_magnitude)

                # apply rigid transformations
                f.shift([step_scale * factor * item for item in step] + [0])
                if rotation:
                    f.rotate(factor * ((random.random() * 2) - 1) * (2 * np.pi) / 100)

                # if just moved out of nerve, move back in
                if not f.within_nerve(new_nerve):
                    f.shift([step_scale * -factor * item for item in step] + [0])

                # invert factor for next fascicle
                factor *= -1

        # Initial shift - proportional to amount of change in the nerve boundary and distance of
        # fascicle centroid from nerve centroid

        for i, fascicle in enumerate(self.fascicles):
            # print('fascicle {}'.format(i))

            fascicle_centroid = fascicle.centroid()
            new_nerve_centroid = new_nerve.centroid()
            r_fascicle_initial = LineString([new_nerve_centroid, fascicle_centroid])

            r_mean = new_nerve.mean_radius()
            r_fasc = r_fascicle_initial.length
            a = 3  # FIXME:
            exterior_scale_factor = a * (r_mean / r_fasc)
            exterior_line: LineString = scale(r_fascicle_initial,
                                              *([exterior_scale_factor] * 3),
                                              origin=new_nerve_centroid)

            # plt.plot(*new_nerve_centroid, 'go')
            # plt.plot(*fascicle_centroid, 'r+')
            # new_nerve.plot()
            # plt.plot(*np.array(exterior_line.coords).T)
            # plt.show()

            new_intersection = exterior_line.intersection(new_nerve.polygon().boundary)
            old_intersection = exterior_line.intersection(self.nerve.polygon().boundary)
            # nerve_change_vector = LineString([new_intersection.coords[0], old_intersection.coords[0]])

            # plt.plot(*np.array(nerve_change_vector.coords).T)
            # self.nerve.plot()
            # new_nerve.plot()

            # get radial vector to new nerve trace
            r_new_nerve = LineString([new_nerve_centroid, new_intersection.coords[0]])

            # get radial vector to FIRST coordinate intersection of old nerve trace
            if isinstance(old_intersection, Point):  # simple Point geometry
                r_old_nerve = LineString([new_nerve_centroid, old_intersection.coords[0]])
            else:  # more complex geometry (MULTIPOINT)
                r_old_nerve = LineString([new_nerve_centroid, list(old_intersection)[0].coords[0]])

            fascicle_scale_factor = (r_new_nerve.length/r_old_nerve.length) * 0.8

            # TODO: nonlinear scaling of fascicle_scale_factor
            # if fascicle_scale_factor > 1:
            #     fascicle_scale_factor **= exponent

            r_fascicle_final = scale(r_fascicle_initial,
                                     *([fascicle_scale_factor] * 3),
                                     origin=new_nerve_centroid)

            shift = list(np.array(r_fascicle_final.coords[1]) - np.array(r_fascicle_initial.coords[1])) + [0]
            fascicle.shift(shift)
            # fascicle.plot('r-')

            # attempt to move in direction of closest boundary
            _, min_dist_intersection_initial = fascicle.centroid_distance(self.nerve, return_points=True)
            _, min_dist_intersection_final = fascicle.centroid_distance(new_nerve, return_points=True)
            min_distance_length = LineString([min_dist_intersection_final[1].coords[0],
                                              min_dist_intersection_initial[1].coords[0]]).length
            min_distance_vector = np.array(min_dist_intersection_final[1].coords[0]) - \
                                  np.array(min_dist_intersection_initial[1].coords[0])
            min_distance_vector *= 1

            # fascicle.shift(list(-min_distance_vector) + [0])

        # NOW, set the slide's actual nerve to be the new nerve
        self.nerve = new_nerve

        # Jitter
        iteration = 0
        print('start random jitter')
        while not self.validation(specific=False, die=False, tolerance=None):

            # USER OUTPUT
            iteration += 1
            plt.figure()
            self.plot(final=True, fix_aspect_ratio=True, inner_format='r-')
            plt.title('iteration: {}'.format(iteration - 1))
            plt.show()
            print('\titeration: {}'.format(iteration))

            # loop through random permutation
            for fascicle in random_permutation(self.fascicles):
                while fascicle.min_distance(self.nerve) < minimum_distance:
                    jitter(fascicle, self.nerve)

                for other_fascicle in random_permutation(filter(lambda item: item is not fascicle, self.fascicles)):
                    while any([fascicle.min_distance(other_fascicle) < minimum_distance,
                               fascicle.outer.within(other_fascicle.outer)]):
                        jitter(fascicle, other_fascicle)

        print('end random jitter')

        # validate again just for kicks
        self.validation()

        self.plot('CHANGE', inner_format='r-')

    def plot(self, title: str = None, final: bool = True, inner_format: str = 'b-', fix_aspect_ratio: bool = False):
        """
        Quick util for plotting the nerve and fascicles
        :param title: optional string title for plot
        :param final: optional, if False, will not show or add title (if comparisons are being overlayed)
        :param inner_format: optional format for inner traces of fascicles
        :param fix_aspect_ratio: optional, if True, will set equal aspect ratio
        """

        # if not the last graph plotted
        if fix_aspect_ratio:
            plt.axes().set_aspect('equal', 'datalim')

        # loop through constituents and plot each
        self.nerve.plot(plot_format='g-')
        for fascicle in self.fascicles:
            fascicle.plot(inner_format)

        # if final plot, add title and show
        if final:
            if title is not None:
                plt.title(title)

            plt.show()

    def scale(self, factor: float):
        """
        :param factor:
        :return:
        """

        center = list(self.nerve.centroid())

        self.nerve.scale(factor, center)
        for fascicle in self.fascicles:
            fascicle.scale(factor, center)

    def rotate(self, angle: float):
        """
        :param angle:
        :return:
        """

        center = list(self.nerve.centroid())

        self.nerve.rotate(angle, center)
        for fascicle in self.fascicles:
            fascicle.rotate(angle, center)

    def write(self, mode: WriteMode, path: str):
        """
        :param mode:
        :param path: root path of slide
        """

        start = os.getcwd()

        if not os.path.exists(path):
            self.throw(26)
        else:
            # go to directory to write to
            os.chdir(path)

            # keep track of starting place
            sub_start = os.getcwd()

            # write nerve and fascicles
            for items, folder in [([self.nerve], 'nerve'), (self.fascicles, 'fascicles')]:
                # build path if not already existing
                if not os.path.exists(folder):
                    os.makedirs(folder)
                os.chdir(folder)

                # write all items (give filename as i (index) without the extension
                for i, item in enumerate(items):

                    if isinstance(item, Nerve):
                        item.write(mode, os.path.join(os.getcwd(), str(i)))
                    else:
                        # start to keep track of position file structure
                        index_start_folder = os.getcwd()

                        # go to indexed folder for each fascicle
                        index_folder = str(i)
                        if not os.path.exists(index_folder):
                            os.makedirs(index_folder)
                        os.chdir(index_folder)
                        item.write(mode, os.getcwd())

                        # go back up a folder
                        os.chdir(index_start_folder)

                # change directory back to starting place
                os.chdir(sub_start)

        os.chdir(start)
