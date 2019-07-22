import numpy as np

from src.utils import *


class Trace(Exceptionable):

    def __init__(self, points, exception_config):
        """

        :param points:
        :param exception_config:
        """

        self.points = None  # must declare instance variable in __init__ at some point!
        self.append(points)

        # set up superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

    def append(self, points: np.ndarray):
        """
        :param points: nx3 ndarray, where each row is a point (x, y, z)
        :return: none
        """
        # if points has not been initialized (case when called by __init__)
        if self.points is None:
            self.points = np.array(points)
        else:
            self.points = np.append(self.points, np.array(points))

        # make sure points is multidimensional ndarray
        self.points = self.__force_multidim(self.points)

    def empty(self):
        """
        Set self.points to None
        :return: none
        """
        self.points = None

    def count(self):
        """
        :return: number of rows in self.points (i.e. number of points)
        """
        return np.shape(self.points)[0]

    def shift(self, vector):
        """
        :param vector: 1-dim vector with 3 elements... shape is (3,)
        :return: none
        """

        # must be 3 item vector
        if np.shape(vector) != (3,):
            self.throw(3)

        # step through each row (point), and apply shift
        self.points = np.apply_along_axis(lambda point: point + vector, 1, self.points)

    def write(self, mode: WriteMode):
        pass

    @staticmethod
    def __force_multidim(vector):
        """
        :param vector: arbitrary list or ndarray
        :return: if the vector had shape (n,), now it has (1,n)
        """
        shape = np.shape(vector)
        print(shape)
        if len(shape) == 1:
            vector = np.reshape(vector, (1, shape[0]))
        return vector
