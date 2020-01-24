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
        self.xy_coordinates = None
        self.full_coordinates = None

        # empty metadata
        self.fiber_metadata: Dict[str, list] = {}
        self.add(SetupMode.NEW, Config.FIBER_Z, os.path.join('config', 'system', 'fiber_z.json'))

        self.fibers = None

    def init_post_config(self):
        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(39)  # TODO NOT WRITTEN - INCORRECT INDEX

    def generate(self):
        """
        :return:
        """
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
