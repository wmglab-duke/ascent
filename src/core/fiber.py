# builtins

# packages

# access
import numpy as np

from src.utils import *

class Fiber(Exceptionable, Configurable, Saveable):
    """
    Required (Config.) JSON's:
        MODEL
        SIM
    """

    def __init__(self, exceptions_config: list):
        """
        :param exceptions_config: preloaded exceptions.json data
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # init instance variables
        # self.mode = \
        #     self.dt = \
        #     self.t_start = \
        #     self.t_on = \
        #     self.t_off = \
        #     self.t_stop = \
        #     self.time_unit = \
        #     self.frequency_unit = None

        self.fibers = None


    def init_post_config(self):

        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(39)  # TODO NOT WRITTEN - INCORRECT INDEX

        # # get mode
        # self.modes = self.search_multi_mode(Config.SIM, WaveformMode)
        #
        # # get global vars data
        # global_parameters: dict = self.search(Config.SIM,
        #                                       WaveformMode.parameters.value,
        #                                       WaveformMode.global_parameters.value)
        #
        # # unpack global variables
        # self.dt, \
        # self.t_start, \
        # self.t_on, \
        # self.t_off, \
        # self.t_stop, \
        # self.time_unit, \
        # self.frequency_unit = [global_parameters.get(key) for key in ['dt',
        #                                                               't_start',
        #                                                               't_on',
        #                                                               't_off',
        #                                                               't_stop',
        #                                                               'time_unit',
        #                                                               'frequency_unit']]
        #
        # self.validate_times()


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
