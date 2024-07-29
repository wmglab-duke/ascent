#!/usr/bin/env python3.7

"""The copyrights of this software are owned by Duke University.

Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import warnings

import numpy as np
import pandas as pd

from src.core.query import Query

# RUN THIS FROM REPOSITORY ROOT

sys.path.append(os.path.sep.join([os.getcwd(), '']))


def load(config_path: str):
    """Load in json data and returns to user and assume it has already been validated.

    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path) as handle:
        return json.load(handle)


def paths_from_keeps(my_path: str, my_keeps: dict, my_paths=None):
    """Recursively find all paths that match the keeps dict.

    :param my_path: path to parameters in keeps.json
    :param my_keeps: keeps.json
    :param my_paths: list of paths to return to user (default None) for files to keep
    :return: list of paths to return to user (default None) for files to keep
    """
    if my_paths is None:
        my_paths = []

    for key in my_keeps:
        new_path = os.path.join(my_path, key)
        if my_keeps[key] is True:
            my_paths.append(new_path)
        elif my_keeps[key] is False:  # noqa: R507
            continue
        elif isinstance(my_keeps[key], dict):
            paths_from_keeps(new_path, my_keeps[key], my_paths)

    return my_paths


def replace_placeholders(my_thing_to_copy: str, my_sample: int, my_model: int, my_sim: int, my_n_sim: int):
    """Replace placeholders in a string.

    :param my_thing_to_copy: the string to replace placeholders in
    :param my_sample: the sample index
    :param my_model: the model index
    :param my_sim: the simulation index
    :param my_n_sim: the n_sim index
    :return: the string with placeholders replaced
    """
    my_place_holders = ["<sample_index>", "<model_index>", "<sim_index>", "<n_sim_index>"]
    my_indices = [my_sample, my_model, my_sim, my_n_sim]

    for place_holder, index in zip(my_place_holders, my_indices):
        my_thing_to_copy = my_thing_to_copy.replace(place_holder, str(index))

    return my_thing_to_copy


def to_json(output_path: str, my_dict: dict):
    """Write json file.

    :param output_path: the path to write to
    :param my_dict: the dict to write
    """
    with open(output_path, "w") as f:
        json.dump(my_dict, f, indent=2)


def handoff(comsol_files: list[str], env: dict, my_dataset_index: int):
    """Handoff the comsol files to the comsol server.

    :param comsol_files: list of comsol files to handoff for clearing
    :param env: the environment variables
    :param my_dataset_index: the dataset index
    :raises ValueError: if the compile step or handoff fails
    """
    comsol_path = env['ASCENT_COMSOL_PATH']
    jdk_path = env['ASCENT_JDK_PATH']
    class_name = 'ModelClearer'
    export_directory = env['ASCENT_DATASET_EXPORT_PATH']

    if sys.platform.startswith('win'):  # windows
        # prep COMSOL files for java
        comsol_files = [comsol_file.replace(os.sep, '/') for comsol_file in comsol_files]
        server_command = [f'{comsol_path}\\bin\\win64\\comsolmphserver.exe', '-login', 'auto']
        compile_command = (
            f'""{jdk_path}\\javac" '
            f'-cp "..\\bin\\json-20190722.jar";"{comsol_path}\\plugins\\*" '
            'model\\*.java -d ..\\bin"'
        )
        java_command = (
            f'""{comsol_path}\\java\\win64\\jre\\bin\\java" '
            f'-cp "{comsol_path}\\plugins\\*";"..\\bin\\json-20190722.jar";"..\\bin" '
            f'model.{class_name} "{comsol_files}" "{export_directory}" "{my_dataset_index}""'
        )
    else:
        server_command = [f'{comsol_path}/bin/comsol', 'mphserver', '-login', 'auto']

        compile_command = (
            f'{jdk_path}/javac -classpath '
            f'../bin/json-20190722.jar:'
            f'{comsol_path}/plugins/* model/*.java -d ../bin'
        )
        # https://stackoverflow.com/questions/219585/including-all-the-jars-in-a-directory-within-the-java-classpath
        if sys.platform.startswith('linux'):  # linux
            java_comsol_path = comsol_path + '/java/glnxa64/jre/bin/java'
        else:  # mac
            java_comsol_path = comsol_path + '/java/maci64/jre/Contents/Home/bin/java'

        java_command = (
            f'{java_comsol_path} '
            f'-cp .:$(echo {comsol_path}/plugins/*.jar | '
            f'tr \' \' \':\'):../bin/json-20190722.jar:../bin model.{class_name} '
            f'"{comsol_files}" "{export_directory}" "{my_dataset_index}"'
        )

    # start comsol server
    subprocess.Popen(server_command, close_fds=True, shell=True)
    # wait for server to start
    time.sleep(10)
    os.chdir('src')
    # compile java code
    exit_code = os.system(compile_command)
    if exit_code != 0:
        raise ValueError('Java classes failed to compile')
    # run java code
    exit_code = os.system(java_command)
    if exit_code != 0:
        raise ValueError('Error occurred during handoff() to Java')
    os.chdir('..')


