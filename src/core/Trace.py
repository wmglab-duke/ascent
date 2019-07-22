import numpy as np

from src.utils import *


class Trace(Exceptionable, Configurable):

    def __init__(self, x, y, z, master_config, exception_config):
        """

        :param x:
        :param y:
        :param z:
        :param master_config:
        :param exception_config:
        """

        self.points = None
        self.append(x, y, z)

        # set up superclasses
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

    def append(self, x, y, z):
        # check that all lists are of same length
        # creates "set" form list of lengths of x, y, z, then tests if there is 1 item (hence, all items equal)
        if len(set([len(item) for item in [x, y, z]])) is not 1:
            self.throw(3)

        if self.points is None:
            self.points = np.array(points)
        else:
            np.append(self.points, np.array(points))
