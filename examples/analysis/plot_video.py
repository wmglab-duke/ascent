import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

sample = 0
model = 0
sim = 0
inner = 0
fiber = 0
n_sim = 0

# build file and extract data
data_path = os.path.join(
    'samples', str(sample),
    'models', str(model),
    'sims', str(sim),
    'n_sims', str(n_sim),
    'data', 'outputs',
    'gating_h_time_inner{}_fiber{}.dat'.format(inner, fiber)
    )
data = np.loadtxt(data_path, skiprows=1)[:, 1:]

# initialize plot
fig, ax = plt.subplots()
ln, = plt.plot(np.arange(0, len(data[0])), data[0])

# define initializer function for animation
def init():
    flat_data = data.flatten()
    ax.set_ylim(np.min(flat_data), np.max(flat_data))
    return ln,

# define update function for each frame of animation
def update(frame):
    print(frame)
    ln.set_data(np.arange(0, len(data[0])), data[frame])
    return ln,

# build and save animation
print('WARNING: DO NOT ATTEMPT TO OPEN FILE UNTIL FRAME INDICES HAVE FINISHED PRINTING')
ani = FuncAnimation(fig, update, frames=np.arange(0, 5000, 1),
                    init_func=init, blit=False, interval=1, save_count=5000, repeat=False)
ani.save('/Users/jakecariello/Desktop/sample_movie.mp4')
plt.plot()