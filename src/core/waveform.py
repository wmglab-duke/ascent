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
import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sg

from src.utils import Configurable, Saveable
from src.utils.enums import Config, SetupMode, WaveformMode, WriteMode


class Waveform(Configurable, Saveable):
    """Class used to construct stimulation waveforms."""

    def __init__(self):
        """Initialize Waveform Class."""
        # set up superclasses
        Configurable.__init__(self)

        # init instance variables
        self.t_signal = None
        self.frequency = None
        self.mode = self.dt = self.start = self.on = self.off = self.stop = None

        self.wave: np.ndarray = None
        self.mode_str = None

    def init_post_config(self):
        """Initialize instance variables after configuration is loaded.

        :raises KeyError: if any required configs are missing
        :return: self
        """
        if any(config.value not in self.configs.keys() for config in (Config.MODEL, Config.SIM)):
            raise KeyError(f"Missing at least one of {Config.MODEL.value} or {Config.SIM.value} configuration.")

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
        self.dt, self.on, self.off, self.stop = (global_parameters.get(key) for key in ['dt', 'on', 'off', 'stop'])

        self.start = 0

        self.validate_times()

        return self

    def validate_times(self):
        """Check to make sure that the waveform T_ON < T_START < T_OFF < T_STOP.

        :raises ValueError: if any time params are out of order
        """
        time_params = [self.start, self.on, self.off, self.stop]
        if sorted(time_params) != time_params:
            raise ValueError("t_start t_on t_off t_stop must be in order.")

    def rho_weerasuriya(self, f=None):
        """Calculate of perineurium impedance using results from Weerasuriya 1984 (frog).

        Weerasuriya discussion indicates that Models A & B are better candidates than Models C & D, so we only
        consider the former pair.

        :param f: frequency (Hz)
        :raises NotImplementedError: if temperature is not 37C
        :return: rho [ohm-m].
        """
        temp = self.search(Config.MODEL, "temperature")  # [degC] 37 for mammalian

        # f is in [Hz]
        materials_path = os.path.join('config', 'system', 'materials.json')
        self.add(SetupMode.NEW, Config.MATERIALS, materials_path)

        if f < 10:  # stimulation for activation response, arbitrary cutoff of 10 Hz!
            if not np.isclose(temp, 37, atol=0.01):
                raise NotImplementedError("Temperature dependent perineurium not yet implemented for high frequencies")

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

        return rho  # noqa: R504

    @staticmethod
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

    def generate(self):
        """Generate the waveform.

        :raises NotImplementedError: If the waveform is not implemented.
        :return: list of 1d ndarrays, waveforms as specified by configuration.
        """
        # time values to be used for all waves
        self.t_signal = np.arange(0, self.off - self.on, self.dt)

        self.frequency = self.search(Config.SIM, 'waveform', self.mode.name, 'pulse_repetition_freq') / 1000
        if self.mode == WaveformMode.MONOPHASIC_PULSE_TRAIN:
            generated_wave = self.generate_monophasic()

        elif self.mode == WaveformMode.SINUSOID:
            generated_wave = self.generate_sinusoid()

        elif self.mode == WaveformMode.BIPHASIC_FULL_DUTY:
            generated_wave = self.generate_biphasic_fullduty()

        elif self.mode == WaveformMode.BIPHASIC_PULSE_TRAIN:
            generated_wave = self.generate_biphasic_basic()

        elif self.mode == WaveformMode.BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW:
            generated_wave = self.generate_biphasic_uneven()

        elif self.mode == WaveformMode.EXPLICIT:
            generated_wave = self.generate_explicit()

        else:
            raise NotImplementedError("WaveformMode chosen not yet implemented.")

        self.wave = generated_wave

        return self

    def generate_biphasic_uneven(self):
        """Generate a biphasic pulse train with uneven pulse widths.

        :raises ValueError: If the timestep is too long for the waveform.
        :return: generated waveform
        """
        pw1 = self.search(Config.SIM, 'waveform', self.mode_str, 'pulse_width_1')
        pw2 = self.search(Config.SIM, 'waveform', self.mode_str, 'pulse_width_2')
        if self.dt > pw1 or self.dt > pw2:
            raise ValueError(
                "Timestep self.dt is longer than BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW pw1 or pw2 indicated in Sim."
            )
        # ensure fits within period
        if (pw1 + pw2) > 1.0 / self.frequency:
            raise ValueError("Pulse is longer than period (2x for biphasic).")
        # loop on inter phase
        inter_phase = self.search(Config.SIM, 'waveform', self.mode_str, 'inter_phase')
        if self.dt > inter_phase != 0:
            raise ValueError(
                "Timestep self.dt is longer than "
                "BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW inter_phase indicated in Sim."
            )
        # ensures fits within period
        if (pw1 + pw2) + inter_phase > 1.0 / self.frequency:
            raise ValueError("2*Pulse + Interphase is longer than period.")
        positive_wave = np.clip(
            sg.square(2 * np.pi * self.frequency * self.t_signal, duty=(pw1 - self.dt) * self.frequency),
            0,
            1,
        )
        negative_wave = np.clip(
            -sg.square(
                2 * np.pi * self.frequency * self.t_signal[: -round((pw1 + inter_phase) / self.dt)],
                duty=(pw2 - self.dt) * self.frequency,
            ),
            -1,
            0,
        )
        padded_positive = self.pad(positive_wave, self.dt, self.on - self.start, self.stop - self.off)
        padded_negative = self.pad(
            negative_wave, self.dt, self.on - self.start + pw1 + inter_phase - self.dt, self.stop - self.off + self.dt
        )
        # q-balanced
        if pw1 < pw2:
            amp1 = 1
            amp2 = (pw1 * amp1) / pw2
        else:
            amp2 = 1
            amp1 = (pw2 * amp2) / pw1

        return amp1 * padded_positive + amp2 * padded_negative

    def generate_monophasic(self):
        """Generate a monophasic pulse train.

        :raises ValueError: if waveform parameters are invalid
        :return: generated waveform
        """
        pw = self.search(Config.SIM, 'waveform', self.mode_str, 'pulse_width')
        if self.dt > pw:
            raise ValueError("Timestep self.dt is longer than MONOPHASIC_PULSE_TRAIN pulse-width indicated in Sim.")
        # ensure pulse fits in period
        if pw > 1.0 / self.frequency:
            raise ValueError("Pulse is longer than period (2x for biphasic).")
        wave = sg.square(2 * np.pi * self.frequency * self.t_signal, duty=(pw - self.dt) * self.frequency)
        clipped = np.clip(wave, 0, 1)
        return self.pad(clipped, self.dt, self.on - self.start, self.stop - self.off)

    def generate_sinusoid(self):
        """Generate a sinusoid.

        :raises ValueError: If the timestep is too long for the waveform.
        :return: generated waveform
        """
        if self.dt > 1.0 / self.frequency:
            raise ValueError(
                "Timestep self.dt is longer than SINUSOID period indicated in Sim by pulse_repetition_freq."
            )
        wave = np.sin(2 * np.pi * self.frequency * self.t_signal)
        return self.pad(wave, self.dt, self.on - self.start, self.stop - self.off)

    def generate_biphasic_fullduty(self):
        """Generate a biphasic pulse train with full duty cycle.

        :raises ValueError: for incorrect timestep.
        :return: generated waveform
        """
        if self.dt > 1.0 / self.frequency:
            raise ValueError(
                "Timestep self.dt is longer than BIPHASIC_FULL_DUTY period indicated in Sim by pulse_repetition_freq."
            )
        wave = sg.square(2 * np.pi * self.frequency * self.t_signal)
        return self.pad(wave, self.dt, self.on - self.start, self.stop - self.off)

    def generate_biphasic_basic(self):
        """Generate a biphasic pulse train with basic parameters.

        :raises ValueError: If parameters are invalid
        :return: generated waveform
        """
        pw = self.search(Config.SIM, 'waveform', self.mode_str, 'pulse_width')
        if self.dt > pw:
            raise ValueError("Timestep self.dt is longer than BIPHASIC_PULSE_TRAIN pulse-width indicated in Sim.")
        # ensure fits within period
        if 2 * pw > 1.0 / self.frequency:
            raise ValueError("Pulse is longer than period (2x for biphasic).")
        # loop on inter phase
        inter_phase = self.search(Config.SIM, 'waveform', self.mode_str, 'inter_phase')
        if self.dt > inter_phase != 0:
            raise ValueError("Timestep self.dt is longer than BIPHASIC_PULSE_TRAIN inter_phase indicated in Sim.")
        # ensures fits within period
        if (2 * pw) + inter_phase > 1.0 / self.frequency:
            raise ValueError("2*Pulse + Interphase is longer than period.")
        positive_wave = np.clip(
            sg.square(2 * np.pi * self.frequency * self.t_signal, duty=(pw - self.dt) * self.frequency),
            0,
            1,
        )
        negative_wave = np.clip(
            -sg.square(
                2 * np.pi * self.frequency * self.t_signal[: -round((pw + inter_phase) / self.dt)],
                duty=(pw - self.dt) * self.frequency,
            ),
            -1,
            0,
        )
        padded_positive = self.pad(positive_wave, self.dt, self.on - self.start, self.stop - self.off)
        padded_negative = self.pad(
            negative_wave, self.dt, self.on - self.start + pw + inter_phase - self.dt, self.stop - self.off + self.dt
        )
        return padded_positive + padded_negative

    def generate_explicit(self):
        """Generate an explicit waveform.

        :raises TypeError: if wave repeats is not an int
        :raises ValueError: If number of wave repeats does not fit between wave on and off
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
            warnings.warn(warning_str, stacklevel=2)

            period_explicit = dt_explicit * len(explicit_wave)
            n_samples_resampled = round(period_explicit / self.dt)

            # need to convert input explicit waveform to 'global' time discretization as used by NEURON
            signal = sg.resample(explicit_wave, n_samples_resampled)

        else:
            signal = explicit_wave
        # repeats?
        repeats = self.search(Config.SIM, 'waveform', WaveformMode.EXPLICIT.name, 'period_repeats')
        if isinstance(repeats, int):
            raise TypeError("Number of repeats for explicit wave must be an integer value")
        if repeats > 1:
            signal = np.tile(signal, repeats)
        # if number of repeats cannot fit in off-on interval, error
        if self.dt * len(signal) > (self.off - self.on):
            raise ValueError("Number of repeats for explicit wave does not fit in global.off - global.on in Sim config")
        # pad with zeros for: time before on, time after off
        return self.pad(
            signal,
            self.dt,
            self.on - self.start,
            self.stop - (self.on + self.dt * len(signal)),
        )

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
        digits = self.search(Config.SIM, 'waveform', self.mode_str, 'digits')

        dt_all, dt_post = num_digits_precision(self.dt)
        stop_all, stop_post = num_digits_precision(self.stop)

        with open(path + WriteMode.file_endings.value[mode.value], "ab") as f:
            np.savetxt(f, [self.dt], fmt=f'%{dt_all - dt_post}.{dt_post}f')

        with open(path + WriteMode.file_endings.value[mode.value], "ab") as f:
            np.savetxt(f, [self.stop], fmt=f'%{stop_all - stop_post}.{stop_post}f')

        with open(path + WriteMode.file_endings.value[mode.value], "ab") as f:
            np.savetxt(f, self.wave, fmt=f'%.{digits}f')

        f.close()

        return self


def num_digits_precision(x):
    """Return the number of digits and the scale of the number.

    :param x: number
    :return: number of digits, scale
    """
    # integral component
    intx = math.floor(abs(x))
    if intx == 0:
        n_int = 0
    else:
        n_int = math.floor(math.log10(intx)) + 1

    # fractional component
    fracx = abs(x) - intx
    if fracx == 0:
        n_prec = 0
    else:
        n_prec = 1
        while ((10**n_prec) * fracx) % 1 > 0:
            n_prec += 1
    n_digits = n_int + n_prec

    return n_digits, n_prec
