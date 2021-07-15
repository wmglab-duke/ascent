#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os
from pathlib import Path

# these are the parts of files we want removed
# NOTE: be careful with "out" -- added warning!
INCLUDED_FILENAMES = [
    'runtime',
    'blank',
    'special',
    'logs',
    'start_'
]

if 'out' in INCLUDED_FILENAMES:
    proceed = input('You included \'out\' in INCLUDED_FILENAMES (i.e., files to remove). '
                    '\n\t Would you like to proceed?\n'
                    '\t\t 0 = NO\n'
                    '\t\t 1 = YES\n')
    if not int(proceed):
        quit()
    else:
        print('Proceeding...')


def run(args):


    # if no verbose arg passed (minimum number of args)
    VALID_ARGS = len(args) >= 2
    first_sample_index = 1
    VERBOSE = False

    # if verbose arg passed
    if args[1] == '-v':
        VALID_ARGS = len(args) >= 3
        first_sample_index = 2
        VERBOSE = True

    # ensure all args are integers
    for arg in args[first_sample_index:]:
        try:
            int(arg)
        except ValueError:
            VALID_ARGS = False
            break

    # exit if any validation failed
    if not VALID_ARGS:
        print('Usage: python run tidy_samples [-v] sample_1 sample_2 ...\n where all sample_i are integers')
        return

    for sample in args[first_sample_index:]:

        if VERBOSE:
            print(f'Sample: {sample}')

        sample_path = Path(os.path.join('samples', f'{sample}'))

        # remove files
        if VERBOSE:
            print('\n\t- - - - - - FILES - - - - - -\n')
        for filepath in [str(path.absolute()) for path in sample_path.glob('**/*')]:

            # skip over directories for now
            if os.path.isdir(filepath):
                continue

            if any([included_filename in filepath for included_filename in INCLUDED_FILENAMES]):
                os.remove(filepath)
                if VERBOSE:
                    print(f'\tREMOVE FILE: {filepath}')

            else:
                if VERBOSE:
                    print(f'\tKEEP FILE: {filepath}')

        # remove empty directories
        if VERBOSE:
            print('\n\t- - - - - DIRECTORIES - - - -\n')
        def remove_empty_directories(directory: str):

            for path in os.listdir(directory):
                subdirectory = os.path.join(directory, path)
                if os.path.isdir(subdirectory):
                    remove_empty_directories(subdirectory)

            if os.path.isdir(directory) and len(os.listdir(directory)) == 0:
                os.rmdir(directory)
                if VERBOSE:
                    print(f'\tREMOVE DIR: {directory}')

            else:
                if VERBOSE:
                    print(f'\tKEEP DIR: {directory}')

        remove_empty_directories(str(sample_path.absolute()))

        if VERBOSE:
            print('\n\n')

