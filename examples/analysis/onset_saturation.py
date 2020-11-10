# #!/usr/bin/env python3.7
#
# # RUN THIS FROM REPOSITORY ROOT
#
# import matplotlib.pyplot as plt
# import scipy.io as sio
# import sys
# import os
# import numpy as np
#
# from matplotlib import rcParams
# rcParams['figure.figsize'] = (8.0, 10.0) #predefine the size of the figure window
# rcParams.update({'font.size': 14})
#
# sys.path.append(os.path.sep.join([os.getcwd(), '']))
#
# data = sio.loadmat(r'D:\Documents\LivaNovaContact\Pig191205-0\EPhys\figures\AucIntactLateEmgDRC.mat')
#
# sample = 83
# model = 0
# sim = 10
# cmaps_ln = ["Greys", "Purples", "Blues", "Greens", "Oranges", "Reds"]
#
# fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
# ax3 = fig.add_subplot(111, zorder=-1)
# for _, spine in ax3.spines.items():
#     spine.set_visible(False)
# ax3.tick_params(labelleft=False, labelbottom=False, left=False, right=False)
# ax3.get_shared_x_axes().join(ax3, ax1)
#
#
# for line in range(len(data['x'])):
#     if data['labels'][0][line][0][-1] == '0' or data['labels'][0][line][0][0] == '0':  # only want monopolar
#         on_ind = int(data['labels'][0][line][0][0])-1
#         cmap = plt.cm.get_cmap(cmaps_ln[on_ind])
#         ax1.plot(data['x'][line][0][0]/1000, data['y'][line][0][0], label=data['labels'][0][line][0], color=tuple(cmap(0.7)), linewidth=2)
#
# handles, labels = ax1.get_legend_handles_labels()
# order = [5, 4, 3, 2, 1, 0]
# ax1.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
#
# # plt.xlabel('Stimulation Amplitude (mA)')
# # ax1.ylabel('Area-Under-Curve Response (\u03bcV*s)')
# ax1.set_title('In Vivo: Intact Late EMG Recruitment')
# # ax1.xlim(-0.100, 3.100)
# # ax1.ylim(0, 0.5)
# ax1.set_ylabel('Area-Under-Curve Response (\u03bcV*s)')
#
#
# # 5.7 (1, 5, 9, 13, 17, 21) and 10 (3, 7, 11, 15, 19, 23)
# n_sims = [3, 7, 11, 15, 19, 23]
# missing_color = (1, 0, 0, 1)
# n_inners = 49
# n_sims_path = r'D:\Documents\ascent\samples\{}\models\{}\sims\{}\n_sims'.format(sample, model, sim)
# all_thresholds = []
# all_colors = []
# for src in range(len(n_sims)):
#     n_sim_dir = os.path.join(n_sims_path, str(n_sims[src]))
#     thresholds = []
#     colors = []
#     missing_indices = []
#     cmap = plt.cm.get_cmap(cmaps_ln[src]).reversed()
#
#     for i in range(n_inners):
#         thresh_path = os.path.join(n_sim_dir, 'data', 'outputs',
#                                    'thresh_inner{}_fiber0.dat'.format(i))
#         if os.path.exists(thresh_path):
#             threshold = abs(np.loadtxt(thresh_path))
#             if len(np.atleast_1d(threshold)) > 1:
#                 threshold = threshold[-1]
#             thresholds.append(threshold)
#         else:
#             missing_indices.append(i)
#             print('MISSING: {}'.format(thresh_path))
#     all_thresholds.append(thresholds)
#
#     offset = 0
#     max_thresh = np.max(thresholds)
#     min_thresh = np.min(thresholds)
#
#     for i in range(n_inners):
#         actual_i = i - offset
#         if i not in missing_indices:
#             colors.append(
#                 tuple(cmap((thresholds[actual_i] - min_thresh) / (max_thresh - min_thresh))))
#         else:
#             # NOTE: PLOTS MISSING VALUES AS RED
#             offset += 1
#             colors.append(missing_color)
#     all_colors.append(colors)
#
# for src in range(len(n_sims)):
#     zipped = zip(all_thresholds[src], all_colors[src])
#     zipped = list(zipped)
#     res = sorted(zipped, key=lambda x: x[0])
#
#     for i, element in enumerate(res):
#         if i == len(res)-1:
#             ax2.plot(element[0], len(n_sims)-src, markerfacecolor=element[1], markersize=8, marker='o', markeredgecolor='black')
#         else:
#             ax2.plot(element[0], len(n_sims)-src, markerfacecolor=element[1], markersize=8, marker='o', markeredgecolor='none')
#
#     #plt.legend()
# # ax2.xlim(-0.100, 3.100)
# # ax2.ylim(0, 7)
# ax2.set_yticks(np.arange(1, len(n_sims)+1, step=1))  # ("6-0", "5-0", "4-0", "3-0", "2-0", "1-0")
# ax2.set_yticklabels(("6-0", "5-0", "4-0", "3-0", "2-0", "1-0"))
# ax2.set_xlabel('Stimulation Amplitude (mA)')
# ax2.set_ylabel('Model: Thresholds (10 \u03bcm MRG Fibers)')
# # plt.tight_layout(pad=3)
# # ax1.grid(alpha=0.2, linestyle=':')
# # ax2.grid(alpha=0.2, linestyle=':')
#
# major_ticks = np.arange(0, 3.5, 0.5)
# minor_ticks = np.arange(0, 3.5, 0.25)
#
# ax1.set_xticks(major_ticks)
# ax1.set_xticks(minor_ticks, minor=True)
#
# # And a corresponding grid
# ax1.grid(axis="x")
#
# # Or if you want different settings for the grids:
# ax1.grid(which='minor', alpha=0.5, linestyle=":")
# ax1.grid(which='major', alpha=0.5)
#
# ax2.set_xticks(major_ticks)
# ax2.set_xticks(minor_ticks, minor=True)
#
# # And a corresponding grid
# ax2.grid(axis="x")
#
# # Or if you want different settings for the grids:
# ax2.grid(which='minor', alpha=0.5, linestyle=":")
# ax2.grid(which='major', alpha=0.5)
#
# ax3.set_xticks(major_ticks)
# ax3.set_xticks(minor_ticks, minor=True)
#
# # And a corresponding grid
# ax3.grid(axis="x")
#
# # Or if you want different settings for the grids:
# ax3.grid(which='minor', alpha=0.5, linestyle=":")
# ax3.grid(which='major', alpha=0.5)
#
# plt.show()
# print('here')