def make_comsol_cleared_readme(
    my_dataset_index, comsol_clearing_config_directory, samples_sub_sam_path, files_readme_path
):
    """Make the readme for the comsol cleared files.

    :param my_dataset_index: the dataset index
    :param comsol_clearing_config_directory: the comsol clearing config directory
    :param samples_sub_sam_path: the path to the samples sub-sam file which maps samples to sparc sub and sam
    :param files_readme_path: the path to the file's readme
    """
    comsol_clearing_exceptions_path = os.path.join(comsol_clearing_config_directory, f'{my_dataset_index}.json')
    comsol_clearing_exceptions = load(comsol_clearing_exceptions_path)

    samples_key = load(samples_sub_sam_path)

    meshes_kept_mesh = []
    for x in comsol_clearing_exceptions["mesh.mph"]:
        sub = samples_key[str(x[0])]['sub']
        sam = samples_key[str(x[0])]['sam']
        ascent_sample = x[0]
        ascent_model = x[1]
        meshes_kept_mesh.append(f'sub-{sub}/sam-{sam}-sub-{sub}\tASCENT:(Sample {ascent_sample}, Model {ascent_model})')

    bases_kept_mesh = []
    for x in comsol_clearing_exceptions["<basis_index>.mph"]["mesh"]:
        sub = samples_key[str(x[0])]['sub']
        sam = samples_key[str(x[0])]['sam']
        ascent_sample = x[0]
        ascent_model = x[1]
        bases_index = x[2]
        bases_kept_mesh.append(
            f'sub-{sub}/sam-{sam}-sub-{sub}'
            f'\tASCENT:(Sample {ascent_sample}, Model {ascent_model}, Bases Index {bases_index})'
        )

    bases_kept_solution = []
    for x in comsol_clearing_exceptions["<basis_index>.mph"]["solution"]:
        sub = samples_key[str(x[0])]['sub']
        sam = samples_key[str(x[0])]['sam']
        ascent_sample = x[0]
        ascent_model = x[1]
        bases_index = x[2]
        bases_kept_solution.append(
            f'sub-{sub}/sam-{sam}-sub-{sub}'
            f'\tASCENT:(Sample {ascent_sample}, Model {ascent_model}, Bases Index {bases_index})'
        )

    group_names = [
        'mesh.mph files with mesh retained',
        '<basis_index>.mph files with mesh retained',
        '<basis_index>.mph files with solution retained',
    ]
    with open(files_readme_path, 'bw+') as f:
        f.write(
            b'# Files for which the mesh/solution were retained.\n'
            b'<basis_index>.mph files can have dual membership\n\n'
        )
        for group, group_name in zip([meshes_kept_mesh, bases_kept_mesh, bases_kept_solution], group_names):
            f.write(f'# {group_name}\n'.encode())
            for fi, file in enumerate(group):
                if fi != len(group) - 1:
                    f.write(f'* {file}\n'.encode())
                else:
                    f.write(f'* {file}\n\n'.encode())


def tidy_n_sim_index_json(thing_to_copy: str, model_config_path: str, tmp_files_dataset_directory: str):
    """Tidy up the n_sim_index.json file and copy it to the dataset directory.

    This means removing the keys that are not needed.
    :param thing_to_copy: the thing to copy, 'n_sim_index.json'
    :param model_config_path: the path to the model_config.json file
    :param tmp_files_dataset_directory: the path to the dataset directory
    :raises ValueError: if no active_srcs are found that match the cuff preset
    :return: output_path which is the path to the copied file
    """
    n_sim_index_json = load(thing_to_copy)
    model_config = load(model_config_path)
    cuff = model_config['cuff']['preset']

    keys = list(n_sim_index_json['active_srcs'])
    for key in keys:
        if key not in [cuff, 'default']:
            n_sim_index_json['active_srcs'].pop(key)

    if len(n_sim_index_json['active_srcs']) > 1 and 'default' in n_sim_index_json['active_srcs']:
        n_sim_index_json['active_srcs'].pop('default')
    elif len(n_sim_index_json['active_srcs']) == 1 and 'default' in n_sim_index_json['active_srcs']:
        n_sim_index_json['active_srcs'][cuff] = n_sim_index_json['active_srcs'].pop('default')
    elif len(n_sim_index_json['active_srcs']) == 0:
        raise ValueError('No active sources found in n_sim_index_json that match the cuff preset')

    rootdir = os.path.splitdrive(tmp_files_dataset_directory)[0]
    # save modified n_sim_index_json to tmp/
    output_file = os.path.join(os.sep, rootdir + os.sep, tmp_files_dataset_directory, thing_to_copy)
    output_folder = os.path.join(
        os.sep, rootdir + os.sep, tmp_files_dataset_directory, os.path.join(*thing_to_copy.split(os.sep)[:-1])
    )
    os.makedirs(output_folder, exist_ok=True)

    to_json(output_file, n_sim_index_json)

    return output_file


