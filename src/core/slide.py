#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""
import itertools
import os
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from src.utils import Exceptionable, NerveMode, ReshapeNerveMode, SetupMode, WriteMode

from .fascicle import Fascicle
from .nerve import Nerve
from .trace import Trace


class Slide(Exceptionable):
    def __init__(
        self,
        fascicles: List[Fascicle],
        nerve: Nerve,
        nerve_mode: NerveMode,
        exception_config: list,
        will_reposition: bool = False,
    ):
        """
        :param fascicles: List of fascicles
        :param nerve: Nerve (effectively is a Trace)
        :param nerve_mode: from Enums, indicates if the nerve exists or not (PRESENT, NOT_PRESENT)
        :param exception_config: pre-loaded configuration data
        :param will_reposition: boolean flag that tells the initializer whether or not it should be validating the
        geometries - if it will be reposition then this is not a concern
        """

        # init superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.nerve_mode = nerve_mode

        self.nerve: Nerve = nerve
        self.fascicles: List[Fascicle] = fascicles

        if not will_reposition:
            self.validation()
        else:
            if self.nerve_mode == NerveMode.NOT_PRESENT:
                self.throw(39)

        self.orientation_point: Optional[Tuple[float, float]] = None
        self.orientation_angle: Optional[float] = None

    def monofasc(self) -> bool:
        return self.nerve_mode == NerveMode.NOT_PRESENT and len(self.fascicles) == 1

    def fascicle_centroid(self) -> Tuple[float, float]:
        area_sum = x_sum = y_sum = 0.0

        for fascicle in self.fascicles:
            x, y = fascicle.centroid()
            area = fascicle.area()

            x_sum += x * area
            y_sum += y * area
            area_sum += area

        return (x_sum / area_sum), (y_sum / area_sum)

    def validation(
        self,
        specific: bool = True,
        die: bool = True,
        tolerance: float = None,
        plotpath=None,
    ) -> bool:
        """
        Checks to make sure nerve geometry is not overlapping itself
        :param specific: if you want to know what made it fail first
        :param die: if non-specific, decides whether or not to throw an error if it fails
        :param tolerance: minimum separation distance for unit you are currently in
        :return: Boolean for True (no intersection) or False (issues with geometry overlap)
        """

        def debug_plot():
            print('Slide validation failed, saving debug sample plot.')
            if plotpath is None:
                return
            plt.figure()
            self.plot(
                final=False,
                fix_aspect_ratio='True',
                axlabel=u"\u03bcm",
                title='Debug sample which failed validation.',
            )
            plt.savefig(plotpath + '/sample_debug')
            plt.clf()
            plt.close()

        if self.fascicles_too_small():
            debug_plot()
            self.throw(146)

        if self.monofasc():
            return True

        if specific:
            if self.fascicle_fascicle_intersection():
                debug_plot()
                self.throw(10)

            if self.fascicle_nerve_intersection():
                debug_plot()
                self.throw(11)

            if self.fascicles_outside_nerve():
                debug_plot()
                self.throw(12)

        else:
            if any(
                [
                    self.fascicle_fascicle_intersection(),
                    self.fascicle_nerve_intersection(),
                    self.fascicles_outside_nerve(),
                    self.fascicles_too_close(tolerance),
                ],
                self.fascicles_too_small(),
            ):
                if die:
                    debug_plot()
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

        if self.monofasc():
            self.throw(41)

        if tolerance is None:
            return False
        else:
            pairs = itertools.combinations(self.fascicles, 2)
            return any([first.min_distance(second) < tolerance for first, second in pairs]) or any(
                [fascicle.min_distance(self.nerve) < tolerance for fascicle in self.fascicles]
            )

    def fascicles_too_small(self) -> bool:
        """
        :return: True if any fascicle has a trace with less than 3 points
        """
        check = []
        for f in self.fascicles:
            check.append(len(f.outer.points) < 3)
            check.extend([len(i.points) < 3 for i in f.inners])
        return any(check)

    def fascicle_fascicle_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects another fascicle, otherwise False
        """

        if self.monofasc():
            self.throw(42)

        pairs = itertools.combinations(self.fascicles, 2)
        return any([first.intersects(second) for first, second in pairs])

    def fascicle_nerve_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects the nerve, otherwise False
        """

        if self.monofasc():
            self.throw(43)

        return any([fascicle.intersects(self.nerve) for fascicle in self.fascicles])

    def fascicles_outside_nerve(self) -> bool:
        """
        :return: True if any fascicle lies outside the nerve, otherwise False
        """

        if self.monofasc():
            self.throw(44)

        return any([not fascicle.within_nerve(self.nerve) for fascicle in self.fascicles])

    def move_center(self, point: np.ndarray):
        """
        :param point: the point of the new slide center
        """

        if self.monofasc():
            # get shift from nerve centroid and point argument
            shift = list(point - np.array(self.fascicles[0].centroid())) + [0]
        else:
            # get shift from nerve centroid and point argument
            shift = list(point - np.array(self.nerve.centroid())) + [0]

            # apply shift to nerve trace and all fascicles
            self.nerve.shift(shift)

        for fascicle in self.fascicles:
            fascicle.shift(shift)

    def reshaped_nerve(self, mode: ReshapeNerveMode, buffer: float = 0.0) -> Nerve:
        """
        :param buffer:
        :param mode: Final form of reshaped nerve, either circle or ellipse
        :return: a copy of the nerve with reshaped nerve boundary, preserves point count which is SUPER critical for
        fascicle repositioning
        """

        if self.monofasc():
            self.throw(45)

        if mode == ReshapeNerveMode.CIRCLE:
            return self.nerve.to_circle(buffer)
        elif mode == ReshapeNerveMode.ELLIPSE:
            return self.nerve.to_ellipse()
        elif mode == ReshapeNerveMode.NONE:
            return self.nerve
        else:
            self.throw(16)

    def plot(
        self,
        title: str = None,
        final: bool = True,
        inner_format: str = 'b-',
        fix_aspect_ratio: bool = True,
        fascicle_colors: List[Tuple[float, float, float, float]] = None,
        ax: plt.Axes = None,
        outers_flag: bool = True,
        inner_index_labels: bool = False,
        show_axis: bool = True,
        axlabel: str = None,
        line_kws=None,
    ):
        """
        Quick util for plotting the nerve and fascicles
        :param show_axis:
        :param inner_index_labels:
        :param outers_flag:
        :param fascicle_colors:
        :param ax:
        :param title: optional string title for plot
        :param final: optional, if False, will not show or add title (if comparisons are being overlayed)
        :param inner_format: optional format for inner traces of fascicles
        :param fix_aspect_ratio: optional, if True, will set equal aspect ratio
        """

        if ax is None:
            ax = plt.gca()

        if not show_axis:
            ax.axis('off')

        # if not the last graph plotted
        if fix_aspect_ratio:
            ax.set_aspect('equal', 'datalim')

        # loop through constituents and plot each
        if not self.monofasc():
            self.nerve.plot(plot_format='k-', ax=ax, linewidth=1.5, line_kws=line_kws)

        out_to_in = []
        inner_ind = 0
        for i, fascicle in enumerate(self.fascicles):
            out_to_in.append([])
            for _inner in fascicle.inners:
                out_to_in[i].append(inner_ind)
                inner_ind += 1

        if fascicle_colors is not None:
            if inner_ind != len(fascicle_colors):
                self.throw(65)
        else:
            fascicle_colors = [None] * inner_ind

        inner_index = 0
        for fascicle_ind, fascicle in enumerate(self.fascicles):
            inners = out_to_in[fascicle_ind]
            color = []
            for inner in inners:
                color.append(fascicle_colors[inner])
            fascicle.plot(
                inner_format,
                color,
                ax=ax,
                outer_flag=outers_flag,
                inner_index_start=inner_index if inner_index_labels else None,
                line_kws=line_kws,
            )
            inner_index += len(fascicle.inners)

        if title is not None:
            ax.title.set_text(title)

        if axlabel is not None:
            ax.set_xlabel(axlabel)
            ax.set_ylabel(axlabel)

        # if final plot, show
        if final:
            plt.show()

    def scale(self, factor: float):
        """
        :param factor: scale factor, only knows how to scale around its own centroid
        """

        if self.monofasc():
            center = list(self.fascicles[0].centroid())
        else:
            center = list(self.nerve.centroid())
            self.nerve.scale(factor, center)

        for fascicle in self.fascicles:
            fascicle.scale(factor, center)

    def smooth_traces(self, n_distance, i_distance):
        """
        Smooth traces for the slide
        :param n_distance: distance to inflate and deflate the nerve trace
        :param i_distance: distance to inflate and deflate the fascicle traces"""

        if i_distance is None:
            self.throw(113)
        for trace in self.trace_list():
            if isinstance(trace, Nerve):
                trace.smooth(n_distance)
            else:
                trace.smooth(i_distance)

    def generate_perineurium(self, fit: dict):
        for fascicle in self.fascicles:
            fascicle.perineurium_setup(fit=fit)

    def rotate(self, angle: float):
        """
        :param angle: angle in radians, only knows how to rotate around its own centroid
        """

        if self.monofasc():
            center = list(self.fascicles[0].centroid())
        else:
            center = list(self.nerve.centroid())
            self.nerve.rotate(angle, center)

        for fascicle in self.fascicles:
            fascicle.rotate(angle, center)

        self.validation()

    def bounds(self):
        """
        :return: check bounds of all traces and return outermost bounds
        """
        allbound = np.array([trace.bounds() for trace in self.trace_list() if trace is not None])
        return (
            min(allbound[:, 0]),
            min(allbound[:, 1]),
            max(allbound[:, 2]),
            max(allbound[:, 3]),
        )

    def trace_list(self):
        """
        :return: list of all traces in the slide
        """
        if self.monofasc():
            trace_list = [f.outer for f in self.fascicles]
        else:
            trace_list = [self.nerve] + [f.outer for f in self.fascicles]
        return trace_list

    def write(self, mode: WriteMode, path: str):
        """
        :param mode: Sectionwise for now... could be other types in the future (STL, DXF)
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

            # write nerve (if not monofasc) and fascicles
            if self.monofasc():
                trace_list = [(self.fascicles, 'fascicles')]
            else:
                trace_list = [([self.nerve], 'nerve'), (self.fascicles, 'fascicles')]

            for items, folder in trace_list:
                # build path if not already existing
                if not os.path.exists(folder):
                    os.makedirs(folder)
                os.chdir(folder)

                # write all items (give filename as i (index) without the extension
                for i, item in enumerate(items):
                    if isinstance(item, Trace):  # not Nerve bc it is buffer class!
                        if not os.path.exists(str(i)):
                            os.mkdir(str(i))
                        item.write(mode, os.path.join(os.getcwd(), str(i), str(i)))
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
