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
import cv2

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

        # ensure all inner Traces are actually inside outer Trace
        if any([not inner.within(outer) for inner in self.inners]):
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

    def min_distance(self, other: Union['Fascicle', Nerve], return_points: bool = False):
        """
        :param return_points:
        :param other: other Fascicle or Nerve to check
        :return: minimum straight-line distance between self and other
        """
        if isinstance(other, Fascicle):
            return self.outer.min_distance(other.outer, return_points=return_points)
        else:  # other must be a Nerve
            return self.outer.min_distance(other, return_points=return_points)

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
        return list(self.inners) + [self.outer]

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

    def plot(self, plot_format: str = 'b-'):
        self.outer.plot()
        for inner in self.inners:
            inner.plot(plot_format)

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
    def compiled_to_list(img_path: str, exception_config,
                         plot: bool = False, scale: float = None) -> List['Fascicle']:
        """
        Example usage:
            fascicles = Fascicle.compiled_to_list(my_image_path, ... )

        Each row of hierarchy corresponds to the same 0-based index contour in cnts
        For all elements, if the associated feature is not present/applicable, the value will be negative (-1).
        Interpreting elements of each row (numbers refer to indices, NOT values):
            0: index of previous contour at same hierarchical level
            1: index of next contour at same hierarchical level
            2: index of first child contour
            3: index of parent contour

        This algorithm is expecting a max hierarchical depth of 2 (i.e. one level each of inners and outers)

        :param img_path:
        :param scale:
        :param plot:
        :param exception_config:
        :return: list of Fascicles derived from the single image
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

        # read image and flip
        img = np.flipud(cv2.imread(img_path, -1))

        # get contours and hierarchy
        cnts, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # create list (will be returned at end of method)
        fascicles: List[Fascicle] = []

        if plot:
            plt.axes().set_aspect('equal', 'datalim')

        # loop through all rows... not filtering in one line b/c want to preserve indices
        for i, row in enumerate(hierarchy[0]):
            # if top level (no parent)
            if row[3] < 0:
                outer_contour = cnts[i]
                inner_contours = [cnts[index] for index in inner_indices(i, hierarchy[0])]

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
                    fascicles.append(Fascicle(exception_config, outer_trace, outer_scale=scale))

                if plot:
                    fascicles[i].plot()

        if plot:
            plt.show()

        return fascicles

    @staticmethod
    def separate_to_list(inner_img_path: str, outer_img_path: str, exception_config,
                         plot: bool = False) -> List['Fascicle']:
        """
        Example usage:
            fascicles = Fascicle.separate_to_list(my_inner_image_path,
                                                  my_outer_image_path, ... )

        :param outer_img_path:
        :param inner_img_path:
        :param exception_config:
        :param plot:
        :return: list of Fascicles derived from the two images
        """
        def build_traces(path: str) -> List[Trace]:
            # default findContours params
            params = [cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE]
            # default findContours params
            img = np.flipud(cv2.imread(path, -1))
            # find points of traces (hierarchy is IGNORED! ... see that "_")
            contours, _ = cv2.findContours(img, *params)
            # build list of traces
            return [Trace(contour[:, 0, :], exception_config) for contour in contours]

        # build traces list for inner and outer image paths
        inners, outers = (np.array(build_traces(path)) for path in (inner_img_path, outer_img_path))

        # create empty list to hold the outer traces that inners correspond to
        inner_correspondence: List[int] = []

        # iterate through all inner traces and assign outer index
        for inner in inners:
            mask = [inner.within(outer) for outer in outers]
            inner_correspondence.append(np.where(mask)[0][0])

        # create empty list to hold fascicles
        fascicles: List[Fascicle] = []

        if plot:
            plt.axes().set_aspect('equal', 'datalim')

        # iterate through each outer and build fascicles
        for index, outer in enumerate(outers):
            # get all the inner traces that correspond to this outer
            inners_corresponding = inners[np.where(np.array(inner_correspondence) == index)]

            # add fascicle!
            fascicles.append(Fascicle(exception_config, outer, inners_corresponding))

            if plot:
                fascicles[index].plot()

        if plot:
            plt.show()

        return fascicles

    @staticmethod
    def inner_to_list(img_path: str, exception_config,
                      plot: bool = False, scale: float = None) -> List['Fascicle']:
        return Fascicle.compiled_to_list(img_path, exception_config, plot, scale)
