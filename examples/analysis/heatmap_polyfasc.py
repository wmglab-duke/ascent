#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

# ASSUMPTIONS:
#   1) 1:1 inner:outer for all fascicles
#   2) Single slide for each sample (0_0)
#   3) Single fiber per inner
# TODO: Change above assumptions in later iteration? (highest priority is probably assumption 3)

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

# import matplotlib
import matplotlib.colors as mplcolors
import matplotlib.pyplot as plt
import numpy as np

from src.core import Sample
from src.core.query import Query
from src.utils import Object, Config

# set default fig size
plt.rcParams['figure.figsize'] = [16.8, 10.14]
# plt.rcParams['figure.figsize'] = tuple(np.array(plt.rcParams['figure.figsize'])*2)

# initialize and run Query, then fetch results
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [4],
        'model': [0],
        'sim': [0]
    }
}).run()
results: dict = q.summary()

# loop samples
sample_results: dict
for sample_results in results.get('samples', []):
    sample_index = sample_results['index']
    sample_object: Sample = q.get_object(Object.SAMPLE, [sample_index])
    sample_config: dict = q.get_config(Config.SAMPLE, [sample_index])
    slide = sample_object.slides[0]
    n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

    print('sample: {}'.format(sample_index))

    # loop models
    model_results: dict
    for model_results in sample_results.get('models', []):
        model_index = model_results['index']

        print('\tmodel: {}'.format(model_index))

        # calculate orientation point location (i.e., contact location)
        r = slide.nerve.mean_radius() * 1.1  # scale up so orientation point is outside nerve
        theta = np.arctan2(*tuple(np.flip(slide.nerve.points[slide.orientation_point_index][:2])))
        theta += np.deg2rad(
            q.get_config(Config.MODEL, [sample_index, model_index]).get('cuff').get('rotate').get('add_ang')
        )
        orientation_point = r * np.cos(theta), r * np.sin(theta)

        # loop sims
        for sim_index in model_results.get('sims', []):
            sim_object = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

            print('\t\tsim: {}'.format(sim_index))

            # init figure with subplots
            master_product_count = len(sim_object.master_product_indices)
            rows = int(np.floor(np.sqrt(master_product_count)))
            cols = int(np.ceil(master_product_count / rows))
            figure, axes = plt.subplots(rows, cols, constrained_layout=True)

            # loop nsims
            for n, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]

                # fetch axis
                ax: plt.Axes = axes.reshape(-1)[n]

                # fetch sim information
                sim_dir = q.build_path(Object.SIMULATION, [sample_index, model_index, sim_index], just_directory=True)
                n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n))
                fiberset_dir = os.path.join(sim_dir, 'fibersets', str(fiberset_index))

                # fetch thresholds, then find min and max
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

                # generate colors from colorbar and thresholds
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

                # figure title -- make arbitrary, hard-coded subplot title modifications here (add elif's)
                title = ''
                for fib_key_name, fib_key_value in zip(sim_object.fiberset_key,
                                                       sim_object.fiberset_product[fiberset_index]):

                    if fib_key_name == 'fibers->z_parameters->diameter':
                        title = r'{} fiber diameter: {}µm'.format(title, fib_key_value)
                    else:
                        # default title
                        title = '{} {}:{}'.format(title, fib_key_name, fib_key_value)

                for wave_key_name, wave_key_value in zip(sim_object.wave_key, sim_object.wave_product[waveform_index]):

                    # default title
                    title = '{} {}:{}'.format(title, wave_key_name, wave_key_value)

                ax.set_title(title)

                # vals = np.linspace(-1500, 1500, 1000)
                # ax.plot(vals, vals)

                # plot orientation point and fascicles
                ax.plot(*orientation_point, 'r.', markersize=20)
                ax.plot(*tuple(slide.nerve.points[slide.orientation_point_index][:2]), 'b*')
                sample_object.slides[0].plot(final=False, fix_aspect_ratio=True, fascicle_colors=colors,
                                             ax=ax, outers_flag=False, inner_format='k-')

                # plot colorbar
                norm = mplcolors.Normalize(vmin=min_thresh, vmax=max_thresh)
                mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                plt.colorbar(mappable=mappable, ax=ax, orientation='vertical', label=r'mA')

            # PLOT!
            plt.suptitle('Sample: {}, Model: {}, Fiber mode: {}'.format(
                sample_config.get('sample'),
                model_index,
                sim_object.search(Config.SIM, 'fibers', 'mode'))
            )
            plt.show()

            # save... remember to change this path
            # plt.savefig('/Users/jakecariello/Box/SPARC_JakeCariello/Madison/thresholds_figures/{}_{}_{}.png'.format(
            #     sample_index, model_index, sim_index
            # ), dpi=400)

                # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
                # also, look into adding documentation to Simulation (might be useful for above task too)
