#!/usr/bin/env python3.7

import os
import time
import sys

from src import Runner
from src.utils.enums import SetupMode, ConfigKey

# START timer
start = time.time()

if len(sys.argv) != 2:
    print('INVALID number of arguments to start.py')
    exit(1)

run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(sys.argv[1]))
if not os.path.exists(run_path):
    print('INVALID run configuration path: {}'.format(run_path))

env_path = os.path.join('config', 'system', 'env.json')
if not os.path.exists(env_path):
    print('INVALID env configuration path: {}'.format(env_path))

# get main configuration file
# master_config_file_path = os.path.join('.config', 'master.json')
# master_config_file_path = os.path.join('.config', 'master.json')

# initialize Runner (loads in parameters)
runner = Runner()
runner.add(SetupMode.NEW, ConfigKey.RUN, run_path)
runner.add(SetupMode.NEW, ConfigKey.ENV, env_path)

# runner = Runner(master_config_file_path)

# ready, set, GO!
# runner.run()
# runner.trace_test()
# runner.fascicle_test()
# runner.reposition_test()
# runner.reposition_test2()
# runner.manager_test()
runner.smart_run()
# runner.load_up_manager()

# END timer
end = time.time()
print('\nruntime: {}'.format(end - start))

# cleanup for console viewing/inspecting
del start, end
