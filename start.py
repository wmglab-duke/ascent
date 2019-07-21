import os

from src import Runner

# get main configuration file
main_config_file_path = os.path.join('.config', 'master.json')

# initialize Runner (loads in parameters)
runner = Runner(main_config_file_path)

# ready, set, GO!
runner.run()