#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

# import matplotlib.pyplot as plt
# import scipy.io as sio
# import sys
# import os
# import numpy as np
#
# from matplotlib import rcParams
# rcParams['figure.figsize'] = (8.0, 10.0) #predefine the size of the figure window
# rcParams.update({'font.size': 14})
#
# sys.path.append(os.path.sep.join([os.getcwd(), '']))
#
# data = sio.loadmat(r'D:\Documents\LivaNovaContact\Pig191205-0\EPhys\figures\P2pRLTA-betaDRC.mat')
#
# sample = 83
# model = 0
# sim = 10
# cmaps_ln = ["Greys", "Purples", "Blues", "Greens", "Oranges", "Reds"]
#
# fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
# ax3 = fig.add_subplot(111, zorder=-1)
# for _, spine in ax3.spines.items():
#     spine.set_visible(False)
# ax3.tick_params(labelleft=False, labelbottom=False, left=False, right=False)
# ax3.get_shared_x_axes().join(ax3, ax1)
#
#
# for line in range(len(data['x'])):
#     if data['labels'][0][line][0][-1] == '0' or data['labels'][0][line][0][0] == '0':  # only want monopolar
#         on_ind = int(data['labels'][0][line][0][0])-1
#         cmap = plt.cm.get_cmap(cmaps_ln[on_ind])
#         ax1.plot(data['x'][line][0][0]/1000, data['y'][line][0][0], label=data['labels'][0][line][0], color=tuple(cmap(0.7)), linewidth=2)
#
# handles, labels = ax1.get_legend_handles_labels()
# order = [5, 4, 3, 2, 1, 0]
# ax1.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
#
# # plt.xlabel('Stimulation Amplitude (mA)')
# # ax1.ylabel('Area-Under-Curve Response (\u03bcV*s)')
# ax1.set_title('In Vivo: RLT A-beta Recruitment')
# # ax1.xlim(-0.100, 3.100)
# # ax1.ylim(0, 0.5)
# ax1.set_ylabel('Peak-to-Peak Response (\u03bcV)')
#
#
# # 5.7 (1, 5, 9, 13, 17, 21) and 10 (3, 7, 11, 15, 19, 23)
# n_sims = [1, 5, 9, 13, 17, 21]
# missing_color = (1, 0, 0, 1)
# n_inners = 49
# n_sims_path = r'D:\Documents\ascent\samples\{}\models\{}\sims\{}\n_sims'.format(sample, model, sim)
# all_thresholds = []
# all_colors = []
# for src in range(len(n_sims)):
#     n_sim_dir = os.path.join(n_sims_path, str(n_sims[src]))
#     thresholds = []
#     colors = []
#     missing_indices = []
#     cmap = plt.cm.get_cmap(cmaps_ln[src]).reversed()
#
#     for i in range(n_inners):
#         thresh_path = os.path.join(n_sim_dir, 'data', 'outputs',
#                                    'thresh_inner{}_fiber0.dat'.format(i))
#         if os.path.exists(thresh_path):
#             threshold = abs(np.loadtxt(thresh_path))
#             if len(np.atleast_1d(threshold)) > 1:
#                 threshold = threshold[-1]
#             thresholds.append(threshold)
#         else:
#             missing_indices.append(i)
#             print('MISSING: {}'.format(thresh_path))
#     all_thresholds.append(thresholds)
#
#     offset = 0
#     max_thresh = np.max(thresholds)
#     min_thresh = np.min(thresholds)
#
#     for i in range(n_inners):
#         actual_i = i - offset
#         if i not in missing_indices:
#             colors.append(
#                 tuple(cmap((thresholds[actual_i] - min_thresh) / (max_thresh - min_thresh))))
#         else:
#             # NOTE: PLOTS MISSING VALUES AS RED
#             offset += 1
#             colors.append(missing_color)
#     all_colors.append(colors)
#
# for src in range(len(n_sims)):
#     zipped = zip(all_thresholds[src], all_colors[src])
#     zipped = list(zipped)
#     res = sorted(zipped, key=lambda x: x[0])
#
#     for i, element in enumerate(res):
#         if i == len(res)-1:
#             ax2.plot(element[0], len(n_sims)-src, markerfacecolor=element[1], markersize=8, marker='o', markeredgecolor='black')
#         else:
#             ax2.plot(element[0], len(n_sims)-src, markerfacecolor=element[1], markersize=8, marker='o', markeredgecolor='none')
#
#     #plt.legend()
# # ax2.xlim(-0.100, 3.100)
# # ax2.ylim(0, 7)
# ax2.set_yticks(np.arange(1, len(n_sims)+1, step=1))  # ("6-0", "5-0", "4-0", "3-0", "2-0", "1-0")
# ax2.set_yticklabels(("6-0", "5-0", "4-0", "3-0", "2-0", "1-0"))
# ax2.set_xlabel('Stimulation Amplitude (mA)')
# ax2.set_ylabel('Model: Thresholds (5.7 \u03bcm MRG Fibers)')
# # plt.tight_layout(pad=3)
# # ax1.grid(alpha=0.2, linestyle=':')
# # ax2.grid(alpha=0.2, linestyle=':')
#
# major_ticks = np.arange(0, 3.5, 0.5)
# minor_ticks = np.arange(0, 3.5, 0.25)
#
# ax1.set_xticks(major_ticks)
# ax1.set_xticks(minor_ticks, minor=True)
#
# # And a corresponding grid
# ax1.grid(axis="x")
#
# # Or if you want different settings for the grids:
# ax1.grid(which='minor', alpha=0.5, linestyle=":")
# ax1.grid(which='major', alpha=0.5)
#
# ax2.set_xticks(major_ticks)
# ax2.set_xticks(minor_ticks, minor=True)
#
# # And a corresponding grid
# ax2.grid(axis="x")
#
# # Or if you want different settings for the grids:
# ax2.grid(which='minor', alpha=0.5, linestyle=":")
# ax2.grid(which='major', alpha=0.5)
#
# ax3.set_xticks(major_ticks)
# ax3.set_xticks(minor_ticks, minor=True)
#
# # And a corresponding grid
# ax3.grid(axis="x")
#
# # Or if you want different settings for the grids:
# ax3.grid(which='minor', alpha=0.5, linestyle=":")
# ax3.grid(which='major', alpha=0.5)
#
# plt.show()
# print('here')








