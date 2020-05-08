#!/usr/bin/env python3.7

import os
import sys

from src.core import Simulation
from src.utils import Configurable

assert len(sys.argv) > 1, 'Too few arguments to start.py (must have at least one run index)'

env_path = os.path.join('config', 'system', 'env.json')
assert os.path.isfile(env_path), 'Invalid env path: {}'.format(env_path)

for argument_index in range(1, len(sys.argv)):
    argument = sys.argv[argument_index]

    run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(argument))
    assert os.path.isfile(run_path), 'Invalid run path: {}'.format(run_path)

    run: dict = Configurable.load(run_path)
    nsim_source: str = Configurable.load(env_path).get('nsim_export')

    sample = run.get('sample')
    models = run.get('models')
    sims = run.get('sims')

    for model in models:
        for sim in sims:
            sim_dir = os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim))
            Simulation.import_n_sims(sample, model, sim, sim_dir, os.path.join(nsim_source, 'n_sims'))
