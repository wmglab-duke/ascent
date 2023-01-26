#!/usr/bin/env python3.7

"""Sets up environment path variables for the ASCENT.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import json
import os

from src.utils.enums import Env

default_env = os.path.join('config', 'system', 'env.json')


def run(args, env_path=default_env):
    """Set up environment variables.

    :param args: command line arguments
    :param env_path: path to environment configuration file
    """
    print('Start environment path variables setup.')

    result = {}
    for key in Env.vals.value:
        while True:
            value = input(f'Enter path for {key}: ')

            if os.path.exists(value) or key == 'ASCENT_NSIM_EXPORT_PATH':
                result[key] = value
                break
            else:
                print('Nonexistent path provided. Please try again.')

    with open(env_path, 'w+') as file:
        file.seek(0)  # go to beginning of file to overwrite
        file.write(json.dumps(result, indent=2))
        file.truncate()  # remove any trailing characters from old file

    print('Success! Environment path variables updated.\n')


if __name__ == "__main__":
    run()
