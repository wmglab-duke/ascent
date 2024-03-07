"""Plot a video over time of Ve over the length of a fiber.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

This script requires that you have saved Vm at all locs (under time).
RUN THIS FROM REPOSITORY ROOT
"""

import os
import shutil
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

samples = [200, 201, 205]
models = [0]
sims = [0, 1, 2]
inner = 0
fiber = 0
n_sims = [0, 1, 2]
amp = 0

outpath = 'out/analysis/videos'


# define initializer function for animation
def _init():
    """Initialize the animation."""  # noqa: DAR
    flat_data = data.flatten()
    ax.set_ylim(np.min(flat_data), np.max(flat_data))
    return (ln,)


# define update function for each frame of animation
def _update(frame):
    """Update the animation."""  # noqa: DAR
    time_text.set_text('time: ' + str(data[frame][0]))
    ln.set_data(np.arange(0, len(data[0]) - 1), data[frame][1:])
    return ln, time_text


# create output directory
os.makedirs(outpath, exist_ok=True)


if shutil.which('ffmpeg') is None:
    sys.exit('Please install ffmpeg and add to your PATH before continuing.')

for sample in samples:
    for model in models:
        for sim in sims:
            for n_sim in n_sims:
                # build file and extract data
                data_path = os.path.join(
                    'samples',
                    str(sample),
                    'models',
                    str(model),
                    'sims',
                    str(sim),
                    'n_sims',
                    str(n_sim),
                    'data',
                    'outputs',
                )

                data = np.loadtxt(
                    os.path.join(
                        data_path,
                        f'Vm_time_inner{inner}_fiber{fiber}_amp{amp}.dat',
                    ),
                    skiprows=1,
                )[:, 0:]

                # initialize plot
                fig, ax = plt.subplots()
                (ln,) = plt.plot(np.arange(0, len(data[0])), data[0])
                time_text = ax.text(0.5, 0.5, '', fontsize=15)

                # build and save animation
                print('WARNING: DO NOT ATTEMPT TO OPEN FILE UNTIL FRAME INDICES HAVE FINISHED PRINTING')
                ani = FuncAnimation(
                    fig,
                    _update,
                    frames=np.arange(1, 5000, 5),  # frames=np.arange(0, 5000, 1),
                    init_func=_init,
                    blit=False,
                    interval=10,
                    save_count=5000,
                    repeat=False,
                )

                ani.save(
                    os.path.join(
                        outpath,
                        f'video_Vm_time_{sample}_{model}_{sim}_{n_sim}_inner{inner}_fiber{fiber}_amp{amp}.mp4',
                    )
                )

plt.plot()