def run(args):
    """Run the script, which in this case is a list of dataset indices.

    :param args: the arguments passed to the script
    :raises ValueError: if the env_path, model_config_path, or dataset_path are not found
    :raises ValueError: if trying to run from a directory that is not the ASCENT root directory
    :raises ValueError: if the dataset was previously run
    :raises ValueError: if inconsistent sub/sam indices given
    :raises ValueError: if no way to scale the input nerve segmentations is provided (s.tif or scale_ratio)
    :return: None
    """
    # LOAD ENV CONFIG
    env_path = os.path.join('config', 'system', 'env.json')
    if not os.path.exists(env_path):
        raise ValueError(f'env_path does not exist, so likely not in ASCENT working directory:\n\t{env_path}')
    env_config = load(env_path)

    # FORCE PROGRAM TO BE IN ASCENT WORKING DIRECTORY
    if not os.getcwd() == env_config['ASCENT_PROJECT_PATH']:
        raise ValueError('You are trying to run this script from a directory other than your ASCENT working directory')

    # LOAD SYSTEM CONFIGS
    regex_path = os.path.join('config', 'system', 'regex_ascent_files.json')
    regex_legend = load(regex_path)

    # CONSTANTS
    comsol_file_ending = '.mph'

    # MAKE DIRECTORIES THAT USER NEEDS
    export_directory = env_config['ASCENT_DATASET_EXPORT_PATH']
    config_directory = os.path.join(export_directory, 'config')
    ux_directory = os.path.join(export_directory, 'modify_me')
    query_criteria_config_directory = os.path.join(config_directory, 'query_criteria')
    queried_indices_info_directory = os.path.join(config_directory, 'queried_indices_info')
    datasets_directory = os.path.join(export_directory, 'datasets')
    keeps_config_directory = os.path.join(config_directory, 'keeps')
    comsol_clearing_exceptions_directory = os.path.join(config_directory, 'comsol_clearing_exceptions')
    tmp_files_directory = os.path.join(export_directory, 'tmp')

    for directory in [
        export_directory,
        config_directory,
        ux_directory,
        query_criteria_config_directory,
        queried_indices_info_directory,
        datasets_directory,
        keeps_config_directory,
        tmp_files_directory,
    ]:
        os.makedirs(directory, exist_ok=True)

    # LOOP DATASET INDICES
    for dataset_index in args.dataset_indices:
        # START TIMER
        start = time.time()
        print(f'========================= START DATASET: {dataset_index} =========================')

        dataset_index_directory = os.path.join(datasets_directory, str(dataset_index))

        query_criteria_path = os.path.join(query_criteria_config_directory, f'{dataset_index}.json')
        queried_indices_path = os.path.join(ux_directory, f'{dataset_index}.xlsx')
        queried_indices_info_path = os.path.join(queried_indices_info_directory, f'{dataset_index}.json')

        # MAKE LIST OF INDICES FROM WHICH WE ARE COPYING THINGS
        if args.stage == 'query':
            query_excel_output(queried_indices_info_path, queried_indices_path, query_criteria_path)
        elif args.stage == 'generate':
            generate_dataset(
                args,
                comsol_clearing_exceptions_directory,
                comsol_file_ending,
                dataset_index,
                dataset_index_directory,
                env_config,
                keeps_config_directory,
                queried_indices_path,
                regex_legend,
                tmp_files_directory,
            )
        else:
            raise ValueError(f'Invalid stage: {args.stage}')

        # END TIMER
        end = time.time()
        elapsed = end - start
        elapsed = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        print(f'\ndataset_index {dataset_index} runtime: {elapsed} (HH:MM:SS)')

        print(f'======================= DONE WITH DATASET: {dataset_index} =======================')

    return


