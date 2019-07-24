#!/usr/bin/env python3.7

"""
File:       Fascicle.py
Author:     Jake Cariello
Created:    July 24, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""

# import math
import itertools
from typing import List, Tuple

from src.core import Trace, Trace as Nerve
from src.utils import Exceptionable, SetupMode


class Fascicle(Exceptionable):

    def __init__(self, exception_config, inners: List[Trace], outer: Trace):
        """
        :param exception_config: existing data already loaded form JSON (hence SetupMode.OLD)
        :param inners: list of inner Traces (i.e. endoneuriums)
        :param outer: single outer Trace (i.e. perineurium)
        """

        # set up superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.inners = inners
        self.outer = outer

        # ensure all inner Traces are actually inside outer Trace
        if any([inner for inner in inners if inner.is_inside(outer)]):
            self.throw(8)

        # ensure no Traces intersect (and only check each pair of Traces once)
        self.pairs: List[Tuple[Trace]] = list(itertools.combinations(self.all_traces(), 2))
        if any([pair[0].intersects(pair[1]) for pair in self.pairs]):
            self.throw(9)

    def intersects_fascicle(self, other: 'Fascicle') -> bool:
        """
        :param other: the other Fascicle to check
        :return: True if the outer traces of the Fascicles intersect
        """
        return self.outer.intersects(other.outer)

    def intersects_nerve(self, nerve: Nerve) -> bool:
        """
        :param nerve: the Nerve to check
        :return: True if the self.outer Traces intersects the single Trace of nerve
        """
        return self.outer.intersects(nerve)

    def is_inside_nerve(self, nerve: Nerve) -> bool:
        """
        :param nerve:
        :return:
        """
        return self.outer.is_inside(nerve)

    def shift(self, vector):
        """
        :param vector:
        :return:
        """
        for trace in self.all_traces():
            trace.shift(vector)

    def all_traces(self) -> List[Trace]:
        """
        :return: list of all traces
        """
        return self.inners + [self.outer]

    def ellipse_centroid(self):
        """
        :return: centroid of outer trace (ellipse method)
        """
        return self.outer.ellipse_centroid()

    def mean_centroid(self):
        """
        :return: centroid of outer trace (mean method)
        """
        return self.outer.mean_centroid()

    def area(self):
        """
        :return: area of outer trace
        """
        return self.outer.area()

    def ellipse(self):
        """
        :return: ellipse fit of outer trace (see Trace.ellipse for return format/type)
        """
        return self.outer.ellipse()


# # might use this code for checking if points are within elliptical nerve
# # get bounding ellipse parameters
#
# ((h, k), (a, b)) = outer.ellipse()
#
# for point in inner.points:
#     (x, y, _) = tuple(point)
#     if ((math.pow((x - h), 2) // math.pow(a, 2)) + (math.pow((y - k), 2) // math.pow(b, 2))) < 1:
#         self.throw()