import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Union, List, Tuple
from src.core import Sample, Simulation, Slide, FiberSet
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config, Object, FiberXYMode
import pickle
import matplotlib.colorbar as cbar
import matplotlib.colors as mplcolors
import matplotlib.ticker as tick
from matplotlib import rcParams
import matplotlib.patches as mpatches
import math
rcParams['figure.figsize'] = (8.0, 10.0) #predefine the size of the figure window
rcParams.update({'font.size': 24})

print(os.getcwd())


def get_object(mode: Object, indices: List[int]) -> Union[Sample, Simulation]:
    """

    :return:
    """
    with open(build_path(mode, indices), 'rb') as obj:
        return pickle.load(obj)


def build_path(mode: Union[Config, Object], indices: List[int] = None, just_directory: bool = False) -> str:
    """

    :param just_directory:
    :param mode:
    :param indices:
    :return:
    """

    result = str()
    # just_directory = False

    if indices is None:
        indices = [0, 0, 0]  # dummy values... will be stripped from path later bc just_directory is set to True
        just_directory = True

    if mode == Config.SAMPLE:
        result = os.path.join('..', '..', 'samples', str(indices[0]), 'sample.json')
    elif mode == Config.MODEL:
        result = os.path.join('..', '..', 'samples', str(indices[0]), 'models', str(indices[1]), 'model.json')
    elif mode == Config.SIM:
        result = os.path.join('..', '..', 'config', 'user', 'sims', '{}.json'.format(indices[0]))
    elif mode == Object.SAMPLE:
        result = os.path.join('..', '..', 'samples', str(indices[0]), 'sample.obj')
    elif mode == Object.SIMULATION:
        result = os.path.join('..', '..', 'samples', str(indices[0]), 'models', str(indices[1]), 'sims', str(indices[2]),
                              'sim.obj')
    else:
        print('INVALID MODE:'.format(type(mode)))

    if just_directory:
        result = os.path.join(*result.split(os.sep)[:-1])

    return result

