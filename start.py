#!/usr/bin/env python3.7

# builtins
import os
import time
import sys

# access
from src.runner import Runner
from src.utils.enums import SetupMode, Config
from env_setup import env_setup

if __name__ == "__main__":
    # test
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 7):
        print('You are running Python {}.{}, but 3.7 or later required'.format(sys.version_info.major,
                                                                            sys.version_info.minor))
        exit(1)

    if len(sys.argv) == 1:
        print('Too few arguments to start.py (must have at least one run index)')
        exit(1)

    # create bin/ directory for storing compiled Java files if it does not yet exist
    if not (os.path.exists('bin')):
        os.mkdir('bin')

    for argument_index in range(1, len(sys.argv)):
        # START timer
        start = time.time()

        argument = sys.argv[argument_index]

        try:
            int(argument)
        except ValueError:
            print('Invalid type for argument: {}\n'
                'All arguments must be positive integers.'.format(argument))

        if int(argument_index) < 0:
            print('Invalid sign for argument: {}\n'
                'All arguments must be positive integers.'.format(argument))

        print('\n\n########## STARTING RUN {} ##########\n\n'.format(argument))

        run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(argument))
        if not os.path.exists(run_path):
            print('Invalid run configuration path: {}'.format(run_path))

        env_path = os.path.join('config', 'system', 'env.json')
        if not os.path.exists(env_path):
            print('Missing env configuration file: {}'.format(env_path))
            env_setup(env_path)

        # initialize Runner (loads in parameters)
        runner = Runner(int(argument))
        runner.add(SetupMode.NEW, Config.RUN, run_path)
        runner.add(SetupMode.NEW, Config.ENV, env_path)

        # populate environment variables
        runner.populate_env_vars()

        # ready, set, GO!
        runner.run()

        # END timer
        end = time.time()
        print('\nruntime: {}'.format(end - start))

    # cleanup for console viewing/inspecting
    del start, end
    

