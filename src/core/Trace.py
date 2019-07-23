import numpy as np
import os
import cv2

from src.utils import *


class Trace(Exceptionable):

    #%% constructor
    def __init__(self, points, exception_config):
        """
        :param points:
        :param exception_config:
        """
        # equivalent of calling self.clear_contour()
        self.__contour = None

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

        self.__update()

    def shift(self, vector):
        """
        :param vector: 1-dim vector with 3 elements... shape is (3,)
        """

        # must be 3 item vector
        if np.shape(vector) != (3,):
            self.throw(3)

        # step through each row (point), and apply shift
        self.points = self.points + vector

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

    def write(self, mode: WriteMode, path: str):
        if mode == WriteMode.SECTIONWISE:
            pass
        else:
            self.throw(4)

    #%% private utility methods
    def __update(self):
        self.__int_points = self.__intify(self.points)
        self.__clear_contour()

    def __clear_contour(self):
        self.__contour = None

    @staticmethod
    def __intify(points: np.ndarray):
        return np.array(np.round(points), dtype=np.int32)
