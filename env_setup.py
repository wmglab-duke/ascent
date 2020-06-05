#!/usr/bin/env python3.7

import json
import os
from src.utils.enums import Env

def env_setup(env_path: str):

    print('Start environment path variables setup.')

    result = {}
    for key in Env.vals.value:
        while True:
            value = input('Enter path for {}: '.format(key))

            if os.path.exists(value):
                result[key] = value
            else:
                print('Nonexistent path provided. Please try again.')

    with open(env_path, 'r+') as file:
        file.seek(0)  # go to beginning of file to overwrite
        file.write(json.dumps(result))
        file.truncate()  # remove any trailing characters from old file
    
    print('Success! Environment path variables updated.\n')