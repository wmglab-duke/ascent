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
from typing import List
from matplotlib import path as pth

from src.core import Trace
from src.utils import Exceptionable, SetupMode


class Fascicle(Exceptionable):

    def __init__(self, exception_config, inners: List[Trace], outer: Trace):
        # set up superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.inners = inners
        self.outer = outer

        # validate the inner/outer relationship
        for inner in inners:
            if not self.inside(inner, outer):
                self.throw(8)

    @staticmethod
    def inside(inner: Trace, outer: Trace) -> bool:
        """
        :param inner: the Trace on the inside
        :param outer: the Trace on the outside
        :return: bool indicating whether or not the inner really is inside the outer
        """
        outer_path = pth.Path([tuple(point) for point in outer.points[:, :2]])
        return all(outer_path.contains_points([tuple(point) for point in inner.points[:, :2]]))


# # might use this code for checking if points are within elliptical nerve
# # get bounding ellipse parameters
#
# ((h, k), (a, b)) = outer.ellipse()
#
# for point in inner.points:
#     (x, y, _) = tuple(point)
#     if ((math.pow((x - h), 2) // math.pow(a, 2)) + (math.pow((y - k), 2) // math.pow(b, 2))) < 1:
#         self.throw()