def generate_dataset(  # noqa: D103
    args,
    comsol_clearing_exceptions_directory,
    comsol_file_ending,
    dataset_index,
    dataset_index_directory,
    env_config,
    keeps_config_directory,
    queried_indices_path,
    regex_legend,
    tmp_files_directory,
):
    # check for existing dataset
    check_existing_dataset(args, dataset_index, dataset_index_directory)

    # make directories
    code_destination, data_destination, metadata_destination, tmp_files_dataset_destination = make_dataset_directories(
        dataset_index, dataset_index_directory, tmp_files_directory
    )

    # FREEZE ENVIRONMENT
    freeze_pip_requirements(metadata_destination)
    xls = pd.ExcelFile(queried_indices_path, engine='openpyxl')
    df = pd.read_excel(xls, None)

    # LOAD ASCENT INDICES, AND, IF APPLICABLE, USER-INDICATED PICKY SPARC INDICES
    ascent_indices, sparc_sams, sparc_subs = process_indices(df)

    # CHECK THAT PICKY ENTRIES WITH THE SAME SAMPLE (ASCENT) ARE ASSIGNED TO THE SAME SUB+SAM (SPARC);
    # ALSO ASSIGN PICKY SUB+SAM
    samples_sub_sam = assign_picky(ascent_indices, sparc_sams, sparc_subs)

    # ASSIGN NON-PICKY SUB+SAM, MAKE NEW INDICES LAZILY AS NEEDED TO FILL
    assign_non_picky(ascent_indices, samples_sub_sam, sparc_subs)

    # SAVE SAMPLES_SUB_SAM TO FILE FOR USE IN ANALYSIS CODE
    # TO CONVERT ASCENT FILE STRX TO DATASET FILE STRX WITH SPARC SUB+SAM
    samples_sub_sam_path = os.path.join(metadata_destination, 'samples_sub_sam.json')
    to_json(samples_sub_sam_path, samples_sub_sam)

    # COMPILE ALL INDICES OF THINGS WE WILL COPY: SAMPLE, MODEL, SIM, N-SIM,
    master_indices = compile_indices(ascent_indices, samples_sub_sam)

    # MAKE LIST OF THINGS TO COPY
    (
        destination_ascent_config_directory,
        directories_to_copy,
        file_lists_to_copy,
        files_to_copy,
        modified_files_to_copy,
        sims_to_copy,
    ) = list_things_to_copy(
        code_destination,
        dataset_index,
        keeps_config_directory,
        master_indices,
        samples_sub_sam,
        tmp_files_dataset_destination,
    )

    # CHECK THAT DIRECTORIES TO COPY ARE NOT EMPTY
    check_empty(directories_to_copy)

    # ADD FILES FROM FILE LISTS TO FILES TO COPY USING REGEX
    regex_copy_list(file_lists_to_copy, files_to_copy, regex_legend)

    # REMOVE DUPLICATE THINGS TO COPY
    directories_to_copy, files_to_copy, modified_files_to_copy = remove_duplicates(
        directories_to_copy, files_to_copy, modified_files_to_copy
    )

    # MAKE FOLDERS STRX IN OUTPUT DIRECTORY FOR FILES, LATER MAKE DIRECTORIES TO COPY WHEN WE COPY
    make_folders_for_copy(data_destination, files_to_copy, samples_sub_sam)

    # COPY FILES
    already_copied_files, copied_mph_files = copy_files(
        comsol_file_ending, data_destination, files_to_copy, samples_sub_sam
    )

    # COPY MODIFIED FILES
    copy_modified_files(data_destination, modified_files_to_copy, samples_sub_sam)

    # COPY DIRECTORIES
    copy_directories(comsol_file_ending, copied_mph_files, data_destination, directories_to_copy, samples_sub_sam)

    # COPY SIM CONFIGS
    copy_sim_configs(already_copied_files, destination_ascent_config_directory, sims_to_copy)

    # Clear COMSOL files and make README
    if len(copied_mph_files) > 1:
        make_comsol_cleared_readme(
            my_dataset_index=dataset_index,
            comsol_clearing_config_directory=comsol_clearing_exceptions_directory,
            samples_sub_sam_path=samples_sub_sam_path,
            files_readme_path=os.path.join(destination_ascent_config_directory, 'README.txt'),
        )
        handoff(comsol_files=copied_mph_files, env=env_config, my_dataset_index=dataset_index)

    # Get final sample and subject lists
    sams, subs = get_sams_subs(samples_sub_sam)
    print(f'NUMBER OF SUBJECTS: {len(subs)}')
    print(f'NUMBER OF SAMPLES: {len(sams)}')

    # DELETE TMPDIR
    shutil.rmtree(tmp_files_dataset_destination)
    print(f'REMEMBER TO ADD YOUR SCRIPTS AND VERIFY THAT THEY RUN IN PLACE FROM: {code_destination}\n')
    print(
        'CREATE METADATA FILES FOR DATASET WITH SODA:'
        '\n\tdataset_description.xlsx'
        '\n\tsubmission.xlsx'
        '\n\tsubjects.xlsx'
        '\n\tsamples.xlsx'
        '\nSee template for iterating on contents with your advisor at: <link forthcoming>'
    )


