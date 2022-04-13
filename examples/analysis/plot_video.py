#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import shutil
import sys

samples = [200,201,205]
models = [0]
sims = [0,1,2]
inner = 0
fiber = 0
n_sims = [0,1,2]
amp = 0

outpath = 'out/analysis/videos'

#create output directory
if not os.path.exists(outpath):
    os.makedirs(outpath)

if shutil.which('ffmpeg') is None:
    sys.exit('Please install ffmpeg and add to your PATH before continuing.')

for sample in samples:
    for model in models:
        for sim in sims:
            for n_sim in n_sims:
                # build file and extract data
                data_path = os.path.join(
                    'samples', str(sample),
                    'models', str(model),
                    'sims', str(sim),
                    'n_sims', str(n_sim),
                    'data', 'outputs'
                )
                # data = np.loadtxt(os.path.join(data_path,
                #                                'gating_h_time_inner{}_fiber{}_amp0.dat'.format(inner, fiber)
                #                                ),
                #                   skiprows=1)[:, 1:]
                
                data = np.loadtxt(os.path.join(data_path,
                                               'Vm_time_inner{}_fiber{}_amp{}.dat'.format(inner, fiber, amp)
                                               ),
                                  skiprows=1)[:, 0:]
                
                # initialize plot
                fig, ax = plt.subplots()
                ln, = plt.plot(np.arange(0, len(data[0])), data[0])
                time_text = ax.text(.5, .5, '', fontsize=15)
                
                # define initializer function for animation
                def init():
                    flat_data = data.flatten()
                    ax.set_ylim(np.min(flat_data), np.max(flat_data))
                    return ln,
                
                
                # define update function for each frame of animation
                def update(frame):
                    time_text.set_text('time: ' + str(data[frame][0]))
                    ln.set_data(np.arange(0, len(data[0])-1), data[frame][1:])
                    return ln, time_text
                
                
                # build and save animation
                print('WARNING: DO NOT ATTEMPT TO OPEN FILE UNTIL FRAME INDICES HAVE FINISHED PRINTING')
                ani = FuncAnimation(fig, update, frames=np.arange(1, 5000, 5),  # frames=np.arange(0, 5000, 1),
                                    init_func=init, blit=False, interval=10, save_count=5000, repeat=False)
                # ani.save(os.path.join(data_path,
                #                       'video_gating_h_time_inner{}_fiber{}_amp0.gif'.format(inner, fiber)  # or .mp4
                #                       ))
                
                ani.save(os.path.join(outpath,
                                      'video_Vm_time_{}_{}_{}_{}_inner{}_fiber{}_amp{}.mp4'.format(sample, model, sim, n_sim, inner, fiber, amp)  # or .mp4
                                      ))

plt.plot()
