from src.utils import Exceptionable, Configurable
from src.utils.enums import *


class Waveform(Exceptionable, Configurable):

    def __init__(self, master_config: dict, exceptions_config: list):

        # set up superclasses
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # get mode
        self.modes = self.search_multi_mode(WaveformMode)

        # get global vars data
        global_parameters: dict = self.search(ConfigKey.MASTER,
                                              WaveformMode.parameters.value,
                                              WaveformMode.global_parameters.value)

        # unpack global variables
        self.dt,\
            self.t_start,\
            self.t_on,\
            self.t_off,\
            self.t_stop,\
            self.time_unit,\
            self.frequency_unit = [global_parameters.get(key) for key in ['dt',
                                                                          't_start',
                                                                          't_on',
                                                                          't_off',
                                                                          't_stop',
                                                                          'time_unit',
                                                                          'frequency_unit']]

        self.validate_times()

    def validate_times(self):

        time_params = [self.t_start, self.t_on, self.t_off, self.t_stop]
        if time_params.sort() != time_params:
            self.throw(32)

        if self.dt > min(time_params):
            self.throw(33)


