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

    TODO: check if inners are overlapping

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
        # create path representing the outer Trace shape
        outer_path = pth.Path([tuple(point) for point in outer.points[:, :2]])
        # loop through all inner traces
        for inner in inners:
            # check that all points in this Trace are within the outer path
            if not all(outer_path.contains_points([tuple(point) for point in inner.points[:, :2]])):
                self.throw(8)

# # might use this code for checking if points are within elliptical nerve
# # get bounding ellipse parameters
#
# ((h, k), (a, b)) = outer.ellipse()
#
# for point in inner.points:
#     (x, y, _) = tuple(point)
#     if ((math.pow((x - h), 2) // math.pow(a, 2)) + (math.pow((y - k), 2) // math.pow(b, 2))) < 1:
#         self.throw()
