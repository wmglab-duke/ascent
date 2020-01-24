# builtins

# packages

# access
from typing import Dict

import numpy as np

from core import Sample
from src.utils import *


class FiberSet(Exceptionable, Configurable, Saveable):
    """
    Required (Config.) JSON's:
        MODEL
        SIM
    """

    def __init__(self, sample: Sample, exceptions_config: list):
        """
        :param exceptions_config: preloaded exceptions.json data
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # initialize empty lists of fiber points
        self.fibers = None

        self.add(SetupMode.NEW, Config.FIBER_Z, os.path.join('config', 'system', 'fiber_z.json'))

    def init_post_config(self):
        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(39)  # TODO NOT WRITTEN - INCORRECT INDEX

    def generate(self):
        """
        :return:
        """
        fibers_xy = self.generate_xy()
        self.fibers = self.generate_z(fibers_xy)


        fibers = None

        self.fibers = fibers

    def write(self, mode: WriteMode, path: str):
        """
        :param mode:
        :param path:
        :return:
        """
        filepath = 'None'
        fiber = 'None'
        np.save(filepath, fiber)

    def generate_xy(self) -> np.ndarray:
        return []

    def generate_z(self, fibers_xy):
        pass
