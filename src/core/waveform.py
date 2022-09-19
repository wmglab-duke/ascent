#!/usr/bin/env python3.7

"""Defines Waveform class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""


import csv
import math
import os
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sg

from src.utils import Configurable, Exceptionable, Saveable
from src.utils.enums import Config, SetupMode, WaveformMode, WriteMode


class Waveform(Exceptionable, Configurable, Saveable):
    """Required (Config.) JSON's: MODEL SIM."""

    def __init__(self, exceptions_config: list):
        """:param exceptions_config: preloaded exceptions.json data."""
        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # init instance variables
        self.mode = self.dt = self.start = self.on = self.off = self.stop = None

        self.wave: np.ndarray = None
        self.mode_str = None

    def init_post_config(self):
        """Initialize instance variables after configuration is loaded.

        :return: self
        """
        if any([config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)]):
            self.throw(72)

        # get mode
        self.mode_str = [
            key for key in self.search(Config.SIM, 'waveform').keys() if key != 'global' and key != 'plot'
        ][0]
        self.mode = [mode for mode in WaveformMode if str(mode).split('.')[-1] == self.mode_str][0]

        # get global vars data
        global_parameters: dict = self.search(
            Config.SIM, WaveformMode.config.value, WaveformMode.global_parameters.value
        )

        # unpack global variables
        self.dt, self.on, self.off, self.stop = [global_parameters.get(key) for key in ['dt', 'on', 'off', 'stop']]

        self.start = 0

        self.validate_times()

        return self

    def validate_times(self):
        """Check to make sure that the waveform T_ON < T_START < T_OFF < T_STOP."""
        time_params = [self.start, self.on, self.off, self.stop]
        if sorted(time_params) != time_params:
            self.throw(32)

    def rho_weerasuriya(self, f=None):
        """Calculate of perineurium impedance using results from Weerasuriya 1984 (frog).

        Weerasuriya discussion indicates that Models A & B are better candidates than Models C & D, so we only
        consider the former pair.

        :param f: frequency (Hz)
        :return: rho [ohm-m].
        """
        temp = self.search(Config.MODEL, "temperature")  # [degC] 37 for mammalian

        # f is in [Hz]
        materials_path = os.path.join('config', 'system', 'materials.json')
        self.add(SetupMode.NEW, Config.MATERIALS, materials_path)

        if f < 10:  # stimulation for activation response, arbitrary cutoff of 10 Hz!
            if not np.isclose(temp, 37, atol=0.01):
                self.throw(47)

            self.load(materials_path)
            peri_conductivity = self.search(
                Config.MATERIALS,
                'conductivities',
                'weerasuriya_perineurium_DC',
                'value',
            )
            rho = 1 / eval(peri_conductivity)  # [S/m] -> [ohm-m]

        else:  # stimulation at higher frequency for block
            w = 2 * np.pi * f

            # Parameter values from Tables II & III [TableII, TableIII]
            # R in ohm*cm^2
            # C in uF/cm^2
            r1a = np.mean([385, 493])
            r2a = np.mean([1271, 2168])
            c1a = np.mean([0.081, 0.075]) * 10**-6  # [uF/cm^2 -> F/cm^2]
            c2a = np.mean([2.71, 5.12]) * 10**-6  # [uF/cm^2 -> F/cm^2]

            r1b = np.mean([108, 155])
            r2b = np.mean([277, 338])
            c1b = np.mean([43.7, 202]) * 10**-6  # [uF/cm^2 -> F/cm^2]
            c2b = np.mean([0.088, 0.083]) * 10**-6  # [uF/cm^2 -> F/cm^2]

            r1c = np.mean([1053, 1587])
            r2c = np.mean([385, 493])
            c1c = np.mean([0.106, 0.104]) * 10**-6  # [uF/cm^2 -> F/cm^2]
            c2c = np.mean([2.79, 5.19]) * 10**-6  # [uF/cm^2 -> F/cm^2]

            r1d = np.mean([87, 102])
            r2d = np.mean([298, 390])
            c1d = np.mean([45.2, 201]) * 10**-6  # [uF/cm^2 -> F/cm^2]
            c2d = np.mean([0.081, 0.075]) * 10**-6  # [uF/cm^2 -> F/cm^2]

            # Model A: Z = R1 // 1/(jwC1) // [R2 + 1/jwC2]
            za = (1 / r1a + 1j * w * c1a + 1 / (r2a + 1 / (1j * w * c2a))) ** (-1)
            za_mag = abs(za)
            za_mag = za_mag / 100**2  # [ohm-cm^2 -> ohm-m^2]
            # The equation: sigmas_mag = 1 / za_mag  # [S/m^2]

            # Model B: Z = [R1 // 1/(jwC1)] + [R2 // 1/(jwC2)]
            zb = (1 / r1b + 1j * w * c1b) ** (-1) + (1 / r2b + 1j * w * c2b) ** (-1)
            zb_mag = abs(zb)
            zb_mag = zb_mag / 100**2  # [ohm-cm^2 -> ohm-m^2]
            # The equation: sigmas_mag = 1 / zb_mag  # [S/m^2]

            # Model C: Z = R2 // [ 1/(jwC2) + [R1 // 1/(jwC1)] ]
            tmp = (1 / r1c + 1j * w * c1c) ** (-1)  # [R1 // 1/(jwC1)]
            tmp = 1 / (1j * w * c2c) + tmp  # Right-hand branch: [ 1/(jwC2) + [R1 // 1/(jwC1)] ]
            zc = (1 / r2c + 1 / tmp) ** (-1)
            zc_mag = abs(zc)
            zc_mag = zc_mag / 100**2  # [ohm-cm^2 -> ohm-m^2]
            # The equation: sigmas_mag = 1 / zc_mag  # [S/m^2]

            # Model D: Z = (1/(jwC2)) // [ R2 + [R1 // 1/(jwC1)] ]
            tmp = (1 / r1d + 1j * w * c1d) ** (-1)  # [R1 // 1/(jwC1)]
            tmp = r2d + tmp  # Right-hand branch: [ R2 + [R1 // 1/(jwC1)] ]
            zd = (1j * w * c2d + 1 / tmp) ** (-1)
            zd_mag = abs(zd)
            zd_mag = zd_mag / 100**2  # [ohm-cm^2 -> ohm-m^2]
            # The equation: sigmas_mag = 1 / zd_mag  # [S/m^2]

            # Mean of models A & B
            # Discussion indicates that models A & B are more likely candidates
            rs21 = np.mean([za_mag, zb_mag])  # [ohm-m^2]

            # Adjust for temperature - Use Q10 of 1.5, Shift to 37degC
            temp_room = 21  # [degC]
            q10 = 1.5
            rs37 = ((1 / rs21) * (q10 ** ((temp - temp_room) / 10))) ** (-1)  # [Ohm-m^2]

            # Convert to constant rho
            thk_weerasuriya = 0.00002175  # [m]
            rho = rs37 / thk_weerasuriya  # [ohm-m]

        return rho  # [ohm-m]

    def generate(self):
        """:return: list of 1d ndarrays, waveforms as specified by configuration."""
        # helper function to pad the start and end of signal with zeroes
        def pad(
            input_wave: np.ndarray,
            time_step: float,
            start_to_on: float,
            off_to_stop: float,
        ) -> np.ndarray:
            """Pad the start and end of signal with zeroes.

            :param input_wave: wave (1d np.ndarray) to pad
            :param time_step: effective dt
            :param start_to_on: beginning pad length
            :param off_to_stop: end pad length
            :return: the padded wave (1d np.ndarray)
            """
            return np.concatenate(
                (
                    [0] * (round(start_to_on / time_step) - 1),
                    input_wave,
                    [0] * (round(off_to_stop / time_step) - 1),
                )
            )

        # time values to be used for all waves
        t_signal = np.arange(0, self.off - self.on, self.dt)

        # for ease of parameter src later on
        path_to_specific_parameters = ['waveform', self.mode_str]

        frequency = self.search(Config.SIM, 'waveform', self.mode.name, 'pulse_repetition_freq') / 1000  # scale for ms

        if self.mode == WaveformMode.MONOPHASIC_PULSE_TRAIN:

            generated_wave = self.generate_monophasic(frequency, pad, path_to_specific_parameters, t_signal)

        elif self.mode == WaveformMode.SINUSOID:
            generated_wave = self.generate_sinusoid(frequency, pad, t_signal)

        elif self.mode == WaveformMode.BIPHASIC_FULL_DUTY:

            generated_wave = self.generate_biphasic_fullduty(frequency, pad, t_signal)

        elif self.mode == WaveformMode.BIPHASIC_PULSE_TRAIN:

            generated_wave = self.generate_biphasic_basic(frequency, pad, path_to_specific_parameters, t_signal)

        elif self.mode == WaveformMode.BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW:

            generated_wave = self.generate_biphasic_uneven(frequency, pad, path_to_specific_parameters, t_signal)

        elif self.mode == WaveformMode.EXPLICIT:
            generated_wave = self.generate_explicit(pad)

        else:
            self.throw(34)

        self.wave = generated_wave

        return self

    def generate_biphasic_uneven(self, frequency, pad, path_to_specific_parameters, t_signal):
        """Generate a biphasic pulse train with uneven pulse widths.

        :param frequency: frequency of the pulse train [Hz]
        :param pad: helper function to pad the start and end of signal with zeroes
        :param path_to_specific_parameters: path to the specific parameters for this waveform in Sim config
        :param t_signal: time values to be used for all waves
        :return: generated waveform
        """
        pw1 = self.search(Config.SIM, *path_to_specific_parameters, 'pulse_width_1')
        pw2 = self.search(Config.SIM, *path_to_specific_parameters, 'pulse_width_2')
        if self.dt > pw1:
            self.throw(89)
        if self.dt > pw2:
            self.throw(90)
        # ensure fits within period
        if (pw1 + pw2) > 1.0 / frequency:
            self.throw(35)
        # loop on inter phase
        inter_phase = self.search(Config.SIM, *path_to_specific_parameters, 'inter_phase')
        if self.dt > inter_phase != 0:
            self.throw(91)
        # ensures fits within period
        if (pw1 + pw2) + inter_phase > 1.0 / frequency:
            self.throw(36)
        positive_wave = np.clip(
            sg.square(2 * np.pi * frequency * t_signal, duty=(pw1 - self.dt) * frequency),
            0,
            1,
        )
        negative_wave = np.clip(
            -sg.square(
                2 * np.pi * frequency * t_signal[: -round((pw1 + inter_phase) / self.dt)],
                duty=(pw2 - self.dt) * frequency,
            ),
            -1,
            0,
        )
        padded_positive = pad(positive_wave, self.dt, self.on - self.start, self.stop - self.off)
        padded_negative = pad(
            negative_wave, self.dt, self.on - self.start + pw1 + inter_phase - self.dt, self.stop - self.off + self.dt
        )
        # q-balanced
        if pw1 < pw2:
            amp1 = 1
            amp2 = (pw1 * amp1) / pw2
        else:
            amp2 = 1
            amp1 = (pw2 * amp2) / pw1

        wave = amp1 * padded_positive + amp2 * padded_negative
        return wave

    def generate_monophasic(self, frequency, pad, path_to_specific_parameters, t_signal):
        """Generate a monophasic pulse train.

        :param frequency: frequency of the pulse train [Hz]
        :param pad: helper function to pad the start and end of signal with zeroes
        :param path_to_specific_parameters: path to the specific parameters for this waveform in Sim config
        :param t_signal: time values to be used for all waves
        :return: generated waveform
        """
        pw = self.search(Config.SIM, *path_to_specific_parameters, 'pulse_width')
        if self.dt > pw:
            self.throw(84)
        # ensure pulse fits in period
        if pw > 1.0 / frequency:
            self.throw(35)
        wave = sg.square(2 * np.pi * frequency * t_signal, duty=(pw - self.dt) * frequency)
        clipped = np.clip(wave, 0, 1)
        padded = pad(clipped, self.dt, self.on - self.start, self.stop - self.off)
        wave = padded
        return wave

    def generate_sinusoid(self, frequency, pad, t_signal):
        """Generate a sinusoid.

        :param frequency: frequency of the sinusoid [Hz]
        :param pad: helper function to pad the start and end of signal with zeroes
        :param t_signal: time values to be used for all waves
        :return: generated waveform
        """
        if self.dt > 1.0 / frequency:
            self.throw(85)
        wave = np.sin(2 * np.pi * frequency * t_signal)
        padded = pad(wave, self.dt, self.on - self.start, self.stop - self.off)
        wave = padded
        return wave

    def generate_biphasic_fullduty(self, frequency, pad, t_signal):
        """Generate a biphasic pulse train with full duty cycle.

        :param frequency: frequency of the pulse train [Hz]
        :param pad: helper function to pad the start and end of signal with zeroes
        :param t_signal: time values to be used for all waves
        :return: generated waveform
        """
        if self.dt > 1.0 / frequency:
            self.throw(86)
        wave = sg.square(2 * np.pi * frequency * t_signal)
        padded = pad(wave, self.dt, self.on - self.start, self.stop - self.off)
        wave = padded
        return wave

    def generate_biphasic_basic(self, frequency, pad, path_to_specific_parameters, t_signal):
        """Generate a biphasic pulse train with basic parameters.

        :param frequency: frequency of the pulse train [Hz]
        :param pad: helper function to pad the start and end of signal with zeroes
        :param path_to_specific_parameters: path to the specific parameters for this waveform in Sim config
        :param t_signal: time values to be used for all waves
        :return: generated waveform
        """
        pw = self.search(Config.SIM, *path_to_specific_parameters, 'pulse_width')
        if self.dt > pw:
            self.throw(87)
        # ensure fits within period
        if 2 * pw > 1.0 / frequency:
            self.throw(35)
        # loop on inter phase
        inter_phase = self.search(Config.SIM, *path_to_specific_parameters, 'inter_phase')
        if self.dt > inter_phase != 0:
            self.throw(88)
        # ensures fits within period
        if (2 * pw) + inter_phase > 1.0 / frequency:
            self.throw(36)
        positive_wave = np.clip(
            sg.square(2 * np.pi * frequency * t_signal, duty=(pw - self.dt) * frequency),
            0,
            1,
        )
        negative_wave = np.clip(
            -sg.square(
                2 * np.pi * frequency * t_signal[: -round((pw + inter_phase) / self.dt)],
                duty=(pw - self.dt) * frequency,
            ),
            -1,
            0,
        )
        padded_positive = pad(positive_wave, self.dt, self.on - self.start, self.stop - self.off)
        padded_negative = pad(
            negative_wave, self.dt, self.on - self.start + pw + inter_phase - self.dt, self.stop - self.off + self.dt
        )
        wave = padded_positive + padded_negative
        return wave

    def generate_explicit(self, pad):
        """Generate an explicit waveform.

        :param pad: helper function to pad the start and end of signal with zeroes
        :return: generated waveform
        """
        path_to_wave = os.path.join(
            'config',
            'user',
            'waveforms',
            f"{str(self.search(Config.SIM, 'waveform', WaveformMode.EXPLICIT.name, 'index'))}.dat",
        )
        # read in wave from file
        explicit_wave = []
        with open(os.path.join(path_to_wave)) as f:
            reader = csv.reader(f)
            for row in reader:
                explicit_wave.append(float(row[0]))
        # first element in file is dt of recorded/explicit signal provided to the program
        dt_explicit = explicit_wave.pop(0)
        dt_atol = self.search(Config.SIM, 'waveform', WaveformMode.EXPLICIT.name, 'dt_atol')
        if not np.isclose(dt_explicit, self.dt, atol=dt_atol):
            waveform_index = self.search(
                Config.SIM,
                'waveform',
                WaveformMode.EXPLICIT.name,
                'index',
            )
            warning_str = (
                f'\n Timestep provided: {dt_explicit} (first line in waveform file in '
                f'config/user/waveforms/{waveform_index}.dat) \n does not match "dt" in "global" '
                f'Sim parameters for time discretization in '
                f'NEURON: {self.dt} \n based on set "dt_atol" parameter in Sim: {dt_atol}. \n Altering your input '
                'waveform to fit NEURON time '
                'discretization.'
            )
            warnings.warn(warning_str)

            period_explicit = dt_explicit * len(explicit_wave)
            n_samples_resampled = round(period_explicit / self.dt)

            # need to convert input explicit waveform to 'global' time discretization as used by NEURON
            signal = sg.resample(explicit_wave, n_samples_resampled)

        else:
            signal = explicit_wave
        # repeats?
        repeats = self.search(Config.SIM, 'waveform', WaveformMode.EXPLICIT.name, 'period_repeats')
        if type(repeats) is not int:
            self.throw(73)
        if repeats > 1:
            signal = np.tile(signal, repeats)
        # if number of repeats cannot fit in off-on interval, error
        if self.dt * len(signal) > (self.off - self.on):
            self.throw(74)
        # pad with zeros for: time before on, time after off
        padded = pad(
            signal,
            self.dt,
            self.on - self.start,
            self.stop - (self.on + self.dt * len(signal)),
        )
        wave = padded
        return wave

    def plot(self, ax: plt.Axes = None, final: bool = False, path: str = None, plt_kwargs: dict = None):
        """Plot the waveform.

        :param ax: axes to plot on
        :param final: Whether to display/save the plot
        :param path: Path to save the plot if final is True
        :param plt_kwargs: Keyword arguments to pass to matplotlib.pyplot.plot
        """
        fig = plt.figure()

        if ax is None:
            ax = plt.gca()
        if plt_kwargs is None:
            plt_kwargs = {}

        ax.plot(np.linspace(self.start, self.dt * len(self.wave), len(self.wave)), self.wave, **plt_kwargs)
        ax.set_ylabel('Normalized magnitude')
        ax.set_xlabel('Time step')
        ax.set_title('Waveform generated from user parameters in sim.json')

        if final:
            if path is None:
                plt.show()
            else:
                plt.savefig(path, dpi=300)
                plt.close(fig)

    def write(self, mode: WriteMode, path: str):
        """Write the waveform to a file.

        :param mode: usually DATA
        :param path: path to write to
        :return: self
        """
        path_to_specific_parameters = ['waveform', self.mode_str]
        digits = self.search(Config.SIM, *path_to_specific_parameters, 'digits')

        dt_all, dt_post = precision_and_scale(self.dt)
        stop_all, stop_post = precision_and_scale(self.stop)

        with open(path + WriteMode.file_endings.value[mode.value], "ab") as f:
            np.savetxt(f, [self.dt], fmt=f'%{dt_all-dt_post}.{dt_post}f')

        with open(path + WriteMode.file_endings.value[mode.value], "ab") as f:
            np.savetxt(f, [self.stop], fmt=f'%{stop_all-stop_post}.{stop_post}f')

        with open(path + WriteMode.file_endings.value[mode.value], "ab") as f:
            np.savetxt(f, self.wave, fmt=f'%.{digits}f')

        f.close()

        return self


def precision_and_scale(x):
    """Return the number of digits and the scale of the number.

    :param x: number
    :return: number of digits, scale
    """
    max_digits = sys.float_info.dig
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return magnitude, 0
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return magnitude + scale, scale
