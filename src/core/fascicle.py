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
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

from .trace import Trace
from .nerve import Nerve
from src.utils import Exceptionable, SetupMode


class Fascicle(Exceptionable):

    def __init__(self, exception_config, outer: Trace, inners: List[Trace] = None, outer_scale: float = None):
        """
        :param outer_scale:
        :param exception_config: existing data already loaded form JSON (hence SetupMode.OLD)
        :param inners: list of inner Traces (i.e. endoneuriums)
        :param outer: single outer Trace (i.e. perineurium)
        """

        # set up superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        # use for scaling if no outer trace (i.e. ONLY outer trace has been set)
        self.outer_scale = outer_scale

        self.inners = inners
        self.outer = outer

        if inners is None:
            self.__endoneurium_setup(outer_scale)
        else:
            # ensure all inner Traces are actually inside outer Trace
            if any([not inner.within(outer) for inner in inners]):
                self.throw(8)

            # ensure no Traces intersect (and only check each pair of Traces once)
            pairs: List[Tuple[Trace]] = list(itertools.combinations(self.all_traces(), 2))
            if any([pair[0].intersects(pair[1]) for pair in pairs]):
                self.throw(9)

    def intersects(self, other: Union['Fascicle', Nerve]):
        """
        :param other: the other Fascicle or Nerve to check
        :return: True if a Trace intersection is found
        """
        if isinstance(other, Fascicle):
            return self.outer.intersects(other.outer)
        else:  # other must be a Nerve
            return self.outer.intersects(other)

    def min_distance(self, other: Union['Fascicle', Nerve]):
        """
        :param other: other Fascicle or Nerve to check
        :return: minimum straight-line distance between self and other
        """
        if isinstance(other, Fascicle):
            return self.outer.min_distance(other.outer)
        else:  # other must be a Nerve
            return self.outer.min_distance(other)

    def centroid_distance(self, other: Union['Fascicle', Nerve]):
        """
        :param other: other Fascicle or Nerve to check
        :return: minimum straight-line distance between self and other
        """
        if isinstance(other, Fascicle):
            return self.outer.centroid_distance(other.outer)
        else:  # other must be a Nerve
            return self.outer.centroid_distance(other)

    def within_nerve(self, nerve: Nerve) -> bool:
        """
        :param nerve:
        :return:
        """
        return self.outer.within(nerve)

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

    def centroid(self):
        """
        :return: centroid of outer trace (ellipse method)
        """
        return self.outer.centroid()

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

    def mean_radius(self):
        """
        :return:
        """
        return self.outer.mean_radius()

    def angle_to(self, other: Union['Fascicle', Nerve]):
        """
        :param other:
        :return:
        """
        if isinstance(other, Fascicle):
            return self.outer.angle_to(other.outer)
        else:  # must be Nerve
            return self.outer.angle_to(other)



    def plot(self):
        self.outer.plot()
        for inner in self.inners:
            inner.plot('b-')

    def deepcopy(self):
        return deepcopy(self)

    def __endoneurium_setup(self, factor: float):

        # check that outer scale is provided
        if self.outer_scale is None:
            self.throw(14)

        if factor < 1:
            self.throw(15)

        # set single inner trace
        self.inners = [self.outer.deepcopy()]

        # scale up outer trace
        self.outer.scale(factor)

    @staticmethod
    def list_from_contours_compiled(cnts: list, hierarchy: np.ndarray, exception_config,
                           plot: bool = False, scale: float = None) -> List['Fascicle']:
        """
        Example usage:
            (cnts, hier) = cv2.findContours( ... )
            fascicles = Fascicle.list_from_contours(cnts, hier[0])
        Note: use hier[0] so that hierarchy argument is only 2D

        Each row of hierarchy corresponds to the same 0-based index contour in cnts
        For all elements, if the associated feature is not present/applicable, the value will be negative (-1).
        Interpreting elements of each row (numbers refer to indices, NOT values):
            0: index of previous contour at same hierarchical level
            1: index of next contour at same hierarchical level
            2: index of first child contour
            3: index of parent contour

        This algorithm is expecting a max hierarchical depth of 2 (i.e. one level each of inners and outers)

        :param scale:
        :param plot:
        :param exception_config:
        :param cnts: contours, as returned by cv2.findContours
        :param hierarchy: hierarchical structure, as returned by cv2.findContours
        :return: list of Fascicles derived from the hierarchy (and associated contours)
        """

        # helper method
        def inner_indices(outer_index: int, hierarchy: np.ndarray) -> List[int]:
            indices: List[int] = []

            # get first child index
            start_index = hierarchy[outer_index][2]

            # loop while updating last index
            next_index = start_index
            while next_index >= 0:
                # set current index and append to list
                current_index = next_index
                indices.append(current_index)

                # get next index and break if less than one (i.e. there are only "previous" indices)
                next_index = hierarchy[current_index][0]

            return indices

        # create list (will be returned at end of method)
        fascicles: List[Fascicle] = []

        if plot:
            plt.axes().set_aspect('equal', 'datalim')

        # loop through all rows... not filtering in one line b/c want to preserve indices
        for i, row in enumerate(hierarchy):
            # if top level (no parent)
            if row[3] < 0:
                outer_contour = cnts[i]
                inner_contours = [cnts[index] for index in inner_indices(i, hierarchy)]

                # if no inner traces, this is endoneurium only, so set inner and outer
                # if len(inner_contours) == 0:
                #     inner_contours.append(outer_contour)

                # build Traces from contours
                outer_trace = Trace(outer_contour[:, 0, :], exception_config)
                inner_traces = [Trace(cnt[:, 0, :], exception_config) for cnt in inner_contours]

                # add fascicle to list (with or without inner trace)
                if len(inner_traces) > 0:
                    fascicles.append(Fascicle(exception_config, outer_trace, inner_traces))
                else:
                    fascicles.append(Fascicle(exception_config, outer_trace, outer_scale=scale));

                if plot:
                    fascicles[i].plot()

        if plot:
            plt.show()

        return fascicles

    @staticmethod
    def list_from_contours_separate(inner_cnts: list, outer_cnts: list, hierarchy: np.ndarray, exception_config,
                                    plot: bool = False, scale: float = None) -> List['Fascicle']:
        """
        :param inner_cnts:
        :param outer_cnts:
        :param hierarchy:
        :param exception_config:
        :param plot:
        :param scale:
        :return:
        """

        inners = [Trace(cnt[:, 0, :], exception_config) for cnt in inner_contours]

        fascicles: List[Fascicle] = []

        for inner_cnt in inner_cnts:
            distances = []
