from enum import Enum, unique
from matplotlib.path import Path
import numpy as np
import cv2

from src.utils import *


class Trace(Exceptionable):

    #%% constructor
    def __init__(self, points, exception_config):
        """
        :param points:
        :param exception_config:
        """

        self.__contour = None
        self.__path = None

        # set up superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.points = None  # must declare instance variable in __init__ at some point!
        self.__int_points = None
        self.append(points)

    #%% public, MUTATING methods (must call self.__update)
    def append(self, points):
        """
        :param points: nx3 ndarray, where each row is a point [x, y, z]
        """
        # make sure points is multidimensional ndarray
        points = np.atleast_2d(points)

        # ensure 3 columns
        if np.shape(points)[1] != 3:
            self.throw(5)

        # if points has not been initialized (case when called by __init__)
        if self.points is None:
            self.points = points
        else:
            self.points = np.append(self.points, points, axis=0)  # axis = 0 to append rows

        # required for mutating method
        self.__update()

    def shift(self, vector):
        """
        :param vector: 1-dim vector with 3 elements... shape is (3,)
        """

        # must be 3 item vector
        if np.shape(vector) != (3,):
            self.throw(3)

        # apply shift to each point
        self.points += vector

        # required for mutating method
        self.__update()

    def down_sample(self, mode: 'Trace.DownSampleMode', step: int):
        """
        Simple downsample method to remove points at even intervals.
        Will start indices on "stepth" element (i.e. if step is 4, first selected element at index 3)
        :param mode: decide whether to KEEP only the points on steps, or REMOVE only those points
        :param step: spacing between each selected point (both keep and remove)
        """

        ii = list(range(step - 1, self.count(), step))

        if mode == Trace.DownSampleMode.KEEP:
            pass  # nothing here; just showing the case for readability
        elif mode == Trace.DownSampleMode.REMOVE:
            ii = [i for i in list(range(0, self.count())) if i not in ii]
        else:
            # this should be unreachable because above cases are exhaustive
            print('I am utterly baffled.')

        self.points = self.points[ii, :]

        # required for mutating method
        self.__update()

    #%% public, NON-MUTATING methods
    def count(self):
        """
        :return: number of rows in self.points (i.e. number of points)
        """
        return np.shape(self.points)[0]

    def mean_centroid(self):
        """
        :return: calculated centroid of self.points as ndarray with 3 elements
        """
        count = self.count()
        return np.apply_along_axis(lambda column: np.sum(column) / count, 0, self.points)

    #%% dependent on matplotib.path.Path
    def points_path(self):
        """
        NOTE: this is TWO DIMENSIONAL (ignores z-coordinate)
        :return: matplotlib.path.Path object
        """
        if self.__path is None:
            if len(set(self.points[:, 2])) != 1:
                self.throw(6)

            self.__path = Path([tuple(point) for point in self.points[:, :2]])
        return self.__path

    def is_inside(self, outer: 'Trace') -> bool:
        return all(outer.points_path().contains_points([tuple(point) for point in self.points[:, :2]]))

    def intersects(self, other: 'Trace') -> bool:
        return self.points_path().intersects_path(other.points_path())

    #%% contour-dependent (cv2)

    def contour(self):
        """
        Builds a "fake" contour so that cv2 can analyze it (independent of the image)
        :return:
        """
        if self.__contour is None:
            print('building new contour')
            # check points all have same z-value (MAY BE CHANGED?)
            if len(set(self.__int_points[:, 2])) != 1:
                self.throw(6)

            self.__contour = np.zeros([self.count(), 1, 2])
            # check that all points in same plane
            for i, point in enumerate(self.__int_points):
                self.__contour[i, 0] = point[:-1]  # do not include z

            self.__contour = self.__intify(self.__contour)

        return self.__contour

    def area(self):
        """
        NOTE: this uses 2-D contour (ignores z-coordinate)
        :return: area of Trace
        """
        return cv2.contourArea(self.contour())

    def ellipse(self):
        """
        NOTE: this uses 2-D contour (ignores z-coordinate)
        :return: ellipse specs as 2-D tuple: (center, axes) --> ((x, y), (a, b))
        """
        return cv2.fitEllipse(self.contour())

    def ellipse_centroid(self):
        """
        NOTE: this uses 2-D contour (ignores z-coordinate)
        :return: ellipse centroid as tuple: center --> (x, y)
        """
        return cv2.fitEllipse(self.contour())[0]

    def write(self, mode: 'Trace.WriteMode', path: str):
        """
        Write Trace data (points, elements, etc.) to file
        :param mode: choice of write implementations
        :param path: string path with file name of file WITHOUT extension (it is derived from mode)
        :return: string full path including extension that was written to
        """
        # add extension
        path += mode.value

        try:
            # open in write mode; "+" indicates to create file if not found
            with open(path, 'w+') as f:
                count = self.count()

                # choose implementation from mode
                if mode == Trace.WriteMode.SECTIONWISE:

                    # write coordinates
                    f.write('%% Coordinates\n')
                    for i in range(count):
                        f.write('{}\t{}\t{}\n'.format(self.points[i, 0],
                                                      self.points[i, 1],
                                                      self.points[i, 2]))

                    # write elements (corresponding to their coordinates)
                    f.write('%% Elements\n')
                    for i in range(count):
                        # if not last point, attach to next point
                        if i < count - 1:
                            f.write('{}\t{}\n'.format(i + 1, i + 2))
                        else:  # attach to first point (closed loop)
                            f.write('{}\t{}\n'.format(i + 1, 1))

                else:
                    self.throw(4)
        except EnvironmentError as e:
            # only one of these can run, so comment at will
            self.throw(7)
            #raise e

        return path

    #%% private utility methods
    def __update(self):
        self.__int_points = self.__intify(self.points)
        self.__contour = None
        self.__path = None

    @staticmethod
    def __intify(points: np.ndarray):
        return np.array(np.round(points), dtype=np.int32)

    #%% helper Enums for choosing modes
    @unique
    class DownSampleMode(Enum):
        KEEP = 0
        REMOVE = 1

    class WriteMode(Enum): # note: NOT required to have unique values
        SECTIONWISE = '.txt'
        DATA = '.dat'
