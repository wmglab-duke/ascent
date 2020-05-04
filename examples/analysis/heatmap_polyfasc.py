#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

# ASSUMPTIONS:
#   1) 1:1 inner:outer for all fascicles
#   2) Single slide for each sample (0_0)
#   3) Single fiber per inner
# TODO: Change above assumptions in later iteration? (highest priority is probably assumption 3)

import os
import sys
import random as r

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
import matplotlib.colorbar as mplcolorbar
import cv2

from src.core import Sample, Trace
from src.core.query import Query
from src.utils import Object, MaskFileNames, Configurable, Config


def plot_orienation_mask(sam_ind: int):
    filepath = os.path.join('samples', str(sam_ind), 'slides', '0', '0', 'masks', MaskFileNames.ORIENTATION.value)
    if os.path.exists(filepath):
        contour, _ = cv2.findContours(np.flipud(cv2.imread(filepath, -1)),
                                      cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)
        trace = Trace([point + [0] for point in contour[0][:, 0, :]],
                      Configurable.load(os.path.join('config', 'system', 'exceptions.json')))
        trace.plot(plot_format='r-')
    else:
        print('Attempted to plot nonexistent orientation mask: {}'.format(filepath))


q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [3],
        'model': [0, 1, 2, 3],
        'sim': [0]
    }
}).run()

# sam = q.get_object(Object.SAMPLE, [3, 0, 0])
#
# l = len(sam.slides[0].fascicles)
#
# colormap = cm.get_cmap('viridis')
#
# colors = [colormap(n/l) for n in range(l)]
#
# sam.slides[0].plot(final=True, fix_aspect_ratio=True, fascicle_colors=colors)


results: dict = q.summary()

sample_results: dict
for sample_results in results.get('samples', []):
    sample_index = sample_results['index']
    sample_object: Sample = q.get_object(Object.SAMPLE, [sample_index])
    slide = sample_object.slides[0]
    n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

    model_results: dict
    for model_results in sample_results.get('models', []):
        model_index = model_results['index']

        # %% calculate orientation point location (i.e., contact location)
        r = slide.nerve.mean_radius() * 1.05  # scale up so orientation point is outside nerve
        theta = np.arctan2(*tuple(slide.nerve.points[slide.orientation_point_index][:2]))
        theta += np.deg2rad(
            q.get_config(Config.MODEL, [sample_index, model_index]).get('cuff').get('rotate').get('add_ang')
        )
        orientation_point = r * np.cos(theta), r * np.sin(theta)

        for sim_index in model_results.get('sims', []):
            sim_object = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

            for n, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]

                # %% fetch sim information
                sim_dir = q.build_path(Object.SIMULATION, [sample_index, model_index, sim_index], just_directory=True)
                n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n))
                fiberset_dir = os.path.join(sim_dir, 'fibersets', str(fiberset_index))

                # %% fetch thresholds, perform necessary calculations
                thresholds = []
                missing_indices = []
                for i in range(n_inners):
                    thresh_path = os.path.join(n_sim_dir, 'data', 'outputs', 'thresh_inner{}_fiber0.dat'.format(i))
                    if os.path.exists(thresh_path):
                        thresholds.append(np.loadtxt(thresh_path)[2])
                    else:
                        missing_indices.append(i)
                        print('MISSING: {}'.format(thresh_path))
                max_thresh = max(thresholds)
                min_thresh = min(thresholds)

                # %% generate colors from colorbar and thresholds
                cmap = plt.cm.get_cmap('viridis').reversed()
                colors = []
                offset = 0
                for i in range(n_inners):
                    actual_i = i - offset
                    if i not in missing_indices:
                        colors.append(cmap((thresholds[actual_i] - min_thresh)/(max_thresh - min_thresh)))
                    else:
                        offset += 1
                        colors.append((1, 0, 0, 1))

                # %% init figure
                fig: plt.Figure = plt.figure()

                # %% figure title
                title = ''
                for fib_key_name, fib_key_value in zip(sim_object.fiberset_key,
                                                       sim_object.fiberset_product[fiberset_index]):
                    title = '{} {}={}'.format(title, fib_key_name, fib_key_value)
                for wave_key_name, wave_key_value in zip(sim_object.wave_key, sim_object.wave_product[waveform_index]):
                    title = '{} {}={}'.format(title, wave_key_name, wave_key_value)
                plt.title(title)

                # %% plot orientation point and fascicles
                plt.plot(*orientation_point, 'r.', markersize=20)

                sample_object.slides[0].plot(final=False, fix_aspect_ratio=True, fascicle_colors=colors)  # , fascicle_colors=colors)

                # %% plot colorbar
                ax = fig.axes[0]
                norm = mplcolors.Normalize(vmin=min_thresh, vmax=max_thresh)
                mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                plt.colorbar(mappable=mappable, ax=ax, orientation='vertical')

                plt.show()

                # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
                # also, look into adding documentation to Simulation (might be useful for above task too)
