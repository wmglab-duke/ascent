#!/usr/bin/env python3.7

"""Imports n_sims from the ASCENT n_sims export directory to the ASCENT simulation data directory.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""

import os

from src.core import Simulation
from src.utils import Configurable


def run(args):
    """Run the import.

    :param args: command line arguments
    """
    env_path = os.path.join('config', 'system', 'env.json')
    assert os.path.isfile(env_path), f'Invalid env path: {env_path}'

    for argument in args.run_indices:
        print(f'run {argument}')

        run_path = os.path.join('config', 'user', 'runs', f'{argument}.json')
        assert os.path.isfile(run_path), f'Invalid run path: {run_path}'

        run: dict = Configurable.load(run_path)
        nsim_source: str = Configurable.load(env_path).get('ASCENT_NSIM_EXPORT_PATH')

        samples = [run.get('sample')]
        models = run.get('models')
        sims = run.get('sims')
        for sample in samples:
            for model in models:
                for sim in sims:
                    sim_config: dict = Configurable.load(
                        os.path.join(
                            nsim_source, 'n_sims', '_'.join([str(x) for x in [sample, model, sim, '0']]), '0.json'
                        )
                    )
                    sim_dir = os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim))
                    if sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
                        check = Simulation.activations_exist(
                            sample,
                            model,
                            sim,
                            sim_dir,
                            os.path.join(nsim_source, 'n_sims'),
                            len(sim_config['protocol']['amplitudes']),
                        )
                    else:
                        check = Simulation.thresholds_exist(sample, model, sim, os.path.join(nsim_source, 'n_sims'))
                    if check is False:
                        if args.force is True:
                            print('Force argument passed, continuing with import')
                        else:
                            print(
                                'At least one threshold (or activation log if running FINITE AMPLITUDES) was missing,'
                                f' skipping import for run {argument} sample {sample} model {model} sim {sim}'
                            )
                            continue
                    Simulation.import_n_sims(
                        sample,
                        model,
                        sim,
                        sim_dir,
                        os.path.join(nsim_source, 'n_sims'),
                        delete=args.delete_nsims,
                    )
