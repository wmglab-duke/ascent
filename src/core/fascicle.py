#!/usr/bin/env python3.7

"""
File:       fascicle.py
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
from typing import List, Tuple, Union

from .trace import Trace
from .nerve import Nerve
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
        pairs: List[Tuple[Trace]] = list(itertools.combinations(self.all_traces(), 2))
        if any([pair[0].intersects(pair[1]) for pair in pairs]):
            self.throw(9)

    def intersects(self, other: Union['Fascicle', Nerve]):
        """
        I just realized that this would fail to account for the case when "other" is within,
        but not intersecting "self." This is nonsensical though, so not worrying about it for now.

        :param other: the other Fascicle or Nerve to check
        :return: True if a Trace intersection is found
        """
        if isinstance(other, Fascicle):
            return self.outer.intersects(other.outer)
        else:  # other must be a Nerve
            return self.outer.intersects(other)

    def is_inside_nerve(self, nerve: Nerve) -> bool:
        """
        :param nerve:
        :return:
        """
        return self.outer.is_inside(nerve)

    def shift(self, vector):
        """
        :param vector: shift to apply to all Traces in the fascicle
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