def get_sams_subs(samples_sub_sam):  # noqa: D103
    subs_sams_samples = []
    for sample in samples_sub_sam:
        subs_sams_samples.append((samples_sub_sam[sample]['sub'], samples_sub_sam[sample]['sam'], sample))
    subs_sams_samples.sort(key=lambda element: (element[0], element[1]))  # sort by sub, then sam
    subs, sams = [], []
    for sub, sam, _ in subs_sams_samples:
        # since ASCENT Sample is sub x sam
        if sub not in subs:
            subs.append(sub)
        sams.append(sam)
    return sams, subs


def copy_files(comsol_file_ending, data_destination, files_to_copy, samples_sub_sam):  # noqa: D103
    already_copied_files = []
    copied_mph_files = []  # to use later if you choose to clear mesh/solutions
    for file in files_to_copy:
        sample = int(file.split(os.sep)[1])
        sub = samples_sub_sam[sample]['sub']
        sam = samples_sub_sam[sample]['sam']
        base_directory = os.path.join(data_destination, f'sub-{sub}', f'sam-{sam}-sub-{sub}')
        new_file_path = os.path.join(base_directory, file)

        if not os.path.exists(new_file_path):
            shutil.copy(file, new_file_path)
        else:
            already_copied_files.append(file)

        if new_file_path.endswith(comsol_file_ending):
            copied_mph_files.append(new_file_path)
    if len(already_copied_files) > 0:
        print('FILES ALREADY COPIED OVER:')
        print('\t' + '\n\t'.join(already_copied_files))
    return already_copied_files, copied_mph_files


def copy_modified_files(data_destination, modified_files_to_copy, samples_sub_sam):  # noqa: D103
    already_copied_modified_files = []
    for file in modified_files_to_copy:
        dataset_file_path = file.split(os.path.join('samples'))[1]
        sample = int(dataset_file_path.split(os.sep)[1])
        sub = samples_sub_sam[sample]['sub']
        sam = samples_sub_sam[sample]['sam']
        base_directory = os.path.join(data_destination, f'sub-{sub}', f'sam-{sam}-sub-{sub}')
        new_file_path = os.path.join(base_directory, 'samples') + dataset_file_path

        if not os.path.exists(new_file_path):
            shutil.copy(file, new_file_path)
        else:
            already_copied_modified_files.append(file)
    if len(already_copied_modified_files) > 0:
        print('FILES (modified) ALREADY COPIED OVER:')
        print('\t' + '\n\t'.join(already_copied_modified_files))


def copy_sim_configs(already_copied_files, destination_ascent_config_directory, sims_to_copy):  # noqa: D103
    destination_ascent_sims_directory = os.path.join(destination_ascent_config_directory, 'sims')
    source_ascent_config_directory = os.path.join('config', 'user', 'sims')
    if len(sims_to_copy) > 0 and not os.path.exists(destination_ascent_sims_directory):
        os.makedirs(destination_ascent_sims_directory)
    for sim in sims_to_copy:
        source_sim_path = os.path.join(source_ascent_config_directory, f'{sim}.json')
        destination_sim_path = os.path.join(destination_ascent_sims_directory, f'{sim}.json')
        if not os.path.exists(destination_sim_path):
            shutil.copy(source_sim_path, destination_sim_path)
        else:
            already_copied_files.append(source_sim_path)


def copy_directories(  # noqa: D103
    comsol_file_ending, copied_mph_files, data_destination, directories_to_copy, samples_sub_sam
):  # noqa: D103
    already_copied_directories = []
    for directory in directories_to_copy:
        sample = int(directory.split(os.sep)[1])
        sub = samples_sub_sam[sample]['sub']
        sam = samples_sub_sam[sample]['sam']
        base_directory = os.path.join(data_destination, f'sub-{sub}', f'sam-{sam}-sub-{sub}')
        new_directory = os.path.join(base_directory, directory)

        if not os.path.exists(new_directory):
            shutil.copytree(directory, new_directory)
        else:
            already_copied_directories.append(directory)

        copied_mph_files.extend(
            [
                os.path.join(new_directory, file)
                for file in os.listdir(new_directory)
                if file.endswith(comsol_file_ending)
            ]
        )
    if len(already_copied_directories) > 0:
        print('DIRECTORIES ALREADY COPIED OVER:')
        print('\t' + '\n\t'.join(already_copied_directories))


