#!/usr/bin/env python3.7

"""Remove specified files from sample directories.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import sys
from pathlib import Path

# these are the parts of files we want removed
# NOTE: be careful with "out" -- added warning!
INCLUDED_FILENAMES = ['runtime', 'blank', 'special', 'logs', 'start_']


def remove_empty_directories(directory: str, verbose):
    """Remove empty directories.

    :param directory: The top directory to start removing empty directories from.
    :param verbose: Whether to print out the directories being removed.
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
    """Remove specified files from sample directories.

    :param args: The command line arguments.
    """
    n_removed_files = 0
    global INCLUDED_FILENAMES
    if args.filename:
        INCLUDED_FILENAMES = [args.filename]
    proceed = input(
        'All files with names containing any of the following strings:\n'
        f'\t{INCLUDED_FILENAMES}\n'
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

    if 'out' in INCLUDED_FILENAMES:
        proceed = input(
            'You included \'out\' in INCLUDED_FILENAMES (i.e., files to remove). '
            '\n\t Are you sure you would you like to proceed?\n'
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

            if any(included_filename in filepath for included_filename in INCLUDED_FILENAMES):
                try:
                    if args.verbose:
                        print(f'\tREMOVE FILE: {filepath}')
                    os.remove(filepath)
                    n_removed_files += 1
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

    print(f'Removed {n_removed_files} file(s).')
