#!/usr/bin/env python3.7

"""Defines Trace class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""


import random
from copy import deepcopy

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyclipper
import pymunk
from shapely.affinity import affine_transform, rotate, scale
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

from src.utils import DownSampleMode, MorphologyError, WriteMode


class Trace:
    """Core object for manipulating points/traces of nerve sections.

    Trace is the fundamental building block for nerve geometries
    (fascicles, nerve, endoneurium, perineurium)
    """

    def __init__(self, points):
        """Initialize a Trace object.

        :param points: nx3 iterable of points [x, y, z].
        """
        # These are private instance variables that are returned by getter
        self.__contour = None
        self.__polygon = None
        self.__centroid = None
        self.__int_points = None
        self.__min_circle = None

        # Mutable tracker for affine transformations
        self._transform_mat = np.eye(4).tolist()

        # add 0 as z value if only x and y given
        if np.shape(points)[1] == 2:
            points = np.append(points, np.zeros([len(points), 1]), 1)

        self.points = None  # must declare instance variable in __init__ at some point!
        self.append(points)

    @property
    def transform_matrix(self) -> list[list[float]]:
        """Getter for transformation matrix property.

        :return: Transformation matrix for trace.
        """
        return self._transform_mat

    def set_transform_matrix(self, value):
        """Setter for transformation matrix property.

        :param value: Value for new transformation matrix.
        """
        self._transform_mat = value

    def reset_transform(self):
        """Reset the Trace transformation matrix property to identity."""
        self._transform_mat = np.eye(4)

    # %% public, MUTATING methods
    def append(self, points):
        """Append points to the end of the trace.

        :param points: nx3 ndarray, where each row is a point [x, y, z]
        :raises ValueError: if points do not have 3 columns
        """
        # make sure points is multidimensional ndarray (only applicable if a single point is passed in)
        points = np.atleast_2d(points).astype(float)

        # ensure 3 columns
        if np.shape(points)[1] != 3:
            raise ValueError("Points to append must have 3 columns (x y z)")

        # if points has not been initialized (case when called by __init__)
        if self.points is None:
            self.points = points
        else:
            self.points = np.append(self.points, points, axis=0)  # axis = 0 to append rows

        # required for mutating method
        self.__update()

    def offset(self, fit: dict = None, distance: float = None):
        """Offsets the trace by a given distance.

        This will shrink or expand the trace, similar to a morphological dilate or erode.
        Note: this is not an affine transformation.
        :param fit: dictionary of parameters for a linear fit of distance to offset based off area.
        :param distance: used to scale by a discrete distance
        :raises ValueError: if fit and distance are both None
        """
        # create clipper offset object
        pco = pyclipper.PyclipperOffset()

        # put self.points into a 2-D tuple
        tuple_points = tuple([tuple(point[:2]) for point in self.points])

        # add points to clipper
        pco.AddPath(tuple_points, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

        if fit is not None:
            # find offset distance from factor and mean radius
            distance: float = fit.get("a") * 2 * np.sqrt(self.area() / np.pi) + fit.get("b")
        elif distance is None:
            raise ValueError("Either factor or distance MUST be provided.")

        # set new points of offset
        self.points = None
        newpoints = pco.Execute(distance)
        # ensure closed loop
        newpoints.append(newpoints[0])
        self.append([point + [0] for point in newpoints[np.argmax([len(point) for point in newpoints])]])

        # cleanup
        self.__update()
        pco.Clear()

    def smooth(self, distance, area_compensation=True):
        """Smooth a contour using a dilation followed by erosion.

        :param distance: amount to use for dilation and erosion, in whatever units the trace is using
        :param area_compensation: if True, after smoothing, scale each trace to match its original area
        :raises ValueError: if distance is not a positive number
        :raises MorphologyError: if the pre-smoothing area cannot be maintained
        """
        if distance < 0:
            raise ValueError("Smoothing value cannot be negative (Sample.json)")
        if distance == 0:
            return
        pre_area = self.area()
        self.offset(fit=None, distance=distance)
        self.offset(fit=None, distance=-distance)
        if area_compensation is True:
            # scale back to area of original trace
            self.scale((pre_area / self.area()) ** 0.5)
            if abs(pre_area - self.area()) > 1:
                raise MorphologyError("After smoothing trace, could not restore original area.")
        else:
            self.scale(1)
        self.points = np.flip(self.points, axis=0)  # set points to opencv orientation

    @staticmethod
    def get_shapely_affine(matrix: list[list[float]], return_ndim: int) -> list[float]:
        """Convert 4x4 transformation matrix to shapely.affinity.affine_transform format.

        https://shapely.readthedocs.io/en/stable/manual.html#shapely.affinity.affine_transform

        :param matrix: Square (4x4) affine transformation matrix.
        :param return_ndim: 2 for 2D (x,y) return matrix, 3 for 3d (x,y,z).
        :raises NotImplementedError: return_ndim not supported.
        :return: list of float parameters for affine_transform.
        """
        if return_ndim not in [2, 3]:
            raise NotImplementedError(f"return_ndim not recognized as 2 or 3, received {return_ndim}")

        np_mat = np.asarray(matrix)
        if return_ndim == 2:
            return [
                np_mat[0, 0],
                np_mat[0, 1],
                np_mat[1, 0],
                np_mat[1, 1],
                np_mat[0, 3],
                np_mat[1, 3],
            ]
        return [
            np_mat[0, 0],
            np_mat[0, 1],
            np_mat[0, 2],
            np_mat[1, 0],
            np_mat[1, 1],
            np_mat[1, 2],
            np_mat[2, 0],
            np_mat[2, 1],
            np_mat[2, 2],
            np_mat[0, 3],
            np_mat[1, 3],
            np_mat[2, 3],
        ]

    @staticmethod
    def make_transform_matrix(angle: float, scale_factor: list[float], center: list[float]) -> np.ndarray:
        """Construct transformation matrix to rotate, shift, and scale trace points.

        Rotation and scaling will be performed after centering the points at the provided center.

        :param angle: Counterclockwise xy-plane rotation in radians
        :param scale_factor: List of (x, y, z) scaling factors
        :param center: List of (x, y, z) center about which to apply rotation and scaling
        :returns: 4x4 transformation matrix
        """
        # Assemble affine transformation matrix for each step
        # Transformation matrices can be combined with left-side matrix multiplication
        # Transformation steps:
        # 1. Translate to center of points to origin (T_orig),
        # 2. scale about origin (S),
        # 3. rotate about origin (R),
        # 4. translate to original center (T_center)
        # Final transformation matrix is T_center*R*S*T_orig
        center_mat = np.eye(4)
        uncenter_mat = np.eye(4)
        center_mat[: len(center), -1] = -1 * np.asarray(center)  # translates trace points center to origin
        uncenter_mat[: len(center), -1] = np.asarray(center)  # translates trace points to original center
        scale_mat = np.eye(4)
        scale_mat[0, 0] = scale_factor[0]  # scale points by x factor
        scale_mat[1, 1] = scale_factor[1]  # scale points by y factor
        scale_mat[2, 2] = scale_factor[2]  # scale points by z factor
        rot_mat = np.array(
            [[np.cos(angle), -np.sin(angle), 0, 0], [np.sin(angle), np.cos(angle), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        )  # rotates points by angle

        # Left-multiply to add subsequent steps
        return np.dot(uncenter_mat, np.dot(rot_mat, np.dot(scale_mat, center_mat)))

    def transform(self, transform_matrix: np.ndarray):
        """Transform trace given 4x4 affine transformation matrix.

        :param transform_matrix: 4x4 affine transformation matrix.
        """
        # Get the affine transformation matrix in Shapely affine_transform format
        shapely_tfm = self.get_shapely_affine(transform_matrix, 3)
        # Transform Shapely representation of Trace object
        transformed_polygon: Polygon = affine_transform(self.polygon(), shapely_tfm)
        # Set new trace points
        self.points = None
        self.append([list(coord[:2]) + [0] for coord in transformed_polygon.boundary.coords])
        # Update transformation tracker with this matrix
        self._transform_mat = np.dot(transform_matrix, self._transform_mat).tolist()

    def scale(self, factor: float = 1, center: list[float] | str = 'centroid'):
        """Scales the trace by a given factor.

        :param factor: scaling factor to scale up by - multiply all points by a factor; [X 0 0; 0 Y 0; 0 0 Z]
        :param center: string "centroid", string "center" or a point [x,y]
        :raises ValueError: if center is not a valid choice
        """
        if isinstance(center, list):
            center = tuple(center)
        else:
            # Same as Shapely internals for scale() origin argument
            if center == 'centroid':
                center = np.mean(self.points, axis=0)
            elif center == 'center':
                center = np.max(self.points, axis=0) + np.min(self.points, axis=0) / 2
            else:
                raise ValueError("Invalid scale center string.")

        # Assemble affine transformation matrix
        tfm_mat = self.make_transform_matrix(0, [factor, factor, 1], center)

        # Actually do the scaling with Shapely, but equivalent to tfm_mat*self.points
        scaled_polygon: Polygon = scale(self.polygon(), *([factor] * 3), origin=Point(center))

        self.points = None
        self.append([list(coord[:2]) + [0] for coord in scaled_polygon.boundary.coords])
        # Append these transformations to transformation tracker with left multiplication
        self._transform_mat = np.dot(tfm_mat, self._transform_mat).tolist()
        self.__update()

    def rotate(self, angle: float, center: list[float] | str = 'centroid'):
        """Rotate the trace by a given angle.

        :param angle: rotates trace by radians CCW
        :param center: string "centroid", string "center" or a point [x,y]
        :raises ValueError: if center is not a valid choice
        """
        if isinstance(center, list):
            center = tuple(center)
        else:
            # Same as Shapely internals for scale() origin argument
            if center == 'centroid':
                center = np.mean(self.points, axis=0)
            elif center == 'center':
                center = np.max(self.points, axis=0) + np.min(self.points, axis=0) / 2
            else:
                raise ValueError("Invalid scale center string.")

        # Assemble affine transformation matrix
        tfm_mat = self.make_transform_matrix(angle, [1, 1, 1], center)

        rotated_polygon: Polygon = rotate(self.polygon(), angle, origin=Point(center), use_radians=True)

        self.points = None
        self.append([list(coord[:2]) + [0] for coord in rotated_polygon.boundary.coords])
        # Append these transformations to transformation tracker with left multiplication
        self._transform_mat = np.dot(tfm_mat, self._transform_mat).tolist()
        self.__update()

    def shift(self, vector):
        """Shift the trace by a vector.

        :param vector: 1-dim vector with 3 elements... shape is (3,)
        :raises ValueError: if vector is not a 1-dim vector with 3 elements
        """
        # must be 3 item vector
        if np.shape(vector) != (3,):
            raise ValueError("Vector provided must be of shape (3) (i.e. 1-dim)")

        # Assemble affine transformation matrix for each step
        # Transformation steps:
        # 1. Translate to center of points by the shift vector (T_shift),
        # Final transformation matrix is T_shift
        trans_mat = np.eye(4)
        trans_mat[0:-1, -1] = vector

        # apply shift to each point
        vector = [float(item) for item in vector]
        self.points += vector
        # Append these transformations to transformation tracker with left multiplication
        self._transform_mat = np.dot(trans_mat, self._transform_mat)

        # required for mutating method
        self.__update()

    def down_sample(self, mode: DownSampleMode, step: int):
        """Down sample trace by removing points at even intervals.

        Will start indices on "step-th" element
           (i.e. if step is 4, first selected element at index 3)

        :param mode: decide whether to KEEP only the points on steps, or REMOVE only those points
        :param step: spacing between each selected point (both keep and remove)
        """
        ii = list(range(step - 1, self.count(), step))

        if mode == DownSampleMode.KEEP:
            pass  # nothing here; just showing the case for readability
        else:  # mode == DownSampleMode.REMOVE:
            ii = [i for i in list(range(self.count())) if i not in ii]

        self.points = self.points[ii, :]

        # required for mutating method
        self.__update()

    # %% public, NON-MUTATING methods
    def count(self) -> int:
        """Get the number of points in the trace.

        :return: number of rows in self.points (i.e. number of points)
        """
        return np.shape(self.points)[0]

    # %% dependent on shapely.geometry.Polygon (ALL 2D GEOMETRY)
    def polygon(self) -> Polygon:
        """Generate a shapely Polygon object from the trace.

        :raises ValueError: if the trace points have multiple z values
        :return: shape of polygon as a shapely.geometry.Polygon (ALL 2D geometry)
        """
        if self.__polygon is None:
            if len(set(self.points[:, 2])) != 1:
                raise ValueError(
                    "Current implementation requires that all points in Trace have same z-value to create contour"
                )

            self.__polygon = Polygon([tuple(point) for point in self.points[:, :2]])

        return self.__polygon

    def bounds(self):
        """Calculate the bounding box of the trace.

        :return: bounds of the trace object
        """
        return self.polygon().bounds

    def random_points(self, count: int, buffer: float = 0, my_xy_seed: int = 123) -> list[tuple[float]]:
        """Get random points within the trace.

        :param my_xy_seed: seed for random number generator
        :param buffer: minimum distance from the edge of the trace
        :param count: number of points to find
        :raises ValueError: if buffer is too large for the trace
        :return: list of tuples (x,y) that are within the trace (polygon)
        """
        if self.ecd() < buffer * 2.5:
            raise ValueError("Buffer is too large for trace")

        trace_to_compare = self.deepcopy()
        trace_to_compare.offset(None, -buffer)

        min_x, min_y, max_x, max_y = trace_to_compare.polygon().bounds

        points: list[tuple[float]] = []
        random.seed(my_xy_seed)

        while len(points) < count:
            coordinate = tuple(
                (random.random() * (ceiling - floor)) + floor for floor, ceiling in ((min_x, max_x), (min_y, max_y))
            )

            if Point(coordinate).within(trace_to_compare.polygon()):
                points.append(coordinate)

        return points

    def within(self, outer: 'Trace') -> bool:
        """Check if the trace is within another trace.

        :param outer: other Trace to check
        :return: True if within other Trace, else False
        """
        return self.polygon().within(outer.polygon())

    def intersects(self, other: 'Trace') -> bool:
        """Check if the trace intersects another trace.

        :param other: other Trace to check
        :return: True if intersecting, else False
        """
        return self.polygon().boundary.intersects(other.polygon().boundary)

    def centroid(self) -> tuple[float, float]:
        """Get the centroid of the trace.

        :return: ellipse centroid as tuple: center --> (x, y)
        """
        if self.__centroid is None:
            self.__centroid = list(self.polygon().centroid.coords)[0]

        return self.__centroid

    def angle_to(self, other: 'Trace'):
        """Calculate the angle between the centroid of the trace and another trace.

        :param other: type Trace
        :return: returns the CCW angle to the other trace based on self and other's centroids
        """
        return Trace.angle(self.centroid(), other.centroid())

    @staticmethod
    def angle(first, second):
        """Calculate an angle between two points.

        :param first: first point
        :param second: second point
        :return: angle in radians
        """
        return np.arctan2(second[1] - first[1], second[0] - first[0])

    def area(self) -> float:
        """Get the area of the Trace.

        :return: area of Trace
        """
        return self.polygon().area

    def min_distance(self, other: 'Trace') -> float | tuple:
        """Find the minimum distance between this trace and another trace.

        :param other: Trace to find distance to
        :return: float minimum distance and the points if indicated
        """
        distance = self.polygon().boundary.distance(other.polygon().boundary)

        return distance, nearest_points(self.polygon(), other.polygon())

    def max_distance(self, other: 'Trace') -> float:
        """Find the maximum distance between this trace and another trace.

        :param other: Trace to find distance to
        :return: float maximum distance
        """
        return self.polygon().boundary.hausdorff_distance(other.polygon().boundary)

    def centroid_distance(self, other: 'Trace') -> float | tuple:
        """Find the distance between the centroids of this trace and another trace.

        :param other: Trace to find distance to
        :return: float maximum distance and the points if indicated
        """
        self_c = Point([self.centroid()])

        distance = self_c.distance(other.polygon().boundary)

        return distance, nearest_points(self_c, other.polygon().boundary)

    # %% contour-dependent (cv2)
    def contour(self) -> np.ndarray:
        """Return a contour based off the Trace.

        Builds a "fake" contour so that cv2 can analyze it (independent of the image). Use for to_circle and to_ellipse.
        :raises ValueError: if the trace points have multiple unique z values
        :return: contour as np.ndarray
        """
        if self.__contour is None:
            # check points all have same z-value (MAY BE CHANGED?)
            if len(set(self.__int_points[:, 2])) != 1:
                raise ValueError(
                    "Current implementation requires that all points in Trace have same z-value to create contour"
                )

            self.__contour = np.zeros([self.count(), 1, 2])
            # check that all points in same plane
            for i, point in enumerate(self.__int_points):
                self.__contour[i, 0] = point[:-1]  # do not include z

            self.__contour = self.__int32(self.__contour)

        return self.__contour

    def ellipse(self):
        """Generate a best-fit ellipse from the trace.

        NOTE: this uses 2-D contour (ignores z-coordinate)
        :return: ellipse specs as 2-D tuple: (center, axes) --> ((x, y), (a, b), angle)
        """
        return cv2.fitEllipse(self.contour())

    def mean_radius(self) -> float:
        """Calculate the mean radius of the trace.

        :return: the mean radius of the best-fit ellipse
        """
        ((_, _), (a, b), _) = cv2.fitEllipse(self.contour())
        return float(np.mean([item / 2 for item in (a, b)], axis=0))

    def to_ellipse(self):
        """Get a best fit ellipse from the trace.

        :return: returns ellipse object methods for best-fit ellipse
        """
        # ((centroid), (axes), angle) ... note angle is in degrees
        ((u, v), (a, b), angle) = self.ellipse()

        # return the associated ellipse object, after converting angle to degrees
        return self.__ellipse_object(u, v, a, b, angle * 2 * np.pi / 360)

    def to_circle(self, buffer: float = 0.0):
        """Get best fit circle from the trace.

        :param buffer: buffer to add to the circle
        :return: returns circle object for best-fit circle
        """
        # ((centroid), (axes), angle) ... note angle is in degrees
        ((u, v), (_, _), angle) = self.ellipse()

        # find average radius of circle
        # casting to float is just so PyCharm stops yelling at me (I think it should already be a float64?)
        r = float(np.sqrt(self.area() / np.pi)) - buffer

        # return the associated ellipse object, after converting angle to degrees
        # also, PyCharm thinks that np.mean returns a ndarray, but it definitely isn't in this case
        return self.__ellipse_object(u, v, 2 * r, 2 * r, angle * 2 * np.pi / 360)

    def __ellipse_object(self, u: float, v: float, a: float, b: float, angle: float) -> 'Trace':
        """Create an ellipse object from the given parameters.

        :param u: x value of center
        :param v: y value of center
        :param a: first (minor) axis, twice the "radius"
        :param b: second (major) axis, twice the "radius"
        :param angle: clockwise angle to rotate in radians
        :return: a new Trace object with the points of the best-fit ellipse (point count is preserved)
        """
        # get t values for parameterized ellipse and preserve number of points
        t = np.linspace(0, 2 * np.pi, self.count())

        # divide a and b by 2 because they are AXIS lengths
        (a, b) = (item / 2 for item in (a, b))

        # find x and y values along ellipse (not shifted to centroid yet)
        (x, y) = (a * np.cos(t), b * np.sin(t))

        # create rotation matrix
        rot_mat = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

        # apply rotation and shift to centroid
        points = (rot_mat @ np.array([x, y])).T + [u, v]

        # add column of z-values (should all be the same)
        points = np.append(points, np.c_[self.points[:, 2]], axis=1)
        trace = Trace(points)
        trace.set_transform_matrix(self.transform_matrix)

        return trace

    # %% output
    def plot(
        self,
        plot_format: str = 'k-',
        color: tuple[float, float, float, float] = None,
        ax: plt.Axes = None,
        linewidth=1,
        line_kws: dict = None,
    ):
        """Plot the trace.

        :param line_kws: Additional keyword arguments to matplotlib.pyplot.plot
        :param linewidth: Width of the line
        :param ax: Axes to plot on
        :param color: Color to fill the trace with, if None, no fill
        :param plot_format: the plt.plot format spec (see matplotlib docs)
        """
        if ax is None:
            ax = plt.gca()

        # append first point to plot as loop
        points = np.vstack([self.points, self.points[0]])

        if color is not None:
            ax.fill(points[:, 0], points[:, 1], color=color)

        ax.plot(points[:, 0], points[:, 1], plot_format, linewidth=linewidth, **{} if line_kws is None else line_kws)

    def plot_centroid(self, plot_format: str = 'k*'):
        """Plot the centroid of the trace.

        :param plot_format: the plt.plot format spec (see matplotlib docs)
        """
        plt.plot(*self.centroid(), plot_format)

    def write(self, mode: WriteMode, path: str):
        """Write Trace data (points, elements, etc.) to file.

        :param mode: choice of write implementations - sectionwise file for COMSOL
        :param path: string path with file name of file WITHOUT extension (it is derived from mode)
        :raises ValueError: if mode is not supported
        :raises OSError: if file cannot be written
        :return: string full path including extension that was written to
        """
        # add extension
        path += WriteMode.file_endings.value[mode.value]

        try:
            # open in write mode; "+" indicates to create file if not found
            with open(path, 'w+') as f:
                count = self.count()

                # choose implementation from mode
                if mode == WriteMode.SECTIONWISE:
                    # write coordinates
                    f.write('%% Coordinates\n')
                    for i in range(count):
                        f.write(f'{self.points[i, 0]}\t{self.points[i, 1]}\t{self.points[i, 2]}\n')

                    # write elements (corresponding to their coordinates)
                    f.write('%% Elements\n')
                    for i in range(count):
                        # if not last point, attach to next point
                        if i < count - 1:
                            f.write(f'{i + 1}\t{i + 2}\n')
                        else:  # attach to first point (closed loop)
                            f.write(f'{i + 1}\t{1}\n')

                elif mode == WriteMode.SECTIONWISE2D:
                    # write coordinates
                    f.write('%% Coordinates\n')
                    for i in range(count):
                        f.write(f'{self.points[i, 0]}\t{self.points[i, 1]}\n')

                else:
                    raise ValueError("Write mode not supported or invalid")

        except OSError as e:
            raise OSError(f"Exception while writing: {e}")

        return path

    def deepcopy(self) -> 'Trace':
        """Deep copy of Trace object.

        Deep copies ensure that the new object is not a reference to the old object;
            changes to the new object will not affect the old object.

        :return: creates a new place in memory for the Trace. See: https://docs.python.org/2/library/copy.html
        """
        return deepcopy(self)

    def pymunk_poly(self) -> tuple[pymunk.Body, pymunk.Poly]:
        """Generate pymunk Body and Poly objects for the Trace.

        :return: a body and polygon shape, rigid polygon
        """
        copy = self.deepcopy()
        copy.shift(-np.array(list(copy.centroid()) + [0]))

        mass = 1
        radius = 1
        vertices = [tuple(point[:2]) for point in copy.points]
        inertia = pymunk.moment_for_poly(mass, vertices)
        body = pymunk.Body(mass, inertia)
        body.position = self.centroid()  # position is tracked from trace centroid
        shape = pymunk.Poly(body, vertices, radius=radius)
        shape.density = 0.01  # all fascicles have same density so this value does not matter
        shape.friction = 0.5
        shape.elasticity = 0.0  # they absorb all energy, i.e. they do not bounce
        return body, shape

    def pymunk_segments(self, space: pymunk.Space) -> list[pymunk.Segment]:
        """Generate list of pymunk segment objects comprising a trace.

        :param space: pymunk space to add segments to
        :return: returns a list of static line segments that cannot be moved
        """
        copy = self.deepcopy()

        points = np.vstack((copy.points, copy.points[0]))

        segments: list[pymunk.Segment] = []

        for first, second in zip(points[:-1], points[1:]):
            if np.array_equiv(first[:2], second[:2]):
                pass
            segments.append(
                pymunk.Segment(
                    space.static_body,
                    first[:2].tolist(),
                    second[:2].tolist(),
                    radius=1.0,
                )
            )
        return segments

    def make_circle(self):
        """Return the smallest circle that encloses all the given points.

        Runs in expected O(n) time, randomized.
        :return: A triple of floats representing a circle.
        """
        points = [(float(x), float(y)) for (x, y) in self.points[:, 0:2]]
        if len(points) < 2:
            if len(points) == 1:
                return points[0][0], points[0][1], 0.0
            return None  # Maybe error if no points?
        # OpenCV requires float32 input
        (cx, cy), r = cv2.minEnclosingCircle(np.array(points).astype(np.float32))
        return cx, cy, r

    # %% private utility methods
    def __update(self):
        """Update the internal data structures."""
        self.__int_points = self.__int32(self.points)
        self.__contour = None
        self.__polygon = None
        self.__centroid = None

    @staticmethod
    def __int32(points: np.ndarray):
        """Convert points to int32.

        :param points: points to convert
        :return: points converted to int32
        """
        return np.array(np.round(points), dtype=np.int32)

    def ecd(self):
        """Return the effective circular diameter.

        :return: effective circular diameter
        """
        return 2 * np.sqrt(self.area() / np.pi)