# @staticmethod
# def range(x, axis=0):
#     return np.max(x, axis=axis) - np.min(x, axis=axis)

sample = 83
model = 0
sim = 10
fibers_strs = ["2\u03bcm MRG", " 5.7\u03bcm MRG", "8.7\u03bcm MRG", "10\u03bcm MRG"]

# 5.7 (1, 5, 9, 13, 17, 21) and 10 (3, 7, 11, 15, 19, 23)
all_n_sims = [[0, 4, 8, 12, 16, 20], [1, 5, 9, 13, 17, 21], [2, 6, 10, 14, 18, 22], [3, 7, 11, 15, 19, 23]]
missing_color = (1, 0, 0, 1)
n_inners = 50
n_sims_path = r'D:\Documents\ascent\samples\{}\models\{}\sims\{}\n_sims'.format(sample, model, sim)
all_thresholds = []
all_colors = []
all_fasc_means = []
all_fasc_ranges = []

rows = 1
cols = 4

figure, axes = plt.subplots(rows, cols, constrained_layout=False, figsize=(25, 5))
axes = axes.reshape(-1)
sample_object = get_object(Object.SAMPLE, [sample])

for fiber_index, n_sims in enumerate(all_n_sims):
    fiber_thresholds = []
    for _, n_sim in enumerate(n_sims):
        n_sim_dir = os.path.join(n_sims_path, str(n_sim))
        src_thresholds = []
        colors = []
        missing_indices = []

        for i in range(n_inners):
            thresh_path = os.path.join(n_sim_dir, 'data', 'outputs',
                                       'thresh_inner{}_fiber0.dat'.format(i))
            if os.path.exists(thresh_path):
                threshold = abs(np.loadtxt(thresh_path))
                if len(np.atleast_1d(threshold)) > 1:
                    threshold = threshold[-1]
                src_thresholds.append(threshold)
            else:
                missing_indices.append(i)
                print('MISSING: {}'.format(thresh_path))
        fiber_thresholds.append(src_thresholds)
    all_thresholds.append(fiber_thresholds)

    fasc_means = []
    fasc_ranges = []
    for fasc_ind in range(len(fiber_thresholds[0])):
        fasc_means.append(np.mean([contact[fasc_ind] for contact in fiber_thresholds]))
        tmp = [contact[fasc_ind] for contact in fiber_thresholds]
        fasc_ranges.append(np.max(tmp) - np.min(tmp))

    all_fasc_means.append(fasc_means)
    all_fasc_ranges.append(fasc_ranges)

