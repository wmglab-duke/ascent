#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# builtins
import os
import time
import sys

# ascent
from src.runner import Runner
from src.utils.enums import SetupMode, Config
from .env_setup import run as env_setup


def run(args):
    # test
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 7):
        print('You are running Python {}.{}, but 3.7 or later required'.format(sys.version_info.major,
                                                                               sys.version_info.minor))
        exit(1)

    # create bin/ directory for storing compiled Java files if it does not yet exist
    if not (os.path.exists('bin')):
        os.mkdir('bin')

    for argument in args.run_indices:
        # START timer
        start = time.time()

        try:
            int(argument)
        except ValueError:
            print('Invalid type for argument: {}\n'
                  'All arguments must be positive integers.'.format(argument))
            exit(1)

        if int(argument) < 0:
            print('Invalid sign for argument: {}\n'
                  'All arguments must be positive integers.'.format(argument))
            exit(1)

        print('\n\n########## STARTING RUN {} ##########\n\n'.format(argument))

        run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(argument))
        if not os.path.exists(run_path):
            print('Invalid run configuration path: {}'.format(run_path))
            exit(1)

        env_path = os.path.join('config', 'system', 'env.json')
        if not os.path.exists(env_path):
            print('Missing env configuration file: {}'.format(env_path))
            env_setup(env_path)

        # initialize Runner (loads in parameters)
        runner = Runner(int(argument))
        runner.add(SetupMode.NEW, Config.RUN, run_path)
        runner.add(SetupMode.NEW, Config.ENV, env_path)
        runner.add(SetupMode.OLD, Config.CLI_ARGS, vars(args))

        # populate environment variables
        runner.populate_env_vars()

        # ready, set, GO!
        runner.run()

        # END timer
        end = time.time()
        print('\nruntime: {} seconds ({} minutes)'.format(round(end - start,2),round((end - start)/60),3))

    # cleanup for console viewing/inspecting
    del start, end
