import os
import time

from src import Runner

# START timer
start = time.time()

# get main configuration file
master_config_file_path = os.path.join('.config', 'master.json')

# initialize Runner (loads in parameters)
runner = Runner(master_config_file_path)

# ready, set, GO!
runner.run()
#runner.test1()
runner.test2()

# END timer
end = time.time()
print('runtime: {}'.format(end - start))
