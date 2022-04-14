#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os

from src.core import Simulation
from src.utils import Configurable



def run(args):
    env_path = os.path.join('config', 'system', 'env.json')
    assert os.path.isfile(env_path), 'Invalid env path: {}'.format(env_path)

    for argument in args.run_indices:
        print('run {}'.format(argument))

        run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(argument))
        assert os.path.isfile(run_path), 'Invalid run path: {}'.format(run_path)

        run: dict = Configurable.load(run_path)
        nsim_source: str = Configurable.load(env_path).get('ASCENT_NSIM_EXPORT_PATH')

        sample = run.get('sample')
        models = run.get('models')
        sims = run.get('sims')

        for model in models:
            for sim in sims:
                sim_dir = os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim))
                os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim),'sim.obj')
                check = Simulation.thresholds_exist(sample, model, sim, sim_dir, os.path.join(nsim_source, 'n_sims'))
                if check==False:
                    if args.force==True:
                        print('Force argument passed, continuing with import')
                    else:
                        print('At least one threshold was missing, skipping import for run {} sample {} model {} sim {}'.format(argument,sample,model,sim))
                        continue
                Simulation.import_n_sims(sample, model, sim, sim_dir, os.path.join(nsim_source, 'n_sims'),delete = args.delete_nsims)
                
