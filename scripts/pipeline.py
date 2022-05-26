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
import subprocess

# ascent
from src.runner import Runner
from src.utils.enums import SetupMode, Config, Env
from .env_setup import run as env_setup


def run(args):
    # test
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 7):
        print('You are running Python {}.{}, but 3.7 or later required'.format(sys.version_info.major,
                                                                               sys.version_info.minor))
        sys.exit()

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
            sys.exit()

        if int(argument) < 0:
            print('Invalid sign for argument: {}\n'
                  'All arguments must be positive integers.'.format(argument))
            sys.exit()

        print('\n\n########## STARTING RUN {} ##########\n\n'.format(argument))

        run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(argument))
        if not os.path.exists(run_path):
            print('Invalid run configuration path: {}'.format(run_path))
            sys.exit()

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
        elapsed = end - start
        print('\nruntime: {} (hh:mm:ss)'.format(time.strftime('%H:%M:%S', time.gmtime(elapsed))))

        if args.auto_submit or runner.search(Config.RUN,'auto_submit_fibers')==True:
            print('Submitting fibers for run {}'.format(argument))
            #submit fibers before moving on to next run
            reset_dir = os.getcwd()
            export_path = runner.search(Config.ENV, Env.NSIM_EXPORT_PATH.value)
            os.chdir(export_path)
            with open(os.devnull, 'wb') as devnull:
                subprocess.check_call(['python','submit.py', '-s',str(argument)], stdout=devnull, stderr=devnull)
            os.chdir(reset_dir)

    # cleanup for console viewing/inspecting
    del start, end
