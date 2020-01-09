#!/usr/bin/env python3.7

# builtins
from typing import List
import os

# packages
import numpy as np
import scipy.signal as sg

# access
from src.utils import Exceptionable, Configurable, Saveable
from src.utils.enums import *


class Waveform(Exceptionable, Configurable, Saveable):
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
        self.modes = \
            self.dt = \
            self.t_start = \
            self.t_on = \
            self.t_off = \
            self.t_stop = \
            self.time_unit = \
            self.frequency_unit = None

    def init_post_config(self):

        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(39)

        # get mode
        self.modes = self.search_multi_mode(Config.SIM, WaveformMode)

        # get global vars data
        global_parameters: dict = self.search(Config.SIM,
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

    def rho_weerasuriya(self, f=None, all_configs=None):
        """
        Calculation of perineurium impedance using results from Weerasuriya 1984 (frog). Weerasuriya discussion
        indicates that Models A & B are better candidates than Models C & D, so we only consider the former pair.
        :return: rho [ohm-m]
        """

        if self.search(Config.MODEL, "temperature", "unit") != "celsius":
            self.throw(46)

        temp = int(self.search(Config.MODEL, "temperature", "value"))  # [degC] 37 for mammalian

        # f is in [Hz]
        if f < 10:                                  # stimulation for activation response, arbitrary cutoff of 10 Hz!
            if temp != 37:
                self.throw(47)

            materials_path = os.path.join('config', 'system', 'materials.json')
            materials_config = self.load(materials_path)
            rho = eval(materials_config['conductivities']['weerasuriya_perineurium_DC']['value'])  # [ohm-m] // TODO

        else:                                       # stimulation at higher frequency for block
            w = 2*np.pi*f

            # Parameter values from Tables II & III
            # [TableII, TableIII]
            # R in ohm*cm^2
            # C in uF/cm^2
            r1a = np.mean([385, 493])
            r2a = np.mean([1271, 2168])
            c1a = np.mean([0.081, 0.075])*10**-6   # [uF/cm^2 -> F/cm^2]
            c2a = np.mean([2.71, 5.12])*10**-6     # [uF/cm^2 -> F/cm^2]

            r1b = np.mean([108, 155])
            r2b = np.mean([277, 338])
            c1b = np.mean([43.7, 202])*10**-6      # [uF/cm^2 -> F/cm^2]
            c2b = np.mean([0.088, 0.083])*10**-6   # [uF/cm^2 -> F/cm^2]

            r1c = np.mean([1053, 1587])
            r2c = np.mean([385, 493])
            c1c = np.mean([0.106, 0.104])*10**-6   # [uF/cm^2 -> F/cm^2]
            c2c = np.mean([2.79, 5.19])*10**-6     # [uF/cm^2 -> F/cm^2]

            r1d = np.mean([87, 102])
            r2d = np.mean([298, 390])
            c1d = np.mean([45.2, 201])*10**-6      # [uF/cm^2 -> F/cm^2]
            c2d = np.mean([0.081, 0.075])*10**-6   # [uF/cm^2 -> F/cm^2]

            # Model A: Z = R1 // 1/(jwC1) // [R2 + 1/jwC2]
            za = (1/r1a + 1j*w*c1a + 1/(r2a + 1/(1j*w*c2a)))**(-1)
            za_mag = abs(za)
            za_mag = za_mag / 100**2               # [ohm-cm^2 -> ohm-m^2]
            sigmas_mag = 1 / za_mag                # [S/m^2]

            # Model B: Z = [R1 // 1/(jwC1)] + [R2 // 1/(jwC2)]
            zb = (1/r1b + 1j*w*c1b)**(-1) + (1/r2b + 1j*w*c2b)**(-1)
            zb_mag = abs(zb)
            zb_mag = zb_mag / 100**2               # [ohm-cm^2 -> ohm-m^2]
            sigmas_mag = 1/zb_mag                  # [S/m^2]

            # Model C: Z = R2 // [ 1/(jwC2) + [R1 // 1/(jwC1)] ]
            tmp = (1/r1c + 1j*w*c1c)**(-1)         # [R1 // 1/(jwC1)]
            tmp = 1/(1j*w*c2c) + tmp               # Right-hand branch: [ 1/(jwC2) + [R1 // 1/(jwC1)] ]
            zc = (1/r2c + 1/tmp)**(-1)
            zc_mag = abs(zc)
            zc_mag = zc_mag / 100**2               # [ohm-cm^2 -> ohm-m^2]
            sigmas_mag = 1/zc_mag                  # [S/m^2]

            # Model D: Z = (1/(jwC2)) // [ R2 + [R1 // 1/(jwC1)] ]
            tmp = (1/r1d + 1j*w*c1d)**(-1)         # [R1 // 1/(jwC1)]
            tmp = r2d + tmp                        # Right-hand branch: [ R2 + [R1 // 1/(jwC1)] ]
            zd = (1j*w*c2d + 1/tmp)**(-1)
            zd_mag = abs(zd)
            zd_mag = zd_mag / 100**2               # [ohm-cm^2 -> ohm-m^2]
            sigmas_mag = 1/zd_mag                  # [S/m^2]

            # Mean of models A & B
            # Discussion indicates that models A & B are more likely candidates
            rs21 = np.mean([za_mag, zb_mag])       # [ohm-m^2]

            # Adjust for temperature - Use Q10 of 1.5, Shift to 37degC
            temp_room = 21                         # [degC]
            q10 = 1.5
            rs37 = ((1/rs21)*(q10**((temp-temp_room)/10)))**(-1)  # [Ohm-m^2]

            # Convert to constant rho
            thk_weerasuriya = 0.00002175           # [m]
            rho = rs37/thk_weerasuriya             # [ohm-m]

        return rho                                 # [ohm-m]

    def generate(self) -> List[np.ndarray]:
        """
        :return: list of 1d ndarrays, waveforms as specified by configuration
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

            # for ease of parameter src later on
            path_to_specific_parameters = [WaveformMode.parameters, str(mode).split('.')[-1]]

            # loop on frequency (all modes have property)... WITHIN THIS LOOP: "switch" on wave type
            for frequency in self.search(Config.MODEL, *path_to_specific_parameters, 'frequency'):

                if mode == WaveformMode.MONOPHASIC_PULSE_TRAIN:

                    # loop on pulse width
                    for pw in self.search(Config.SIM, *path_to_specific_parameters, 'pulse_width'):

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
                    for pw in self.search(Config.SIM, *path_to_specific_parameters, 'pulse_width'):

                        # ensure fits within period
                        if 2 * pw > 1.0 / frequency:
                            self.throw(35)

                        # loop on inter phase
                        for inter_phase in self.search(Config.SIM, *path_to_specific_parameters, 'inter_phase'):

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








