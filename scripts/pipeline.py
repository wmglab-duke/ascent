#!/usr/bin/env python3.7

"""Main script for running the pipeline.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import subprocess
import sys
import time

from config.system import _version
from src.runner import Runner
from src.utils.enums import Config, Env, SetupMode

from .env_setup import run as env_setup


def export_env(sample_path: str, runner: Runner):
    """Export the system configuration to files.

    :param sample_path: directory in which to save files
    :param runner: runner object
    """
    import neuron

    ascent_version = 'ASCENT==' + _version.__version__
    python_version = sys.version_info
    python_version = 'python==' + '.'.join([str(v) for v in python_version[:3]])
    neuron_version = 'NEURON==' + neuron.__version__
    comsol_path = runner.search(Config.ENV, Env.COMSOL_PATH.value)
    with open(os.path.join(comsol_path, 'readme.txt')) as f:
        comsol_version = f.readline().strip('\n')
    comsol_version = 'COMSOL==' + comsol_version.split(' ')[1]
    with open(sample_path + '/software_info.txt', 'w') as f:
        for sv in (ascent_version, python_version, comsol_version, neuron_version):
            f.write(sv + '\n')

    with open(sample_path + '/package_info.txt', 'w') as f:
        subprocess.run(['pip', 'freeze'], stdout=f)


def run(args):
    """Run the pipeline.

    :param args: The command line arguments.
    :raises ValueError: run indices must be between 0 and 2147482999, inclusive.
    :raises FileNotFoundError: input directory specified in sample.json not found.
    :raises Exception: If the Python version is not 3.10 or newer.
    :raises ValueError: If run group inputs are invalid
    """
    # test
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 10):
        raise Exception('Python 3.10 or newer is required to run this script.')

    # create bin/ directory for storing compiled Java files if it does not yet exist
    if not (os.path.exists('bin')):
        os.mkdir('bin')

    if not args.run_indices:
        raise ValueError('No run indices provided.')

    for argument in args.run_indices:
        # START timer
        start = time.time()

        try:
            int(argument)
        except ValueError:
            raise ValueError(f'Invalid type for argument: {argument}\nAll arguments must be positive integers.')

        if int(argument) < 0:
            raise ValueError(f'Invalid sign for argument: {argument}\nAll arguments must be positive integers.')

        if int(argument) > 2147482999 and not args.test:
            raise ValueError(f'Invalid value for argument: {argument}\nArguments greater than 2147482999 are reserved.')

        print(f'\n########## STARTING RUN {argument} ##########\n')

        run_path = os.path.join('config', 'user', 'runs', f'{argument}.json')
        if not os.path.exists(run_path):
            raise FileNotFoundError(f'Nonexistent run configuration path: {run_path}')

        env_path = os.path.join('config', 'system', 'env.json')
        if not os.path.exists(env_path):
            print(f'Missing env configuration file: {env_path}')
            env_setup(env_path)

        # initialize Runner (loads in parameters)
        runner = Runner(int(argument))
        runner.add(SetupMode.NEW, Config.RUN, run_path)
        runner.add(SetupMode.NEW, Config.ENV, env_path)
        runner.add(SetupMode.OLD, Config.CLI_ARGS, vars(args))

        # populate environment variables
        runner.populate_env_vars()

        if (
            runner.search(Config.RUN, 'sample') > 2147482999
            or any(m > 2147482999 for m in runner.search(Config.RUN, 'models'))
            or any(m > 2147482999 for m in runner.search(Config.RUN, 'sims'))
        ) and not args.test:
            raise ValueError(
                f'Invalid value for argument: {argument}\nAll indices (sample, model, sim) greater than 2147482999 are '
                f'reserved for testing.'
            )

        samples_path = f'samples/{argument}'
        if not os.path.exists(samples_path):
            raise ValueError(f'Sample index {argument} does not exist in /samples folder.')
        export_env(samples_path, runner)

        # ready, set, GO!
        runner.run()

        # END timer
        end = time.time()
        elapsed = end - start

        if args.auto_submit or runner.search(Config.RUN, 'auto_submit_fibers', optional=True) is True:
            print(f'Auto submitting fibers for run {argument}')
            # submit fibers before moving on to next run
            reset_dir = os.getcwd()
            export_path = runner.search(Config.ENV, Env.NSIM_EXPORT_PATH.value)
            os.chdir(export_path)
            with open(os.devnull, 'wb') as devnull:
                # -s flag to skip summary
                comp = subprocess.run(
                    ['python', 'submit.py', '-s', str(argument)],
                    stdout=devnull,
                    stderr=devnull,
                )
                if comp.returncode != 0:
                    print('WARNING: Non-zero exit code during fiber submission. Continuing to next run...')
            os.chdir(reset_dir)

        print(f"\nRun {argument} runtime: {time.strftime('%H:%M:%S', time.gmtime(elapsed))} (hh:mm:ss)")

    # cleanup for console viewing/inspecting
    del start, end
