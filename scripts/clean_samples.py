#!/usr/bin/env python3.7

"""Remove files except those specified from samples directories.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import sys
from pathlib import Path

EXCLUDED_FILENAMES = [
    '.mph',
    'im.json',
    'Primitive.json',
    'sample.json',
    'model.json',
    'explicit.txt',
]


def remove_empty_directories(directory: str, verbose):
    """Remove empty directories from a given directory.

    :param directory: directory to remove empty directories from
    :param verbose: whether to print out information about directory removal
    """
    for path in os.listdir(directory):
        subdirectory = os.path.join(directory, path)
        if os.path.isdir(subdirectory):
            remove_empty_directories(subdirectory, verbose)

    if os.path.isdir(directory) and len(os.listdir(directory)) == 0:
        try:
            if verbose:
                print(f'\tREMOVE DIR: {directory}')
            os.rmdir(directory)
        except (FileNotFoundError, IsADirectoryError) as e:
            print(f'Could not remove {directory}, {e}')
    else:
        if verbose:
            print(f'\tKEEP DIR: {directory}')


def run(args):
    """Remove files except those specified from samples directories.

    :param args: command line arguments
    """
    global EXCLUDED_FILENAMES
    if args.full_reset:
        EXCLUDED_FILENAMES = ['sample.json', 'model.json']
    proceed = input(
        'All files EXCEPT those whose names end with the following strings:\n'
        f'\t{EXCLUDED_FILENAMES}\n'
        'will be removed from the following sample directories:\n'
        f'\t{args.sample_indices}\n'
        '\n\t Would you like to proceed?\n'
        '\t\t 0 = NO\n'
        '\t\t 1 = YES\n'
    )
    if int(proceed) != 1:
        sys.exit()
    else:
        print('Proceeding...')

    for sample in args.sample_indices:

        if args.verbose:
            print(f'Sample: {sample}')
            print('\n\t- - - - - - FILES - - - - - -\n')

        sample_path = Path(os.path.join('samples', f'{sample}'))

        # remove files
        for filepath in [str(path.absolute()) for path in sample_path.glob('**/*')]:

            # skip over directories for now
            if os.path.isdir(filepath):
                continue

            if not any([filepath.endswith(excluded_filename) for excluded_filename in EXCLUDED_FILENAMES]):
                try:
                    if args.verbose:
                        print(f'\tREMOVE FILE: {filepath}')
                    os.remove(filepath)
                except (FileNotFoundError, IsADirectoryError) as e:
                    print(f'Could not remove {filepath}, {e}')
            else:
                if args.verbose:
                    print(f'\tKEEP FILE: {filepath}')

        # remove empty directories
        if args.verbose:
            print('\n\t- - - - - DIRECTORIES - - - -\n')

        remove_empty_directories(str(sample_path.absolute()), args.verbose)

        if args.verbose:
            print('\n\n')