cmap = plt.cm.get_cmap('Spectral')
range_min = np.min(all_fasc_ranges[:])
range_max = np.max(all_fasc_ranges[:])

for fiber_index, _ in enumerate(all_n_sims):
    colors = []
    offset = 0

    for i in range(n_inners):
        actual_i = i - offset
        if i not in missing_indices:
            colors.append(
                tuple(cmap((all_fasc_ranges[fiber_index][actual_i] - range_min) / (range_max - range_min))))
        else:
            # NOTE: PLOTS MISSING VALUES AS RED
            offset += 1
            colors.append(missing_color)
    sample_object.slides[0].plot(final=False, fix_aspect_ratio=True, ax=axes[fiber_index], outers_flag=False, inner_format='k-', fascicle_colors=colors, show_axis=False, title=fibers_strs[fiber_index])
    r_nerve = np.sqrt(sample_object.morphology['Nerve']['area'] / np.pi)
    orientation_point = (-1770.2041441200297, -1217.0532585333917)
    rot_def = np.arctan(orientation_point[1] / orientation_point[0]) + np.pi

    ang = 0.71028  # 0.89012
    ln_angs = [rot_def - 2.5 * ang,
               rot_def - 1.5 * ang,
               rot_def - 0.5 * ang,
               rot_def + 0.5 * ang,
               rot_def + 1.5 * ang,
               rot_def + 2.5 * ang]

    for s_ind, ln_ang in enumerate(ln_angs):
            active_contact = mpatches.Arc(xy=(0, 0),
                                          width=2 * (r_nerve + 100),
                                          height=2 * (r_nerve + 100),
                                          angle=0.0,
                                          theta1=math.degrees(ln_ang) - 2.5,
                                          theta2=math.degrees(ln_ang) + 2.5,
                                          color=(0, 0, 0, 1),
                                          linewidth=3
                                          )
            axes[fiber_index].add_artist(active_contact)

cbar_ax = figure.add_axes([0.88, 0.15, 0.05, 0.7])

my_ticks = [0.05,  0.5, 1, 1.5, 2, 2.5, 3, 3.49]
cb_label = "mA"
cb: cbar.Colorbar = plt.colorbar(
    mappable=plt.cm.ScalarMappable(
        cmap=cmap,
        norm=mplcolors.Normalize(vmin=range_min, vmax=range_max)
    ),
    ticks=my_ticks,
    ax=cbar_ax,
    orientation='vertical',
    # label=cb_label,
    aspect=20
)

cb.ax.set_yticklabels(['{:.2f}'.format(a_tick) for a_tick in my_ticks])
cbar_ax.axis('off')


plt.show()
#range
#mean




# plot slide (nerve and fascicles, defaulting to no outers)



print('here')