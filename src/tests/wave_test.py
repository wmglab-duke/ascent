#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import scipy.signal as sg
import numpy as np
import matplotlib.pyplot as plt

dt = 0.001

t_start = 0
t_stop = 20

t_on = 1
t_off = 19

t_signal = np.arange(0, t_off - t_on, dt)
t_total = np.arange(0, t_stop, dt)

pw = 3
inter_phase = 1
frequency = 1 / 9.0


def pad(input_wave: np.ndarray, time_step: float, start_to_on: float, off_to_stop: float):
    return np.concatenate(
        ([0] * round(start_to_on / time_step),
         input_wave,
         [0] * round(off_to_stop / time_step))
    )


#%% SINUSOID
wave = np.sin(2 * np.pi * frequency * t_signal)
padded = pad(wave, dt, t_on - t_start, t_stop - t_off)
final_wave = padded
plt.plot(t_total, final_wave)
plt.show()


#%% BIPHASIC FULL DUTY
wave = sg.square(2 * np.pi * frequency * t_signal)
padded = pad(wave, dt, t_on - t_start, t_stop - t_off)
final_wave = padded
plt.plot(t_total, final_wave)
plt.show()

#%% MONOPHASIC PULSE TRAIN
wave = sg.square(2 * np.pi * frequency * t_signal, duty=pw * frequency)
clipped = np.clip(wave, 0, 1)
padded = pad(clipped, dt, t_on - t_start, t_stop - t_off)
final_wave = padded
plt.plot(t_total, final_wave)
plt.show()

#%% BIPHASIC PULSE TRAIN
positive_wave = np.clip(
    sg.square(2 * np.pi * frequency * t_signal, duty=pw * frequency),
    0, 1
)
negative_wave = np.clip(
    -sg.square(2 * np.pi * frequency * t_signal[:-round((pw + inter_phase) / dt)], duty=pw * frequency),
    -1, 0
)

padded_positive = pad(positive_wave, dt, t_on - t_start, t_stop - t_off)
padded_negative = pad(negative_wave, dt, t_on - t_start + pw + inter_phase, t_stop - t_off)

final_wave = padded_positive + padded_negative

plt.plot(t_total, final_wave)
plt.show()

#%% ensure that the wave switches to zero at end of wave
# print('pw time start: {}'.format(t_signal[0]))
# print('pw time end: {}'.format(t_signal[np.where(wave == -1)[0][0] - 1]))
# print('first zero: {}'.format(t_signal[np.where(wave == -1)[0][0]]))


