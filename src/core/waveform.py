#!/usr/bin/env python3.7

# builtins
from typing import List

# packages
import numpy as np
import scipy.signal as sg

# SPARCpy
from src.utils import Exceptionable, Configurable
from src.utils.enums import *


class Waveform(Exceptionable, Configurable):

    def __init__(self, master_config: dict, exceptions_config: list):
        """
        :param master_config:
        :param exceptions_config:
        """

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
        """
        Checks to make sure that the waveform T_ON < T_START < T_OFF < T_STOP
        """

        time_params = [self.t_start, self.t_on, self.t_off, self.t_stop]
        if time_params.sort() != time_params:
            self.throw(32)

        if self.dt > min(time_params):
            self.throw(33)

    def generate(self) -> List[np.ndarray]:
        """
        :return: list of 1d ndarrays, waveforms as specified by master configuration
        """

        # helper function to pad the start and end of signal with zeroes
        def pad(input_wave: np.ndarray, time_step: float, start_to_on: float, off_to_stop: float) -> np.ndarray:
            """
            :param input_wave: wave (1d np.ndarray) to pad
            :param time_step: effective dt
            :param start_to_on: beginning pad length
            :param off_to_stop: end pad length
            :return: the padded wave (1d np.ndarray)
            """
            return np.concatenate(
                ([0] * round(start_to_on / time_step),
                 input_wave,
                 [0] * round(off_to_stop / time_step))
            )

        # init empty list of waves
        waves: List[np.ndarray] = []

        # time values to be used for all waves
        t_signal = np.arange(0, self.t_off - self.t_on, self.dt)

        # outermost loop on mode
        for mode in self.modes:

            # for ease of parameter access later on
            path_to_specific_parameters = [WaveformMode.parameters, str(mode).split('.')[-1]]

            # loop on frequency (all modes have property)... WITHIN THIS LOOP: "switch" on wave type
            for frequency in self.search(ConfigKey.MASTER, *path_to_specific_parameters, 'frequency'):

                if mode == WaveformMode.MONOPHASIC_PULSE_TRAIN:

                    # loop on pulse width
                    for pw in self.search(ConfigKey.MASTER, *path_to_specific_parameters, 'pulse_width'):

                        # ensure pulse fits in period
                        if pw > 1.0 / frequency:
                            self.throw(35)

                        wave = sg.square(2 * np.pi * frequency * t_signal, duty=pw * frequency)
                        clipped = np.clip(wave, 0, 1)
                        padded = pad(clipped, self.dt, self.t_on - self.t_start, self.t_stop - self.t_off)
                        waves.append(padded)

                elif mode == WaveformMode.SINUSOID:
                    wave = np.sin(2 * np.pi * frequency * t_signal)
                    padded = pad(wave, self.dt, self.t_on - self.t_start, self.t_stop - self.t_off)
                    waves.append(padded)

                elif mode == WaveformMode.BIPHASIC_FULL_DUTY:
                    wave = sg.square(2 * np.pi * frequency * t_signal)
                    padded = pad(wave, self.dt, self.t_on - self.t_start, self.t_stop - self.t_off)
                    waves.append(padded)

                elif mode == WaveformMode.BIPHASIC_PULSE_TRAIN:

                    # loop on pulse width
                    for pw in self.search(ConfigKey.MASTER, *path_to_specific_parameters, 'pulse_width'):

                        # ensure fits within period
                        if 2 * pw > 1.0 / frequency:
                            self.throw(35)

                        # loop on inter phase
                        for inter_phase in self.search(ConfigKey.MASTER, *path_to_specific_parameters, 'inter_phase'):

                            # ensures fits within period
                            if (2 * pw) + inter_phase > 1.0 / frequency:
                                self.throw(36)

                            positive_wave = np.clip(
                                sg.square(2 * np.pi * frequency * t_signal, duty=pw * frequency),
                                0, 1
                            )
                            negative_wave = np.clip(
                                -sg.square(2 * np.pi * frequency * t_signal[:-round((pw + inter_phase) / self.dt)],
                                           duty=pw * frequency),
                                -1, 0
                            )

                            padded_positive = pad(positive_wave,
                                                  self.dt,
                                                  self.t_on - self.t_start,
                                                  self.t_stop - self.t_off)

                            padded_negative = pad(negative_wave,
                                                  self.dt,
                                                  self.t_on - self.t_start + pw + inter_phase,
                                                  self.t_stop - self.t_off)

                            waves.append(padded_positive + padded_negative)

                else:
                    self.throw(34)

        return waves