def make_folders_for_copy(data_destination, files_to_copy, samples_sub_sam):  # noqa: D103
    # <data_export_index>, which matches export config
    #   "files" (for SPARC)
    #       "primary" (for SPARC)
    #           <sub-#> (for SPARC)
    #               <sam-#> (for SPARC)
    #                   "samples" (from ASCENT)
    #                       <sample_index> (from ASCENT)
    #                           ... rest is same as ASCENT
    #                           i.e., at this level is:
    #                           "sample.json", "sample.obj", "s.tif", "plots/", "slides/", "models/"
    #                               i.e., at this level in "models/" is:
    #                               <model_index>
    #                                   i.e., at this level in "models"/<model_index>/ is:
    #                                   "model.json", "debug_geom.mph", "bases/", "mesh/", "sims/"
    #                                       i.e., at this level in "sims/" is:
    #                                       <sim_index>
    #                                       ... ETC
    file_directories_to_copy = [os.path.join(*file.split(os.sep)[:-1]) for file in files_to_copy]
    file_directories_to_copy = list(set(file_directories_to_copy))
    for directory in file_directories_to_copy:
        sample = int(directory.split(os.sep)[1])
        sub = samples_sub_sam[sample]['sub']
        sam = samples_sub_sam[sample]['sam']
        base_directory = os.path.join(data_destination, f'sub-{sub}', f'sam-{sam}-sub-{sub}')
        potential_new_directory = os.path.join(base_directory, directory)
        os.makedirs(potential_new_directory, exist_ok=True)


def remove_duplicates(directories_to_copy, files_to_copy, modified_files_to_copy):  # noqa: D103
    files_to_copy = list(set(files_to_copy))
    modified_files_to_copy = list(set(modified_files_to_copy))
    directories_to_copy = list(set(directories_to_copy))
    return directories_to_copy, files_to_copy, modified_files_to_copy


def regex_copy_list(file_lists_to_copy, files_to_copy, regex_legend):  # noqa: D103
    for file_list in file_lists_to_copy:
        list_type = file_list.split(os.sep)[-1]
        list_directory = os.path.join(*file_list.split(os.sep)[:-1])
        regex = regex_legend[list_type]

        for filename in [x for x in os.listdir(list_directory) if re.match(regex, x)]:
            files_to_copy.append(os.path.join(list_directory, filename))


def check_empty(directories_to_copy):  # noqa: D103
    empty_directories = [directory for directory in directories_to_copy if len(os.listdir(directory)) == 0]
    if len(empty_directories) > 0:
        for directory in empty_directories:
            print(f'EMPTY DIRECTORY TO COPY: {directory}')
        reply = (
            input(
                'Empty directories specified for copying. See preceding print statement(s) for details.'
                'Would you like to proceed? [y/N] '
            )
            .lower()
            .strip()
        )
        if reply[0] != 'y':
            print('Exiting program.\n')
            sys.exit()
        else:
            print('Continuing...')


