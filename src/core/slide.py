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
from typing import List, Tuple
from shapely.geometry import LineString
import numpy as np

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

    def reposition_fascicles(self, new_nerve: Nerve):
        """
        :return: Shifted fascicles (which contain traces) within the final shape of the nerve
        """

        for fascicle in self.fascicles:
            v_init_fasc = LineString([fascicle.centroid(), new_nerve.centroid()])
            dy = (v_init_fasc.coords[1, 1] - v_init_fasc.coords[0, 1])
            dx = (v_init_fasc.coords[1, 0] - v_init_fasc.coords[0, 0])
            final = 5 * np.array(dx, dy) #FIXME: standardize at some point
            length = np.sqrt(final[0]**2 + final[1]**2)

            #v_init_fasc.length = self.nerve.mean_radius()*5
            #v_init_fasc.intersection(new_nerve.polygon()).coords[0]

        self.validation()

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



