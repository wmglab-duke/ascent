import os
from pathlib import Path

EXCLUDED_FILENAMES = [
    'sample.json',
    'model.json'
]


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
        print('Usage: python run clean_samples [-v] sample_1 sample_2 ...\n where all sample_i are integers')
        return

    for sample in args[first_sample_index:]:

        if VERBOSE:
            print(f'Sample: {sample}')

        sample_path = Path(os.path.join('samples', f'{sample}'))

        # remove files
        print('\n\t- - - - - - FILES - - - - - -\n')
        for filepath in [str(path.absolute()) for path in sample_path.glob('**/*')]:

            # skip over directories for now
            if os.path.isdir(filepath):
                continue

            if not any([filepath.endswith(excluded_filename) for excluded_filename in EXCLUDED_FILENAMES]):
                os.remove(filepath)
                if VERBOSE:
                    print(f'\tREMOVE FILE: {filepath}')

            else:
                if VERBOSE:
                    print(f'\tKEEP FILE: {filepath}')

        # remove empty directories
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
    
        print('\n\n')