def list_things_to_copy(  # noqa: D103
    code_destination,
    dataset_index,
    keeps_config_directory,
    master_indices,
    samples_sub_sam,
    tmp_files_dataset_destination,
):
    keeps_path = os.path.join(keeps_config_directory, f'{dataset_index}.json')
    keeps = load(keeps_path)
    sample_directory = os.path.join('samples', '<sample_index>')
    stuff_to_copy = paths_from_keeps(sample_directory, keeps)
    directories_to_copy = []
    files_to_copy = []
    file_lists_to_copy = []
    modified_files_to_copy = []
    sims_to_copy = []
    mock_samples_copied = []
    not_mock_samples = []
    input_path = 'input'
    destination_ascent_config_directory = os.path.join(code_destination, 'ascent_configs')
    destination_mock_config_input_directory = os.path.join(destination_ascent_config_directory, 'mock_samples')
    for sample, model, sim, n_sim, _, _ in master_indices:
        # copy MockSample configs
        if sample not in not_mock_samples + mock_samples_copied:
            sample_config_path = os.path.join('samples', str(sample), 'sample.json')
            sample_config = load(sample_config_path)
            sample_name = sample_config['sample']
            source_mock_config_input_path = os.path.join(input_path, sample_name, 'mock.json')
            sub = samples_sub_sam[sample]['sub']
            sam = samples_sub_sam[sample]['sam']
            destination_mock_config_input_path = os.path.join(
                destination_mock_config_input_directory, f'sub{sub}_sam{sam}_Sample{sample}.json'
            )

            if os.path.exists(source_mock_config_input_path):
                mock_samples_copied.append(sample)
                os.makedirs(destination_mock_config_input_directory, exist_ok=True)
                shutil.copy(source_mock_config_input_path, destination_mock_config_input_path)
            else:
                not_mock_samples.append(sample)

        # make list of the rest of things to copy, copy later all at once
        for thing_to_copy in stuff_to_copy:
            # copy Sim configs if including things at the Sim level
            if sim not in sims_to_copy and "<sim_index>" in thing_to_copy:
                sims_to_copy.append(sim)

            # tidy files that need tidying
            is_n_sim_index_json = '<n_sim_index>.json' in thing_to_copy

            # replace placeholders in thing_to_copy
            thing_to_copy = replace_placeholders(thing_to_copy, sample, model, sim, n_sim)

            # if tidy_weights is true, tidy the file
            if is_n_sim_index_json:
                model_config_path = os.path.join('samples', str(sample), 'models', str(model), 'model.json')
                # saves the modified file to a temporary location
                modified_thing_to_copy = tidy_n_sim_index_json(
                    thing_to_copy, model_config_path, tmp_files_dataset_destination
                )
                modified_files_to_copy.append(modified_thing_to_copy)
            else:
                # determine if file or directory, append to lists
                if os.path.isfile(thing_to_copy):
                    files_to_copy.append(thing_to_copy)
                elif os.path.isdir(thing_to_copy):
                    directories_to_copy.append(thing_to_copy)
                else:
                    # check that <> is in the path
                    if not all(character in thing_to_copy for character in ['<', '>']):
                        if thing_to_copy.split(os.sep)[-1] == 's.tif':
                            # check that "scale" -> "scale_ratio" is in Sample config
                            sample_config_path = os.path.join('samples', str(sample), 'sample.json')
                            sample_config = load(sample_config_path)
                            if 'scale_ratio' not in sample_config['scale']:
                                raise ValueError(
                                    f'"scale" -> "scale_ratio" not in '
                                    f'\nSample config: {sample_config_path} '
                                    f'\nand "s.tif" not found'
                                )
                        else:
                            print(f'Not sure what this thing_to_copy is, could be missing: {thing_to_copy}')
                        continue
                    file_lists_to_copy.append(thing_to_copy)
    return (
        destination_ascent_config_directory,
        directories_to_copy,
        file_lists_to_copy,
        files_to_copy,
        modified_files_to_copy,
        sims_to_copy,
    )


def compile_indices(ascent_indices, samples_sub_sam):  # noqa: D103
    master_indices = []
    for inds in ascent_indices:
        sample, model, sim, n_sim = tuple([int(x) for x in inds.split('_')])
        master_indices.append(
            (sample, model, sim, n_sim, samples_sub_sam[sample]['sub'], samples_sub_sam[sample]['sam'])
        )
    return master_indices


def assign_non_picky(ascent_indices, samples_sub_sam, sparc_subs):  # noqa: D103
    sub_auto = 0
    # make set comprehension of previous line
    subs_set = []
    for x in sparc_subs:
        if ~np.isnan(x):
            subs_set.append(x)
    subs_set = list(set(subs_set))
    for inds, sub in zip(ascent_indices, sparc_subs):
        sample, model, sim, n_sim = tuple([int(x) for x in inds.split('_')])

        if sample not in samples_sub_sam:
            while True:
                if np.isnan(sub) and sub_auto not in subs_set:
                    samples_sub_sam[sample] = {}
                    samples_sub_sam[sample]['sub'] = sub_auto
                    samples_sub_sam[sample]['sam'] = 0
                    sub_auto += 1
                    break
                sub_auto += 1
        else:
            if 'sam' not in samples_sub_sam[sample]:
                samples_sub_sam[sample]['sam'] = 0
            else:
                continue


def assign_picky(ascent_indices, sparc_sams, sparc_subs):  # noqa: D103
    samples_sub_sam = {}
    for inds, sub, sam in zip(ascent_indices, sparc_subs, sparc_sams):
        sample, _, _, _ = tuple([int(x) for x in inds.split('_')])

        if sample not in samples_sub_sam:
            if not np.isnan(sub):
                samples_sub_sam[sample] = {}
                samples_sub_sam[sample]['sub'] = sub
                if not np.isnan(sam):
                    samples_sub_sam[sample]['sam'] = sam
            else:
                continue
        else:
            prev_sub = samples_sub_sam[sample]['sub']
            prev_sam = samples_sub_sam[sample].get('sam', np.nan)
            if np.isnan(sub) and np.isnan(sam):
                continue
            if sub != prev_sub:
                raise ValueError(
                    'Manual input of SPARC-subs is not consistent.'
                    f'\n\tASCENT Sample {sample} was assigned to both SPARC subs {sub} and {prev_sub}'
                )
            if sam != prev_sam:
                raise ValueError(
                    'Manual input of SPARC-sams is not consistent.'
                    f'\n\tASCENT Sample {sample} was assigned to both SPARC sams {sam} and {prev_sam}'
                )

    return samples_sub_sam


