#!/usr/bin/env python3.7

import os
import time
import sys

from src import Runner
from src.utils.enums import SetupMode, ConfigKey

# START timer
start = time.time()

if len(sys.argv != 1):
    print('INVALID number of arguments to start.py')
    exit(1)

# get main configuration file
# master_config_file_path = os.path.join('.config', 'master.json')
run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(sys.argv[0]))
# master_config_file_path = os.path.join('.config', 'master.json')

# initialize Runner (loads in parameters)
runner = Runner()
runner.add(SetupMode.NEW, ConfigKey.RUN, run_path)

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
