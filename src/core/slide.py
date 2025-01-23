#!/usr/bin/env python3.7

"""Defines Slide class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""
import itertools
import os

import matplotlib.pyplot as plt
import numpy as np
from quantiphy import Quantity
from shapely.geometry import Point

from src.utils import MethodError, MorphologyError, NerveMode, ReshapeNerveMode, WriteMode

from .fascicle import Fascicle
from .nerve import Nerve
from .trace import Trace


class Slide:
    """The Slide class is used to represent a slide of fascicles and nerves.

    The fascicles and nerve boundary are represented
       with Trace and Nerve objects, respectively.
    """

    def __init__(
        self,
        fascicles: list[Fascicle],
        nerve: Nerve,
        nerve_mode: NerveMode,
        will_reposition: bool = False,
    ):
        """Initialize a Slide object.

        :param fascicles: List of fascicles
        :param nerve: Nerve (effectively is a Trace)
        :param nerve_mode: from Enums, indicates if the nerve exists or not (PRESENT, NOT_PRESENT)
        :param will_reposition: boolean flag that tells the initializer whether or not it should be validating the
            geometries - if it will be reposition then this is not a concern
        :raises ValueError: if will repositon is True and the nerve mode is not PRESENT
        """
        self.nerve_mode = nerve_mode

        self.nerve: Nerve = nerve
        self.fascicles: list[Fascicle] = fascicles

        if not will_reposition:
            self.validate()
        else:
            if self.nerve_mode == NerveMode.NOT_PRESENT:
                raise ValueError("Cannot deform monofascicle")

        self.orientation_point: tuple[float, float] | None = None
        self.orientation_angle: float | None = None

    def monofasc(self) -> bool:
        """Check if slide is monofascicular.

        :return: True if there is only one fascicle
        """
        return self.nerve_mode == NerveMode.NOT_PRESENT and len(self.fascicles) == 1

    def fascicle_centroid(self) -> tuple[float, float]:
        """Calculate the centroid of all fascicles.

        :return: Tuple of x and y coordinates of centroid
        """
        area_sum = x_sum = y_sum = 0.0

        for fascicle in self.fascicles:
            x, y = fascicle.centroid()
            area = fascicle.area()

            x_sum += x * area
            y_sum += y * area
            area_sum += area

        return (x_sum / area_sum), (y_sum / area_sum)

    def validate(
        self,
        die: bool = True,
        tolerance: float = None,
        plotpath=None,
        shapely: bool = True,
    ) -> bool:
        """Check to make sure nerve geometry is not overlapping itself.

        :param die: if non-specific, decides whether to throw an error_message if it fails
        :param tolerance: minimum separation distance for unit you are currently in
        :param plotpath: path to save plot to
        :param shapely: if True, uses shapely to check for valid polygons
        :raises MorphologyError: if the nerve morphology is invalid
        :return: Boolean for True (no intersection) or False (issues with geometry overlap)
        """

        def debug_plot():
            print('Slide validation failed, saving debug sample plot.')
            if plotpath is None:
                return
            plt.figure()
            self.plot(
                final=False,
                fix_aspect_ratio=True,
                axlabel="\u03bcm",
                title='Debug sample which failed validation.',
            )
            plt.savefig(plotpath + '/sample_debug')
            plt.clf()
            plt.close()

        error_message = ''

        if self.fascicles_too_small():
            debug_plot()
            error_message = (
                "A white area which results in a fascicle trace with <3 points was detected. "
                "Check your input mask for specks."
            )

        if shapely and not self.polygons_are_valid():
            debug_plot()
            error_message = "A polygon was detected which is invalid. Using smoothing may fix this error_message."

        if not self.monofasc():
            if self.fascicle_fascicle_intersection():
                debug_plot()
                error_message = "Fascicle-fascicle intersection found"

            if self.fascicle_nerve_intersection():
                debug_plot()
                error_message = "Fascicle-nerve intersection found"

            if self.fascicles_outside_nerve():
                debug_plot()
                error_message = "Not all fascicles fall within nerve"

            if self.fascicles_too_close(tolerance):
                debug_plot()
                error_message = "Fascicles are too close to each other"

        if error_message == '':
            return True

        debug_plot()
        if die:
            raise MorphologyError(error_message)

        print(MorphologyError(error_message))
        return False

    def fascicles_too_close(self, tolerance: float = None) -> bool:
        """Check to see if any fascicles are too close to each other.

        :param tolerance: Minimum separation distance
        :raises MethodError: If called on a monofascicular slide
        :return: Boolean for True for fascicles too close as defined by tolerance
        """
        if self.monofasc():
            raise MethodError("Method fascicles_too_close does not apply for monofascicle nerves")

        if tolerance is None:
            return False

        pairs = itertools.combinations(self.fascicles, 2)
        return any(first.min_distance(second) < tolerance for first, second in pairs) or any(
            fascicle.min_distance(self.nerve) < tolerance for fascicle in self.fascicles
        )

    def fascicles_too_small(self) -> bool:
        """Check to see if any fascicles are too small.

        :return: True if any fascicle has a trace with less than 3 points
        """
        check = []
        for f in self.fascicles:
            check.append(len(f.outer.points) < 3)
            check.extend([len(i.points) < 3 for i in f.inners])
        return any(check)

    def fascicle_fascicle_intersection(self) -> bool:
        """Check to see if any fascicles intersect each other.

        :raises MethodError: If called on a monofascicular slide
        :return: True if any fascicle intersects another fascicle, otherwise False
        """
        if self.monofasc():
            raise MethodError("Method fascicle_fascicle_intersection does not apply for monofascicle nerves")

        pairs = itertools.combinations(self.fascicles, 2)
        return any(first.intersects(second) for first, second in pairs)

    def fascicle_nerve_intersection(self) -> bool:
        """Check for intersection between the fascicles and nerve.

        :raises MethodError: If called on a monofascicular slide
        :return: True if any fascicle intersects the nerve, otherwise False
        """
        if self.monofasc():
            raise MethodError("Method fascicle_nerve_intersection does not apply for monofascicle nerves")

        return any(fascicle.intersects(self.nerve) for fascicle in self.fascicles)

    def fascicles_outside_nerve(self) -> bool:
        """Check if any fascicle is outside the nerve.

        :raises MethodError: If called on a monofascicular slide
        :return: True if any fascicle lies outside the nerve, otherwise False
        """
        if self.monofasc():
            raise MethodError("Method fascicles_outside_nerve does not apply for monofascicle nerves")

        return any(not fascicle.within_nerve(self.nerve) for fascicle in self.fascicles)

    def move_center(self, point: np.ndarray):
        """Shifts the center of the slide to the given point.

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
        """Get a nerve trace equal to the area of the current nerve trace.

        :param buffer: buffer distance to subtract from nerve trace radius (microns)
        :param mode: Final form of reshaped nerve, either circle or ellipse
        :raises MethodError: If called on a monofascicular slide
        :raises ValueError: for an invalid mode
        :return: a copy of the nerve with reshaped nerve boundary, preserves point count which is SUPER critical for
            fascicle repositioning
        """
        if self.monofasc():
            raise MethodError("Method reshaped_nerve does not apply for monofascicle nerves")

        if mode == ReshapeNerveMode.CIRCLE:  # noqa R505
            return self.nerve.to_circle(buffer)
        elif mode == ReshapeNerveMode.ELLIPSE:
            return self.nerve.to_ellipse()
        elif mode == ReshapeNerveMode.NONE:
            return self.nerve
        else:
            raise ValueError("Invalid reshape mode.")

    def plot(
        self,
        title: str = None,
        final: bool = True,
        inner_format: str = 'b-',
        fix_aspect_ratio: bool = True,
        fascicle_colors: list[tuple[float, float, float, float]] = None,
        ax: plt.Axes = None,
        outers_flag: bool = True,
        inner_index_labels: bool = False,
        show_axis: bool = True,
        axlabel: str = None,
        scalebar: bool = False,
        scalebar_length: float = 1,
        scalebar_units: str = 'mm',
        line_kws=None,
    ):
        """Quick util for plotting the nerve and fascicles.

        :param line_kws: Additional keyword arguments to pass to matplotlib.pyplot.plot
        :param axlabel: label for x and y axes
        :param show_axis: If False, hide the axis
        :param inner_index_labels: whether to label the inner traces with their index
        :param outers_flag: whether to plot the outers of the fascicles
        :param fascicle_colors: List of colors for fascicle fill, ig None, no fill. Colors must be
            of a form accepted by matplotlib
        :param ax: axis to plot on
        :param title: optional string title for plot
        :param final: optional, if False, will not show or add title (if comparisons are being overlayed)
        :param inner_format: optional format for inner traces of fascicles
        :param fix_aspect_ratio: optional, if True, will set equal aspect ratio
        :param scalebar: If True, add a scalebar to the plot
        :param scalebar_length: Length of scalebar
        :param scalebar_units: Units of scalebar
        :raises ValueError: If fascicle_colors is not None and not the same length as the number of inners
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
                raise ValueError("Length of fascicle colors list must match length of fascicles list.")
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

        if scalebar:
            # apply aspect for correct scaling
            ax.apply_aspect()
            # convert scalebar length to meters and calculat span across axes
            quantity = Quantity(scalebar_length, scalebar_units, scale='m')
            scalespan = quantity.scale('micron') / np.diff(ax.get_xlim())[0]
            # add scalebar and label
            ax.add_patch(
                plt.Rectangle(
                    (0.99, 0.02), -scalespan, 0.02, fill='black', facecolor='black', linewidth=0, transform=ax.transAxes
                )
            )
            ax.text(
                0.99,
                0.05,
                f'{scalebar_length} {scalebar_units}',
                horizontalalignment='right',
                verticalalignment='bottom',
                transform=ax.transAxes,
                color='black',
            )

        # if final plot, show
        if final:
            plt.show()

    def scale(self, factor: float, center: list[float] = None):
        """Scale the nerve and fascicles by a factor.

        :param factor: scale factor, only knows how to scale around its own centroid
        :param center: origin [x, y] around which to scale the image
        """
        if center is None:
            if self.monofasc():
                center = list(self.fascicles[0].centroid())
            else:
                center = list(self.nerve.centroid())

        if not self.monofasc():
            self.nerve.scale(factor, center)

        for fascicle in self.fascicles:
            fascicle.scale(factor, center)

    def smooth_traces(self, n_distance, i_distance):
        """Smooth traces for the slide.

        :param n_distance: distance to inflate and deflate the nerve trace
        :param i_distance: distance to inflate and deflate the fascicle traces
        :raises ValueError: if i_distance is None
        """
        if i_distance is None:
            raise ValueError("Fascicle smoothing distance cannot be None")
        for trace in self.trace_list():
            if isinstance(trace, Nerve):
                trace.smooth(n_distance)
            else:
                trace.smooth(i_distance)

    def generate_perineurium(self, fit: dict):
        """Generate perineurium for all fascicles in the slide.

        :param fit: dictionary of fit parameters
            (Linear fit for perineurium thickness based on fascicle area)
        """
        for fascicle in self.fascicles:
            fascicle.perineurium_setup(fit=fit)

    def rotate(self, angle: float):
        """Rotate the slide around its centroid.

        :param angle: angle in radians
        """
        if self.monofasc():
            center = list(self.fascicles[0].centroid())
        else:
            center = list(self.nerve.centroid())
            self.nerve.rotate(angle, center)

        for fascicle in self.fascicles:
            fascicle.rotate(angle, center)

        self.validate()

    def bounds(self):
        """Get the bounding box for the slide.

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
        """Get a list of all traces in the slide.

        :return: list of trace objects
        """
        all_traces = []
        for f in self.fascicles:
            all_traces.append(f.outer)
            all_traces.extend(f.inners)

        if self.nerve_mode != NerveMode.NOT_PRESENT:
            all_traces.append(self.nerve)

        return all_traces

    def write(self, mode: WriteMode, path: str):
        """Write all traces to files for import into COMSOL.

        :param mode: Sectionwise for now... could be other types in the future (STL, DXF)
        :param path: root path of slide
        :raises OSError: if path does not exist
        """
        start = os.getcwd()

        if not os.path.exists(path):
            raise OSError("Invalid path to write Slide to.")

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
            os.makedirs(folder, exist_ok=True)
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
                    os.makedirs(index_folder, exist_ok=True)

                    os.chdir(index_folder)
                    item.write(mode, os.getcwd())

                    # go back up a folder
                    os.chdir(index_start_folder)

            # change directory back to starting place
            os.chdir(sub_start)

        os.chdir(start)

    def polygons_are_valid(self):
        """Check if all polygons are valid and attempt to fix if not.

        :return: True if all polygons are valid, False if not
        """
        for trace in self.trace_list():
            if not trace.polygon().is_valid:
                trace.offset(distance=0)
                if not trace.polygon().is_valid:
                    return False
        return True

    def map_points(self, points: np.ndarray) -> tuple[list, list]:
        """Map points to fascicles.

        Given a ndarray or list of 2D or 3D points, return a list mapping of to point index to an inner it's within.

        :param points: list[xy[z]] coordinates of the fibers
        :return: mapping from fiber index to outer index and from outer index to inner index.
        """
        out_to_fib = []
        out_to_in = []
        xy_points = np.asarray(points)[:, :2]

        inner_ind = 0  # noqa SIM113
        for i, fascicle in enumerate(self.fascicles):
            out_to_in.append([])
            out_to_fib.append([])
            if len(fascicle.inners) > 0:
                inners = fascicle.inners
            else:
                inners = [fascicle.outer]
            for j, inner in enumerate(inners):
                out_to_in[i].append(inner_ind)
                out_to_fib[i].append([])
                inner_ind += 1
                for q, fiber in enumerate(xy_points):
                    if Point(fiber).within(inner.polygon()):
                        out_to_fib[i][j].append(q)

        return out_to_fib, out_to_in