def process_indices(df):  # noqa D103
    ascent_indices = []
    sparc_subs = []
    sparc_sams = []
    for sheet in df:
        new_indices = df[sheet].loc[:, 'Indices'].tolist()
        ascent_indices.extend(new_indices)

        if 'sub' in df[sheet].columns:
            new_subs = [int(x) if not np.isnan(x) else np.nan for x in df[sheet].loc[:, 'sub'].tolist()]
            sparc_subs.extend(new_subs)
        else:
            new_subs = np.full([1, len(new_indices)], np.nan).tolist()[0]
            sparc_subs.extend(new_subs)

        if 'sam' in df[sheet].columns:
            new_sams = [int(x) if not np.isnan(x) else np.nan for x in df[sheet].loc[:, 'sam'].tolist()]
            sparc_sams.extend(new_sams)
        else:
            new_sams = np.full([1, len(new_indices)], np.nan).tolist()[0]
            sparc_sams.extend(new_sams)
    return ascent_indices, sparc_sams, sparc_subs


def freeze_pip_requirements(metadata_destination):  # noqa D103
    pip_requirements_path = os.path.join(metadata_destination, 'pip_requirements.txt')
    with open(pip_requirements_path, 'w') as f:
        subprocess.run(['pip', 'freeze'], stdout=f)
    if shutil.which('conda'):
        # -conda
        conda_requirements_path = os.path.join(metadata_destination, 'conda_requirements.txt')
        try:
            with open(conda_requirements_path, 'w') as f:
                subprocess.run(['conda', 'list'], stdout=f)
        except FileNotFoundError:
            warnings.warn("Issue with conda list export, skipping", stacklevel=2)
    else:
        warnings.warn('conda not found in path, skipping conda list export', stacklevel=2)


def make_dataset_directories(dataset_index, dataset_index_directory, tmp_files_directory):  # noqa D103
    files_directory = os.path.join(dataset_index_directory, 'files')
    data_destination = os.path.join(files_directory, 'primary')
    code_destination = os.path.join(files_directory, 'code')
    metadata_destination = os.path.join(code_destination, 'ascent_metadata')
    tmp_files_dataset_destination = os.path.join(tmp_files_directory, str(dataset_index))
    for path in [data_destination, code_destination, metadata_destination, tmp_files_dataset_destination]:
        os.makedirs(path, exist_ok=True)
    return code_destination, data_destination, metadata_destination, tmp_files_dataset_destination


def check_existing_dataset(args, dataset_index, dataset_index_directory):  # noqa D103
    if os.path.exists(dataset_index_directory):
        if not args.force:
            raise ValueError(
                f'Attempting to re-run dataset_index {dataset_index}.\n\t'
                f'Create configs for a new dataset_index and re-run,\n\t'
                f'or pass the -f option to overwrite the existing dataset_index files.'
            )
        try:
            shutil.rmtree(dataset_index_directory)
        except OSError as e:
            raise OSError('Could not delete existing dataset_index directory') from e


def query_excel_output(queried_indices_info_path, queried_indices_path, query_criteria_path):  # noqa D103
    redo_query_indices = False
    queried_indices_path_exists = False
    if os.path.exists(queried_indices_path):
        queried_indices_path_exists = True
        # ask user if they would like to delete it and rerun
        reply = (
            input(
                f'Existing queried_indices_path found: {queried_indices_path}\n'
                f'Would you like to delete it and start over with '
                f'complete Query result? [y/N]: '
            )
            .lower()
            .strip()
        )
        if reply[0] == 'y':
            os.remove(queried_indices_path)
            redo_query_indices = True
    if not queried_indices_path_exists or redo_query_indices:
        criteria = load(query_criteria_path)
        q = Query(criteria).run()

        queried_indices_info = load(queried_indices_info_path)

        q.excel_output(queried_indices_path, **queried_indices_info)

        print(f'Excel file for you to edit saved to: {queried_indices_path}')
        print(
            'Modify this file if you wish to not export all data '
            '(delete rows for items you do not want), then rerun this script.'
        )
        sys.exit()
    else:
        # if using previously edited queried_indices_path
        print(f'FOUND QUERIED_INDICES: {queried_indices_path}\n\tCONTINUING WITH DATASET EXPORT\n')
