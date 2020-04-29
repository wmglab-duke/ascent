#!/usr/bin/env python3.7

import os
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from src.core import Sample
from src.core.query import Query
from src.utils import Object

cwd = os.getcwd()
root = os.path.abspath(os.path.join(*'../../'.split('/')))

os.chdir(root)

criteria = {
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [3],
        'model': [0],
        'sim': [0]
    }
}


q = Query(criteria)
q.run()

results: dict = q.summary()

sample_metadata: dict
for sample_metadata in results.get('samples', []):
    sample_index = sample_metadata['index']
    sample_object = q.get_object(Object.SAMPLE, [sample_index])

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

                sample_object.slides[0].plot(final=False, title=title)

                colormap = cm.get_cmap('viridis', 1000)

                n_fibers = len(sim_object.fibersets[fiberset_index].fibers)

                missing_fibers = [i for i in range(n_fibers)
                                  if not os.path.exists(os.path.join(n_sim_dir, 'data', 'outputs', 'thresh_inner0_fiber{}.dat'.format(i)))]

                thresholds = [np.loadtxt(
                    os.path.join(n_sim_dir, 'data', 'outputs', 'thresh_inner0_fiber{}.dat'.format(i))
                )[2] for i in range(n_fibers) if i not in missing_fibers]

                max_threshold = max(thresholds)
                min_threshold = min(thresholds)

                for filename in [f for f in os.listdir(fiberset_dir) if int(f.split('.dat')[0]) not in missing_fibers]:
                    coord = np.loadtxt(os.path.join(fiberset_dir, filename), skiprows=1)[0][:2]

                    threshold = np.loadtxt(
                        os.path.join(n_sim_dir, 'data', 'outputs', 'thresh_inner0_fiber{}.dat'.format(filename.split('.dat')[0]))
                    )[2]

                    print((threshold - min_threshold)/(max_threshold - min_threshold))

                    plt.plot(*coord, '*', color=colormap((threshold - min_threshold)/(max_threshold - min_threshold)))

                plt.show()

os.chdir(cwd)
