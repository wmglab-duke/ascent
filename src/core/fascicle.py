#!/usr/bin/env python3.7

"""Defines Fascicle class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""


import itertools
import os
from copy import deepcopy
from typing import Union

import cv2
import matplotlib.pyplot as plt
import numpy as np

from src.utils import MorphologyError, WriteMode

from .nerve import Nerve
from .trace import Trace


class Fascicle:
    """Class which uses Trace objects to define a fascicle.

    A fascicle is a bundle of axons and their myelin sheaths.
    Each fascicle can have multiple inners, but only a single outer.
    """

    def __init__(
        self,
        outer: Trace,
        inners: list[Trace] = None,
    ):
        """Initialize the Fascicle object.

        Fascicle can be created with either: option 1: an outer and any
        number of inners option 2: an inner, which is passed in as an outer
        argument, and scaled out to make a virtual outer option 3: ... tbd.

        :param inners: list of inner Traces (i.e. endoneuriums)
        :param outer: single outer Trace (i.e. perineurium)
        """
        # intialize scale attribute
        self.outer_scale = None

        # initialize constituent traces
        self.inners: list[Trace] = inners if inners is not None else []
        self.outer: Trace = outer

        if len(self.inners) > 0:
            self.validate()

    def validate(self):
        """Perform validation checks on traces.

        :raises MorphologyError: if validation fails
        """
        # ensure all inner Traces are actually inside outer Trace
        if any(not inner.within(self.outer) for inner in self.inners):
            raise MorphologyError("Not all inner Traces fall within outer Trace")
        # ensure no Traces intersect (and only check each pair of Traces once)
        pairs: list[tuple[Trace]] = list(itertools.combinations(self.all_traces(), 2))
        if any(pair[0].intersects(pair[1]) for pair in pairs):
            self.plot()
            plt.axes().set_aspect('equal')
            plt.show()
            raise MorphologyError("Intersecting traces found")

    def intersects(self, other: Union['Fascicle', Nerve]):
        """Check if the fascicle outer intersects with another fascicle or nerve boundary.

        :param other: the other Fascicle or Nerve to check
        :return: True if a Trace intersection is found
        """
        if isinstance(other, Fascicle):
            return self.outer.intersects(other.outer)
        # otherwise must be a Nerve
        return self.outer.intersects(other)

    def min_distance(self, other: Union['Fascicle', Nerve]) -> float | tuple:
        """Calculate the minimum distance between the fascicle and another fascicle or nerve boundary.

        :param other: other Fascicle or Nerve to check
        :return: minimum straight-line distance between self and other
        """
        if isinstance(other, Fascicle):
            return self.outer.min_distance(other.outer)
        # otherwise must be a Nerve
        return self.outer.min_distance(other)

    def centroid_distance(self, other: Union['Fascicle', Nerve]):
        """Calculate the distance between this fascicle's centroid and another centroid.

        :param other: other Fascicle or Nerve to check
        :return: minimum straight-line distance between self and other
        """
        if isinstance(other, Fascicle):
            return self.outer.centroid_distance(other.outer)
        # otherwise must be a Nerve
        return self.outer.centroid_distance(other)

    def within_nerve(self, nerve: Nerve) -> bool:
        """Check if the fascicle is within the nerve boundary.

        :param nerve: Nerve object to check
        :return: returns boolean, true if fascicle is within the nerve, false if fascicle is not in the nerve
        """
        return self.outer.within(nerve)

    def shift(self, vector):
        """Apply a vector shift to all constituent traces.

        :param vector: shift to apply to all Traces in the fascicle
        """
        for trace in self.all_traces():
            trace.shift(vector)

    def all_traces(self) -> list[Trace]:
        """Get all constituent traces.

        :return: list of all traces
        """
        return list(self.inners) + [self.outer]

    def reset_transform(self):
        """Reset the affine transformation trackers for all traces in the fascicle."""
        for trace in self.all_traces():
            trace.reset_transform()

    def centroid(self) -> tuple[float, float]:
        """Get the centroid of the outer trace.

        :return: centroid of outer trace (ellipse method)
        """
        return self.outer.centroid()

    def area(self):
        """Get the area of the outer trace.

        :return: area of outer trace
        """
        return self.outer.area()

    def ellipse(self):
        """Get a best-fit ellipse for the outer trace.

        :return: ellipse fit of outer trace (see Trace.ellipse for return format/type)
        """
        return self.outer.ellipse()

    def mean_radius(self):
        """Get the mean radius of the outer trace.

        :return: mean radius of outer trace
        """
        return self.outer.mean_radius()

    def angle_to(self, other: Union['Fascicle', Nerve]):
        """Calculate the centroid angle between the fascicle and another fascicle or nerve boundary.

        :param other: type Trace
        :return: returns the CCW angle to the other trace based on self and other's centroids
        """
        if isinstance(other, Fascicle):
            return self.outer.angle_to(other.outer)
        # otherwise must be Nerve
        return self.outer.angle_to(other)

    def plot(
        self,
        plot_format: str = 'b-',
        color: tuple[float, float, float, float] | list[tuple[float, float, float, float]] = None,
        ax: plt.Axes = None,
        outer_flag=True,
        inner_index_start: int = None,
        line_kws=None,
    ):
        """Plot the fascicle.

        :param line_kws: keyword arguments to pass to matplotlib.pyplot.plot
        :param outer_flag: whether to plot the outer trace
        :param inner_index_start: index of first inner trace to plot
        :param ax: axes to plot on
        :param color: List of colors to plot the inners with. If None, inners are not filled in.
            The form of each item in the list should be a color specification acceptable to matplotlib.
        :param plot_format: outers automatically black, plot_format only affects inners
        :raises ValueError: if color is not None and len(color) != len(inners)
        """
        if ax is None:
            ax = plt.gca()

        if outer_flag:
            self.outer.plot(ax=ax, line_kws=line_kws)

        if color is not None:
            if len(self.inners) != len(color):
                raise ValueError("Length of fascicle colors list must match number of fascicle inners.")
        else:
            color = [None] * len(self.inners)

        for i, (inner, c) in enumerate(zip(self.inners, color)):
            inner.plot(plot_format, color=c, ax=ax, line_kws=line_kws)
            if inner_index_start is not None:
                ax.text(*inner.centroid(), s=str(i + inner_index_start), ha='center', va='center')

    def deepcopy(self):
        """Deepcopy the fascicle.

        A deepcopy is necessary to avoid modifying the original object
        and other objects (Traces) it contains when modifying the copy.

        :return: creates a new place in memory for the Trace. See: https://docs.python.org/2/library/copy.html
        """
        return deepcopy(self)

    def scale(self, factor: float, center: list[float] = None):
        """Scale the fascicle by a factor.

        :param factor: scale factor
        :param center: [x,y]
        """
        if center is None:
            center = list(self.centroid())

        for trace in self.all_traces():
            trace.scale(factor, center)

    def rotate(self, angle: float, center: list[float] = None):
        """Rotate the fascicle by an angle.

        :param angle: angle in radians
        :param center: [x,y]
        """
        if center is None:
            center = list(self.centroid())

        for trace in self.all_traces():
            trace.rotate(angle, center)

    def smallest_trace(self) -> Trace:
        """Find the smallest trace in the fascicle.

        :return: the trace with the smallest area
        """
        areas = np.array([trace.area() for trace in self.all_traces()])
        return np.array(self.all_traces())[np.where(areas == np.min(areas))][0]

    def perineurium_setup(self, fit: dict):
        """Take inners which were passed in as outers, and generate the perineurium.

        :param fit: a dictionary with the values describing a linear relationship
            between fascicle size and perineurium thickness
        :raises ValueError: if fit is None
        :raises MorphologyError: if outers already exist
        """
        if fit is None:
            raise ValueError("Cannot generate perineurium without fit parameters.")

        self.outer_scale = fit

        # can only generate perineurium if there are no inners
        if len(self.inners) != 0:
            raise MorphologyError(
                "Tried to generate perineurium, but fascicle already has an outer and at least one inner."
            )

        # set single inner trace
        self.inners = [self.outer.deepcopy()]

        # scale up outer trace
        self.outer.offset(fit=fit)

        # check for any bad traces
        self.validate()

    @staticmethod
    def to_list(
        inner_img_path: str,
        outer_img_path: str,
        contour_mode,
        z: float = 0,
    ) -> list['Fascicle']:
        """Convert a set of inner and outer images to a list of fascicles.

        :param z: z-coordinate of the slide this fascicle is on
        :param outer_img_path: path to outer image, if None, only inners are returned
            (stored as outers until perineurium is generated)
        :param inner_img_path: path to inner image
        :param contour_mode: contour mode to use for cv2.findContours
        :return: list of Fascicles derived from the image(s)
        """

        def build_traces(path: str) -> list[Trace]:
            # default findContours params
            params = [cv2.RETR_TREE, contour_mode.value]
            # default findContours params

            img = np.flipud(cv2.imread(path, -1))

            if len(img.shape) > 2 and img.shape[2] > 1:
                img = img[:, :, 0]

            # find points of traces (hierarchy is IGNORED! ... see that "_")
            contours, _ = cv2.findContours(img, *params)

            # build list of traces
            return [Trace([item + [z] for item in contour[:, 0, :]]) for contour in contours]

        if outer_img_path is None:
            # inners only case, set each inner as an outer
            outers = np.array(build_traces(inner_img_path))
        else:
            # build traces list for inner and outer image paths
            inners, outers = (np.array(build_traces(path)) for path in (inner_img_path, outer_img_path))

            # create empty list to hold the outer traces that inners correspond to
            inner_correspondence: list[int] = []

            # iterate through all inner traces and assign outer index
            for inner in inners:
                mask = [inner.within(outer) for outer in outers]
                inner_correspondence.append(np.where(mask)[0][0])

        # create empty list to hold fascicles
        fascicles: list[Fascicle] = []

        # iterate through each outer and build fascicles
        for index, outer in enumerate(outers):
            if outer_img_path is not None:
                # get all the inner traces that correspond to this outer
                inners_corresponding = inners[np.where(np.array(inner_correspondence) == index)]

                # add fascicle!
                fascicles.append(Fascicle(outer, inners_corresponding))
            else:
                # inners only case
                fascicles.append(Fascicle(outer))

        return fascicles

    def write(self, mode: WriteMode, path: str):
        """Write the fascicle traces to files for import into COMSOL.

        :param mode: Sectionwise... for now
        :param path: root path of fascicle trace destination
        :raises OSError: if path does not exist
        """
        start = os.getcwd()

        if not os.path.exists(path):
            raise OSError("Write directory does not exist.")

        # go to directory to write to
        os.chdir(path)

        # keep track of starting place
        sub_start = os.getcwd()

        # write outer and inners
        for items, folder in [([self.outer], 'outer'), (self.inners, 'inners')]:
            os.makedirs(folder, exist_ok=True)
            os.chdir(folder)

            # write all items (give filename as i (index) without the extension
            for i, item in enumerate(items):
                item.write(mode, os.path.join(os.getcwd(), str(i)))

            # change directory back to starting place
            os.chdir(sub_start)

        os.chdir(start)

    def morphology_data(self):
        """Get the morphology data for the fascicle.

        :return: a dictionary with the morphology data
        """
        inners = [
            {
                "area": inner.area(),
                "x": inner.ellipse()[0][0],
                "y": inner.ellipse()[0][1],
                "a": inner.ellipse()[1][0],
                "b": inner.ellipse()[1][1],
                "angle": inner.ellipse()[2],
            }
            for inner in self.inners
        ]
        outer = {
            "area": self.outer.area(),
            "x": self.outer.ellipse()[0][0],
            "y": self.outer.ellipse()[0][1],
            "a": self.outer.ellipse()[1][0],
            "b": self.outer.ellipse()[1][1],
            "angle": self.outer.ellipse()[2],
        }

        return {"outer": outer, "inners": inners}
