#!/usr/bin/env python3.7

"""
File:       slide.py
Author:     Jake Cariello
Created:    July 24, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""
import itertools
from typing import List, Tuple, Union
from shapely.geometry import LineString
from shapely.affinity import scale
import numpy as np
import random
import matplotlib.pyplot as plt

# really weird syntax is required to directly import the class without going through the pesky init
from .fascicle import Fascicle
from .nerve import Nerve
from src.utils import *


class Slide(Exceptionable, Configurable):

    def __init__(self, fascicles: List[Fascicle], nerve: Nerve, master_config: dict, exception_config: list):

        # init superclasses
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.nerve: Nerve = nerve
        self.fascicles: List[Fascicle] = fascicles

        # do validation (default is specific!)
        self.validation()

    def validation(self, specific: bool = True):
        if specific:
            if self.fascicle_fascicle_intersection():
                self.throw(10)

            if self.fascicle_nerve_intersection():
                self.throw(11)

            if self.fascicles_outside_nerve():
                self.throw(12)
        else:
            if any([self.fascicle_fascicle_intersection(),
                    self.fascicle_nerve_intersection(),
                    self.fascicles_outside_nerve()]):
                self.throw(13)

    def fascicle_fascicle_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects another fascicle, otherwise False
        """
        pairs: List[Tuple[Fascicle]] = list(itertools.combinations(self.fascicles, 2))
        return any([pair[0].intersects(pair[1]) for pair in pairs])

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

    def to_circle(self):
        """
        :return:
        """
        self.nerve = self.nerve.to_circle()

    def to_ellipse(self):
        """
        :return:
        """
        self.nerve = self.nerve.to_ellipse()

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

    def reshaped_nerve(self, mode: ReshapeNerveMethod) -> Nerve:
        """
        :param mode:
        :return:
        """
        if mode == ReshapeNerveMethod.CIRCLE:
            return self.nerve.deepcopy().to_circle()
        else:
            self.throw(16)

    def reposition_fascicles(self, new_nerve: Nerve):
        """
        :return: Shifted fascicles (which contain traces) within the final shape of the nerve
        """

        minimum_distance = 10

        def random_permutation(iterable, r=None):
            "Random selection from itertools.permutations(iterable, r)"
            pool = tuple(iterable)
            r = len(pool) if r is None else r
            return tuple(random.sample(pool, r))

        def jitter(first: Fascicle, second: Union[Fascicle, Nerve]):

            if isinstance(second, Fascicle):
                angle = first.angle_to(second)

                step_magnitude =
            else:  # second must be a Nerve
                pass


        # Initial shift - proportional to amount of change in the nerve boundary and distance of
        # fascicle centroid from nerve centroid

        for fascicle in self.fascicles:
            fascicle_centroid = fascicle.centroid()
            new_nerve_centroid = new_nerve.centroid()
            r_fascicle_initial = LineString([new_nerve_centroid, fascicle_centroid])

            r_mean = new_nerve.mean_radius()
            r_fasc = r_fascicle_initial.length
            a = 2 #FIXME
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
            nerve_change_vector = LineString([new_intersection.coords[0], old_intersection.coords[0]])

            # plt.plot(*np.array(nerve_change_vector.coords).T)
            # self.nerve.plot()
            # new_nerve.plot()

            r_new_nerve = LineString([new_nerve_centroid, new_intersection.coords[0]])
            r_old_nerve = LineString([new_nerve_centroid, old_intersection.coords[0]])

            fascicle_scale_factor = r_new_nerve.length/r_old_nerve.length

            r_fascicle_final = scale(r_fascicle_initial,
                                     *([fascicle_scale_factor] * 3),
                                     origin=new_nerve_centroid)

            shift = list(np.array(r_fascicle_final.coords[1]) - np.array(r_fascicle_initial.coords[1])) + [0]
            fascicle.shift(shift)
            # fascicle.plot('r-')

        # Jitter
        while self.validation(specific=False):
            for fascicle in random_permutation(self.fascicles):
                while fascicle.min_distance(new_nerve) < minimum_distance:
                    jitter(fascicle, new_nerve)

                for other_fascicle in random_permutation(filter(lambda item: item is not fascicle, self.fascicles)):
                    while fascicle.min_distance(other_fascicle) < minimum_distance:
                        jitter(fascicle, other_fascicle)

        # plt.show()




            #v_ext_fasc = LineString([point_ext, new_nerve_centroid])
            #nerve_int = v_ext_fasc.intersection(new_nerve.polygon().boundary)

            # line.intersection po

            # v_init_fasc.length = self.nerve.mean_radius()*5
            # v_init_fasc.intersection(new_nerve.polygon()).coords[0]

        # While overlap == True - loop
        self.validation()


# slide: Slide
# slide.reposition_fascicles(slide.reshaped_nerve(ReshapeNerveMethod.CIRCLE))
