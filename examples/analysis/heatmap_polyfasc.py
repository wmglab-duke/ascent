#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

import os
import sys
import random as r

from src.core import Sample

sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
from matplotlib import cm

from src.core.query import Query
from src.utils import Object

plt.show()

q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [3],
        'model': [0],
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

sample_metadata: dict
for sample_metadata in results.get('samples', []):
    sample_index = sample_metadata['index']
    sample_object: Sample = q.get_object(Object.SAMPLE, [sample_index])

    model_metadata: dict
    for model_metadata in sample_metadata.get('models', []):
        model_index = model_metadata['index']

        for sim_index in model_metadata.get('sims', []):
            sim_object = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

            for n, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]

                sim_dir = q.build_path(Object.SIMULATION, [sample_index, model_index, sim_index], just_directory=True)
                n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n))
                fiberset_dir = os.path.join(sim_dir, 'fibersets', str(fiberset_index))

                plt.figure(n)

                title = ''
                for fib_key_name, fib_key_value in zip(sim_object.fiberset_key, sim_object.fiberset_product[fiberset_index]):
                    title = '{} {}={}'.format(title, fib_key_name, fib_key_value)

                for wave_key_name, wave_key_value in zip(sim_object.wave_key, sim_object.wave_product[waveform_index]):
                    title = '{} {}={}'.format(title, wave_key_name, wave_key_value)

                n_inners = sum(len(fasc.inners) for fasc in sample_object.slides[0].fascicles)

                # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
                # also, look into adding documentation to Simulation (might be useful for above task too)