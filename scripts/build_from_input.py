#!/usr/bin/env python3.7

"""Convert .json files in an input/* directory to valid run configurations.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""
import filecmp
import glob
import json
import os
import shutil
import sys
from datetime import datetime

MAXIMUM_INDEX = 2147482999


def write_json(obj: dict, path: str):
    """Write json helper function.

    :param obj: object (dictionary) to serialize
    :param path: file path
    """
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def load_json(path: str) -> dict:
    """Read json helper function.

    :param path: file path
    :returns: json dictionary
    """
    with open(path) as f:
        return json.load(f)


def get_config_ints(search_path: str) -> list[int]:
    r"""Get a list of integers from files with an extension in /config/user/runs for example.

    :param search_path: Path in which to search for \*.json.
    :returns: int_list Integer names of every integer file/folder name in the path.
    """
    int_list = []
    # Todo: Make this more robust
    if '*.json' in search_path:
        new_search_path = search_path
    else:
        ai = search_path.index('*')
        new_search_path = search_path[: ai + 1]
    json_names = [os.path.split(jf)[-1].split('.')[0] for jf in glob.glob(new_search_path)]
    json_names = [jn for jn in json_names if jn.isnumeric()]
    for json_name in sorted(json_names, key=lambda jn: int(jn)):
        if int(json_name) <= 2147482999:
            int_list.append(int(json_name))
    return int_list


def get_available_ints(int_list: list[int], n_ints: int, start_int: int = 0):
    """Get the next integer not in a list.

    :param int_list: list of integers.
    :param n_ints: number of integers not in int_list to return.
    :param start_int: integer at which to start search. 0 if none supplied.
    :returns: available_ints next integer not in int_list.
    """
    next_int = start_int
    available_ints = []
    while len(available_ints) < n_ints:
        while next_int in int_list:
            next_int += 1
        available_ints.append(next_int)
        next_int += 1
    return available_ints


def comp_jsons(json_path: str, existing_jsons: list[str]) -> tuple[int, str] or tuple[None, None]:
    """Compare list of json files with a target json file.

    :param json_path: file path of target .json
    :param existing_jsons: list of file paths to compare against target
    :returns: tuple(ei, exist_json) for index in existing_jsons list and file path for match
                or tuple(None, None) if no match found.
    """
    for ei, exist_json in enumerate(existing_jsons):
        if filecmp.cmp(json_path, exist_json, shallow=False):
            return ei, exist_json
    return None, None


def new_json_ints(json_files: list[str], search_pattern: str) -> list[int]:
    """Get unused integer indices for json files and find existing matches.

    :param json_files: json files for which to make new integer indices
    :param search_pattern: string pattern (with * wildcards) with which to search for existing jsons
    :returns: list of new or matching integer indices for each file in json_files
    """
    new_ints = []

    # get existing json names
    exist_ints = get_config_ints(search_pattern)
    exist_files = [search_pattern.replace('*', str(ei)) for ei in exist_ints]

    # get json names for identical files
    for jf in json_files:
        ei, new_path = comp_jsons(jf, exist_files)
        if ei is None:
            new_ints.append(ei)
        else:
            new_ints.append(exist_ints[ei])

    # get indices of jsons without identical files in directory
    none_inds = []
    for i, jn in enumerate(new_ints):
        if jn is None:
            none_inds.append(i)

    # set next available indices for those with None
    available_ints = get_available_ints(exist_ints, len(none_inds))
    for i, ai in zip(none_inds, available_ints):
        new_ints[i] = ai

    return new_ints


def write_jsons(json_dict: dict, path_pattern: str, root_dir: str = ''):
    """Write several integer-named jsons with a file pattern.

    :param json_dict: Dictionary of origin_json_file_path: integer
    :param path_pattern: file path string pattern (with * wildcards) with which to write json files
    :param root_dir: root directory to prepend to pattern
    """
    for in_json, json_int in json_dict.items():
        new_path = os.path.join(root_dir, path_pattern.replace('*', str(json_int)))
        os.makedirs(os.path.split(new_path)[0], exist_ok=True)
        shutil.copyfile(in_json, new_path)


def refactor_folders(in_search_path: str, out_search_path: str) -> dict:
    """Copy a folder of json files to another folder and rename them as unique integer indices.

    :param in_search_path: source folder for json files
    :param out_search_path: destination folder for new integer-indexed json files
    :returns: json_dict with k:v pairs source_file_path:dest_file_path
    """
    in_jsons = glob.glob('*.json', root_dir=in_search_path)
    new_ints = new_json_ints(in_jsons, out_search_path)
    json_dict = dict(zip(in_jsons, new_ints))
    write_jsons(json_dict, out_search_path)
    return json_dict


def build(input_name: str) -> list[int]:
    """Build ASCENT runs for each input directory.

    :param input_name: folder name for which to generate runs in the root/input directory.
    :returns: list of generated run integers corresponding to the runs found in input folders
    :raises FileNotFoundError: if input_name does not exist in /input folder
    """
    grouppath = os.path.join('config', 'user', 'rungroups.json')
    if os.path.exists(grouppath):
        with open(grouppath) as f:
            rungroups = json.load(f)

        if input_name in rungroups:
            overwrite = input(f'Run group exists for {input_name}, overwrite? (Y/n)')
            if overwrite != 'Y':
                print(f'Aborted build for {input_name} because it is a key in /config/user/rungroups.json')
                sys.exit()
    else:
        rungroups = {}

    input_folder = f'input/{input_name}'

    run_tracker_json = input_folder + '/run_tracking.json'
    if os.path.exists(run_tracker_json):
        run_tracker = load_json(run_tracker_json)
    else:
        run_tracker = {}
    new_run_tracker = {}

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"{input_name} sample folder not found in /input folder")

    print(f'\n########## BUILDING FILES FOR {input_name} ##########\n')

    # Make ASCENT config folder structure
    sims_dir = 'config/user/sims'
    os.makedirs(sims_dir, exist_ok=True)
    samples_dir = 'samples'
    os.makedirs(samples_dir, exist_ok=True)
    runs_dir = 'config/user/runs'
    os.makedirs(runs_dir, exist_ok=True)

    # Get sims from input folder
    in_sim_path = input_folder + '/sims/*.json'
    in_sim_jsons = glob.glob(in_sim_path)
    out_sim_path = sims_dir + '/*.json'
    new_ints = new_json_ints(in_sim_jsons, out_sim_path)
    sims_dict = dict(zip(in_sim_jsons, new_ints))
    write_jsons(sims_dict, out_sim_path)

    # Get samples from input folder
    in_sample_path = input_folder + '/samples/*.json'
    in_sample_jsons = glob.glob(in_sample_path)
    out_sample_path = samples_dir + '/*/sample.json'
    new_sample_ints = new_json_ints(in_sample_jsons, out_sample_path)
    samples_dict = dict(zip(in_sample_jsons, new_sample_ints))
    write_jsons(samples_dict, out_sample_path)

    # Get models from input folder
    in_model_path = input_folder + '/models/*.json'
    in_model_jsons = glob.glob(in_model_path)

    # Get runs from input folder
    in_run_path = input_folder + '/runs/*.json'
    in_run_jsons = glob.glob(in_run_path)
    out_run_path = runs_dir + '/*.json'

    # Iterables of 3-tuples with form (NAME JSON_PATH INT_INDEX)
    runs_iter = tuple([(k.split('/')[-1], k, -1) for k in in_run_jsons])
    for run_name, run_json, _ in runs_iter:
        run_dict = load_json(run_json)

        # Edit sample name in run_dict to sample index
        this_sample_name = run_dict['sample']
        this_sample_json = None
        for sj in samples_dict.keys():
            if os.path.split(sj)[-1] == this_sample_name:
                this_sample_json = sj
                break
        this_sample_int = samples_dict[this_sample_json]
        run_dict['sample'] = this_sample_int
        out_sample_json = f'samples/{this_sample_int}/sample.json'
        sample_dict = load_json(out_sample_json)
        sample_dict['sample'] = input_name
        write_json(sample_dict, out_sample_json)

        # Get json paths for the run's models
        these_in_model_names = run_dict['models']
        these_in_model_jsons = []
        for mn in these_in_model_names:
            for mj in in_model_jsons:
                if os.path.split(mj)[-1] == mn:
                    these_in_model_jsons.append(mj)
                    break

        # Reorganize model files for this run
        out_model_path = samples_dir + f'/{this_sample_int}/models/*/model.json'
        new_model_ints = new_json_ints(these_in_model_jsons, out_model_path)
        these_models_dict = dict(zip(these_in_model_jsons, new_model_ints))
        write_jsons(these_models_dict, out_model_path)
        run_dict['models'] = new_model_ints

        # Edit run dict to have sim indices instead of file names
        these_in_sim_names = run_dict['sims']
        these_in_sim_jsons = []
        for sn in these_in_sim_names:
            for sj in in_sim_jsons:
                if os.path.split(sj)[-1] == sn:
                    these_in_sim_jsons.append(sj)
                    break
        run_dict['sims'] = [sims_dict[sj] for sj in these_in_sim_jsons]

        tmp_json = os.path.join(runs_dir, 'tmp_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + '.json')
        write_json(run_dict, tmp_json)
        new_run_int = new_json_ints([tmp_json], out_run_path)[0]
        write_jsons({tmp_json: new_run_int}, out_run_path)
        os.remove(tmp_json)

        new_run_tracker.update(
            {
                str(new_run_int): {
                    'run_time': datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"),
                    'run_json': run_json,
                    'run_name': run_name,
                    'input_name': input_name,
                    'sample_json': this_sample_json,
                    'sample_int': this_sample_int,
                    'models': {v: k for k, v in these_models_dict.items()},
                    'sims': {sims_dict[sj]: sj for sj in these_in_sim_jsons},
                }
            }
        )

    run_ints, run_jsons = zip(*[(int(k), v['run_json']) for k, v in new_run_tracker.items()])

    print("New runs created for: ")
    for run_json, run_int in zip(run_jsons, run_ints):
        print('\t', run_int, run_json)
    run_tracker.update(new_run_tracker)
    run_tracker = dict(sorted(run_tracker.items(), key=lambda x: int(x[0])))
    write_json(run_tracker, run_tracker_json)

    rungroups[input_name] = run_ints
    with open(grouppath, 'w') as f:
        json.dump(rungroups, f, indent=2)

    return run_ints


def run(args):
    """Build pipeline file structure from input/sample folder.

    :param args: The command line arguments.
    """
    build(args.input_name)


def main():
    """Build runs for all input folders."""
    input_folders = glob.glob('input')
    input_folders = list(filter(lambda x: os.path.isdir(os.path.join('input', x)), input_folders))
    build(input_folders[0])


if __name__ == '__main__':
    main()
