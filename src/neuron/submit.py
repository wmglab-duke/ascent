#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import argparse
import json
import multiprocessing
import os
import pickle
import re
import shutil
import subprocess
import sys
import time
import traceback
import warnings

import numpy as np
import pandas as pd


# %%Set up parser and top level args
class listAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        run_path = 'runs'
        jsons = [file for file in os.listdir(run_path) if file.endswith('.json')]
        data = []
        for j in jsons:
            with open(run_path + '/' + j) as f:
                try:
                    rundata = json.load(f)
                except Exception as e:
                    print('WARNING: Could not load {}'.format(j))
                    print(e)
                    continue
                data.append(
                    {
                        'RUN': os.path.splitext(j)[0],
                        'PSEUDONYM': rundata.get('pseudonym'),
                        'SAMPLE': rundata['sample'],
                        'MODELS': rundata['models'],
                        'SIMS': rundata['sims'],
                    }
                )
        df = pd.DataFrame(data)
        df.RUN = df.RUN.astype(int)
        df = df.sort_values('RUN')
        print('Run indices available (defined by user .json files in {}):\n'.format(run_path))
        print(df.to_string(index=False))
        sys.exit()


parser = argparse.ArgumentParser(
    description='ASCENT: Automated Simulations to Characterize Electrical Nerve Thresholds'
)
parser.add_argument(
    'run_indices',
    type=int,
    nargs='*',
    help='Space separated indices to submit NEURON sims for',
)
parser.add_argument('-p', '--partition', help='If submitting on a cluster, overrides slurm_params.json')
parser.add_argument(
    '-n',
    '--num-cpu',
    type=int,
    help='For local submission: set number of CPUs to use, overrides run.json',
)
parser.add_argument(
    '-m',
    '--job-mem',
    type=int,
    help='For cluster submission: set amount of RAM per job (in MB), overrides slurm_params.json',
)
parser.add_argument(
    '-j',
    '--num-jobs',
    type=int,
    help='For cluster submission: set number of jobs per array, overrides slurm_params.json',
)
parser.add_argument(
    '-l',
    '--list-runs',
    action=listAction,
    nargs=0,
    help='List info for available runs.z If supplying this argument, do not pass any run indices',
)
parser.add_argument(
    '-A',
    '--all-runs',
    action='store_true',
    help='Submit all runs in the present export folder. If supplying this argument, do not pass any run indices',
)
parser.add_argument(
    '-s',
    '--skip-summary',
    action='store_true',
    help='Begin submitting fibers without asking for confirmation',
)
parser.add_argument(
    '-S',
    '--slurm-params',
    type=str,
    help='For cluster submission: string for additional slurm parameters (enclose in quotes)',
)
parser.add_argument(
    '-c',
    '--force-recompile',
    action='store_true',
    help='Force submit.py to recompile NEURON files',
)
submit_context_group = parser.add_mutually_exclusive_group()
submit_context_group.add_argument(
    '-L',
    '--local-submit',
    action='store_true',
    help='Set submission context to local, overrides run.json',
)
submit_context_group.add_argument(
    '-C',
    '--cluster-submit',
    action='store_true',
    help='Set submission context to cluster, overrides run.json',
)

parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed submission info')

OS = 'UNIX-LIKE' if any([s in sys.platform for s in ['darwin', 'linux']]) else 'WINDOWS'

# %% Set up utility functions


class WarnOnlyOnce:
    warnings = set()

    @classmethod
    def warn(cls, message):
        # storing int == less memory then storing raw message
        h = hash(message)
        if h not in cls.warnings:
            # do your warning
            print(f"Warning: {message}")
            cls.warnings.add(h)


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r{} |{}| {}% {}'.format(prefix, bar, percent, suffix), end='')
    # Print New Line on Complete
    if iteration == total:
        print()


def load(config_path: str):
    """
    Loads in json data and returns to user, assuming it has already been validated.
    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path, "r") as handle:
        return json.load(handle)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def auto_compile(override: bool = False):
    if (
        (not os.path.exists(os.path.join('MOD_Files', 'x86_64', 'special')) and OS == 'UNIX-LIKE')
        or (not os.path.exists(os.path.join('MOD_Files', 'nrnmech.dll')) and OS == 'WINDOWS')
        or override
    ):
        print('compile')
        os.chdir(os.path.join('MOD_Files'))
        exit_code = subprocess.call(['nrnivmodl'])
        if exit_code != 0:
            sys.exit("Error in compiling of NEURON files. Exiting...")
        os.chdir('..')
        compiled = True
    else:
        print('skipped compile')
        compiled = False
    return compiled


def get_diameter(my_inner_fiber_diam_key, my_inner_ind, my_fiber_ind):
    for item in my_inner_fiber_diam_key:
        if item[0] == my_inner_ind and item[1] == my_fiber_ind:
            my_diameter = item[2]
            break
        else:
            continue
    if isinstance(my_diameter, list) and len(my_diameter) == 1:
        my_diameter = my_diameter[0]

    return my_diameter


def get_deltaz(fiber_model, diameter):
    fiber_z_config = load(os.path.join('config', 'system', 'fiber_z.json'))
    fiber_model_info: dict = fiber_z_config['fiber_type_parameters'][fiber_model]

    if fiber_model_info.get("geom_determination_method") == 0:
        diameters, delta_zs, paranodal_length_2s = (
            fiber_model_info[key] for key in ('diameters', 'delta_zs', 'paranodal_length_2s')
        )
        diameter_index = diameters.index(diameter)
        delta_z = delta_zs[diameter_index]

    elif fiber_model_info.get("geom_determination_method") == 1:
        paranodal_length_2_str, delta_z_str, inter_length_str = (
            fiber_model_info[key] for key in ('paranodal_length_2', 'delta_z', 'inter_length')
        )

        if diameter >= 5.643:
            delta_z = eval(delta_z_str["diameter_greater_or_equal_5.643um"])
        else:
            delta_z = eval(delta_z_str["diameter_less_5.643um"])

    elif fiber_model_info.get("neuron_flag") == 3:  # C Fiber
        delta_z = fiber_model_info["delta_zs"]

    neuron_flag = fiber_model_info.get("neuron_flag")

    return delta_z, neuron_flag


def get_thresh_bounds(args, sim_dir: str, sim_name: str, inner_ind: int):
    top, bottom = None, None

    sample = sim_name.split('_')[0]
    n_sim = sim_name.split('_')[3]

    sim_config = load(os.path.join(sim_dir, sim_name, '{}.json'.format(n_sim)))

    if sim_config['protocol']['mode'] == 'ACTIVATION_THRESHOLD' or sim_config['protocol']['mode'] == 'BLOCK_THRESHOLD':
        if 'scout' in sim_config['protocol']['bounds_search']:
            # load in threshold from scout_sim (example use: run centroid first, then any other xy-mode after)
            scout = sim_config['protocol']['bounds_search']['scout']
            scout_sim_dir = os.path.join('n_sims')
            scout_sim_name = '{}_{}_{}_{}'.format(sample, scout['model'], scout['sim'], n_sim)
            scout_sim_path = os.path.join(scout_sim_dir, scout_sim_name)
            scout_output_path = os.path.abspath(os.path.join(scout_sim_path, 'data', 'outputs'))
            scout_thresh_path = os.path.join(scout_output_path, 'thresh_inner{}_fiber{}.dat'.format(inner_ind, 0))

            if os.path.exists(scout_thresh_path):
                stimamp = np.loadtxt(scout_thresh_path)

                if len(np.atleast_1d(stimamp)) > 1:
                    stimamp = stimamp[-1]

                step = sim_config['protocol']['bounds_search']['step'] / 100
                top = (1 + step) * stimamp
                bottom = (1 - step) * stimamp

                unused_protocol_keys = ['top', 'bottom']

                if any(
                    unused_protocol_key in sim_config['protocol']['bounds_search']
                    for unused_protocol_key in unused_protocol_keys
                ):
                    if args.verbose:
                        warnings.warn(
                            'WARNING: scout_sim is defined in Sim, so not using "top" or "bottom" '
                            'which you also defined \n'
                        )
                    else:
                        WarnOnlyOnce.warn(
                            'WARNING: scout_sim is defined in Sim, so not using "top" or "bottom" '
                            'which you also defined \n'
                        )

            else:
                if args.verbose:
                    warnings.warn(
                        f"No fiber threshold exists for scout sim: "
                        f"inner{inner_ind} fiber0, using standard top and bottom"
                    )
                else:
                    WarnOnlyOnce.warn(
                        "Missing at least one scout threshold, using standard top and bottom. "
                        "Rerun with --verbose flag for specific inner index."
                    )

                top = sim_config['protocol']['bounds_search']['top']
                bottom = sim_config['protocol']['bounds_search']['bottom']

        else:
            top = sim_config['protocol']['bounds_search']['top']
            bottom = sim_config['protocol']['bounds_search']['bottom']

    elif sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
        top, bottom = 0, 0

    return top, bottom


def make_task(
    my_os: str,
    sub_con: str,
    start_p: str,
    sim_p: str,
    inner: int,
    fiber: int,
    top: float,
    bottom: float,
    diam: float,
    deltaz: float,
    axonnodes: int,
):
    with open(start_p, 'w+') as handle:
        if my_os == 'UNIX-LIKE':
            lines = [
                '#!/bin/bash\n',
                'cd \"{}\"\n'.format(sim_p),
                'chmod a+rwx special\n',
                './special -nobanner '
                '-c \"strdef sim_path\" '
                '-c \"sim_path=\\\"{}\\\"\" '
                '-c \"inner_ind={}\" '
                '-c \"fiber_ind={}\" '
                '-c \"stimamp_top={}\" '
                '-c \"stimamp_bottom={}\" '
                '-c \"fiberD={:.1f}\" '
                '-c \"deltaz={:.4f}\" '
                '-c \"axonnodes={}\" '
                '-c \"saveflag_end_ap_times=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"saveflag_runtime=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'.format(
                    sim_p, inner, fiber, top, bottom, diam, deltaz, axonnodes
                ),
            ]

            if sub_con != 'cluster':
                lines.remove('cd \"{}\"\n'.format(sim_p))

            # copy special files ahead of time to avoid 'text file busy error'
            if not os.path.exists('special'):
                shutil.copy(os.path.join('MOD_Files', 'x86_64', 'special'), sim_p)

        else:  # OS is 'WINDOWS'
            sim_path_win = os.path.join(*sim_p.split(os.pathsep)).replace('\\', '\\\\')
            lines = [
                'nrniv -nobanner '
                '-dll \"{}/MOD_Files/nrnmech.dll\" '
                '-c \"strdef sim_path\" '
                '-c \"sim_path=\\\"{}\"\" '
                '-c \"inner_ind={}\" '
                '-c \"fiber_ind={}\" '
                '-c \"stimamp_top={}\" '
                '-c \"stimamp_bottom={}\" '
                '-c \"fiberD={}\" '
                '-c \"deltaz={:.4f}\" '
                '-c \"axonnodes={}\" '
                '-c \"saveflag_end_ap_times=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"saveflag_runtime=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"saveflag_ap_loctime=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'.format(
                    os.getcwd(),
                    sim_path_win,
                    inner,
                    fiber,
                    top,
                    bottom,
                    diam,
                    deltaz,
                    axonnodes,
                )
            ]

        handle.writelines(lines)
        handle.close()


def local_submit(my_local_args: dict):
    """
    Method is used to submit jobs locally, has historically been NEURON jobs
    :param my_local_args:
    :return:
    """
    sim_path = my_local_args['sim_path']
    os.chdir(sim_path)

    start = my_local_args['start']
    out_filename = my_local_args['output_log']
    err_filename = my_local_args['error_log']

    with open(out_filename, "w+") as fo, open(err_filename, "w+") as fe:
        subprocess.run(['bash', start] if OS == 'UNIX-LIKE' else [start], stdout=fo, stderr=fe)


def cluster_submit(run_number: int, partition: str, args, mem: int = 2000, array_length_max: int = 10):
    # configuration is not empty
    assert array_length_max > 0, 'SLURM Job Array length is not > 0: array_length_max={}'.format(array_length_max)

    # build configuration filename
    filename: str = os.path.join('runs', run_number + '.json')

    # load in configuration data
    run: dict = load(filename)

    # assign appropriate configuration data
    samples = [run.get('sample', [])]
    models = run.get('models', [])
    sims = run.get('sims', [])

    job_count = 1
    data = [[], [], []]
    current_iteration = 0

    for sample in samples:
        # loop models, sims
        for model in models:
            for sim in sims:
                sim_dir = os.path.join('n_sims')
                sim_name_base = '{}_{}_{}_'.format(sample, model, sim)
                nsim_list = [x for x in os.listdir(sim_dir) if x.startswith(sim_name_base)]
                for sim_name in nsim_list:
                    current_iteration += 1
                    if args.verbose:
                        print('\n\n################ {} ################\n\n'.format(sim_name))
                    else:
                        # print progress bar
                        total_iterations = len(samples) * len(models) * len(sims) * len(nsim_list)
                        printProgressBar(
                            current_iteration,
                            total_iterations,
                            length=40,
                            prefix='Run {}:'.format(run_number),
                        )

                    sim_path = os.path.join(sim_dir, sim_name)
                    fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                    output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))
                    start_dir = os.path.join(sim_path, 'start_scripts')
                    start_path_base = os.path.join(start_dir, 'start_')

                    n_sim = sim_name.split('_')[3]
                    sim_config = load(os.path.join(sim_dir, sim_name, '{}.json'.format(n_sim)))

                    fiber_model = sim_config['fibers']['mode']

                    # ensure log directories exist
                    out_dir = os.path.join(sim_path, 'logs', 'out', '')
                    err_dir = os.path.join(sim_path, 'logs', 'err', '')
                    for cur_dir in [
                        fibers_path,
                        output_path,
                        out_dir,
                        err_dir,
                        start_dir,
                    ]:
                        ensure_dir(cur_dir)

                    # ensure blank.hoc exists
                    blank_path = os.path.join(sim_path, 'blank.hoc')
                    if not os.path.exists(blank_path):
                        open(blank_path, 'w').close()

                    fibers_files = [x for x in os.listdir(fibers_path) if re.match('inner[0-9]+_fiber[0-9]+\\.dat', x)]
                    max_fibers_files_ind = len(fibers_files) - 1

                    start_paths_list = []
                    sim_array_batch = 1
                    inner_index_tally = []
                    fiber_index_tally = []
                    missing_total = 0

                    inner_fiber_diam_key_file = os.path.join(fibers_path, 'inner_fiber_diam_key.obj')
                    inner_fiber_diam_key = None
                    if os.path.exists(inner_fiber_diam_key_file):
                        with open(inner_fiber_diam_key_file, 'rb') as f:
                            inner_fiber_diam_key = pickle.load(f)
                        f.close()
                    else:
                        diameter = sim_config['fibers']['z_parameters']['diameter']

                    for fiber_filename in fibers_files:
                        master_fiber_name = str(fiber_filename.split('.')[0])
                        inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                        inner_ind = int(inner_name.split('inner')[-1])
                        fiber_ind = int(fiber_name.split('fiber')[-1])

                        if sim_config['protocol']:
                            pass

                        if sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
                            n_amp = len(sim_config['protocol']['amplitudes'])
                            search_path = os.path.join(
                                output_path,
                                'activation_inner{}_fiber{}_amp{}.dat'.format(inner_ind, fiber_ind, n_amp - 1),
                            )
                        else:
                            search_path = os.path.join(
                                output_path,
                                f"thresh_inner{inner_ind}_fiber{fiber_ind}.dat",
                            )

                        if os.path.exists(search_path):
                            continue
                        else:
                            missing_total += 1
                            inner_ind_solo = inner_ind
                            fiber_ind_solo = fiber_ind
                            master_fiber_name_solo = master_fiber_name

                    if missing_total == 0:
                        continue

                    elif missing_total == 1:
                        stimamp_top, stimamp_bottom = get_thresh_bounds(args, sim_dir, sim_name, inner_ind_solo)
                        start_path_solo = os.path.join(
                            sim_path,
                            'start{}'.format('.sh' if OS == 'UNIX-LIKE' else '.bat'),
                        )

                        if inner_fiber_diam_key is not None:
                            diameter = get_diameter(inner_fiber_diam_key, inner_ind, fiber_ind)

                        deltaz, neuron_flag = get_deltaz(fiber_model, diameter)

                        if stimamp_top is not None and stimamp_bottom is not None:

                            # get the axonnodes from data/inputs/inner{}_fiber{}.dat top line
                            fiber_ve_path = os.path.join(
                                fibers_path,
                                'inner{}_fiber{}.dat'.format(inner_ind_solo, fiber_ind_solo),
                            )
                            fiber_ve = np.loadtxt(fiber_ve_path)
                            n_fiber_coords = int(fiber_ve[0])

                            if neuron_flag == 2:
                                axonnodes = int(1 + (n_fiber_coords - 1) / 11)
                            elif neuron_flag == 3:
                                axonnodes = int(n_fiber_coords)

                            make_task(
                                OS,
                                'cluster',
                                start_path_solo,
                                sim_path,
                                inner_ind_solo,
                                fiber_ind_solo,
                                stimamp_top,
                                stimamp_bottom,
                                diameter,
                                deltaz,
                                axonnodes,
                            )

                            # submit batch job for fiber
                            job_name = '{}_{}'.format(sim_name, master_fiber_name_solo)
                            output_log = os.path.join(out_dir, '{}{}'.format(master_fiber_name_solo, '.log'))
                            error_log = os.path.join(err_dir, '{}{}'.format(master_fiber_name_solo, '.log'))

                            if args.verbose:
                                print('========= SUBMITTING SOLO: {} ==========='.format(job_name))

                            command = [
                                'sbatch{}'.format(' ' + args.slurm_params if args.slurm_params is not None else ''),
                                '--job-name={}'.format(job_name),
                                '--output={}'.format(output_log),
                                '--error={}'.format(error_log),
                                '--mem={}'.format(mem),
                                '-p',
                                partition,
                                '-c',
                                '1',
                                start_path_solo,
                            ]
                            if not args.verbose:
                                with open(os.devnull, 'wb') as devnull:
                                    comp = subprocess.run(command, stdout=devnull)
                            else:
                                comp = subprocess.run(command)
                            if comp.returncode != 0:
                                sys.exit('Non-zero exit code during job submission. Exiting.')

                            # allow job to start before removing slurm file
                            time.sleep(1.0)
                        else:
                            sys.exit('Top and bottom bounds not defined for threshold search. Exiting.')

                    else:
                        if args.verbose:
                            print('================= ARRAY SUBMITTING ====================')
                        array_index = 0
                        for fiber_file_ind, fiber_filename in enumerate(fibers_files):
                            master_fiber_name = str(fiber_filename.split('.')[0])
                            inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                            inner_ind = int(inner_name.split('inner')[-1])
                            fiber_ind = int(fiber_name.split('fiber')[-1])

                            if sim_config['protocol']:
                                pass

                            if sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
                                n_amp = len(sim_config['protocol']['amplitudes'])
                                search_path = os.path.join(
                                    output_path,
                                    'activation_inner{}_fiber{}_amp{}.dat'.format(inner_ind, fiber_ind, n_amp - 1),
                                )
                            else:
                                search_path = os.path.join(
                                    output_path,
                                    f"thresh_inner{inner_ind}_fiber{fiber_ind}.dat",
                                )

                            if not os.path.exists(search_path):
                                if args.verbose:
                                    print(f"RUNNING inner ({inner_ind}) fiber ({fiber_ind})  -->  {search_path}")

                                if inner_fiber_diam_key is not None:
                                    diameter = get_diameter(inner_fiber_diam_key, inner_ind, fiber_ind)
                                deltaz, neuron_flag = get_deltaz(fiber_model, diameter)

                                # get the axonnodes from data/inputs/inner{}_fiber{}.dat top line
                                fiber_ve_path = os.path.join(
                                    fibers_path,
                                    'inner{}_fiber{}.dat'.format(inner_ind, fiber_ind),
                                )
                                fiber_ve = np.loadtxt(fiber_ve_path)
                                n_fiber_coords = int(fiber_ve[0])

                                if neuron_flag == 2:
                                    axonnodes = int(1 + (n_fiber_coords - 1) / 11)
                                elif neuron_flag == 3:
                                    axonnodes = int(n_fiber_coords)

                                start_path = '{}{}{}'.format(
                                    start_path_base,
                                    job_count,
                                    '.sh' if OS == 'UNIX-LIKE' else '.bat',
                                )
                                start_paths_list.append(start_path)

                                inner_index_tally.append(inner_ind)
                                fiber_index_tally.append(fiber_ind)

                                stimamp_top, stimamp_bottom = get_thresh_bounds(args, sim_dir, sim_name, inner_ind)
                                if stimamp_top is not None and stimamp_bottom is not None:
                                    make_task(
                                        OS,
                                        'cluster',
                                        start_path,
                                        sim_path,
                                        inner_ind,
                                        fiber_ind,
                                        stimamp_top,
                                        stimamp_bottom,
                                        diameter,
                                        deltaz,
                                        axonnodes,
                                    )
                                    array_index += 1
                                    job_count += 1

                            if array_index == array_length_max or fiber_file_ind == max_fibers_files_ind:
                                # output key, since we lose this in array method
                                start = job_count - len(start_paths_list)

                                key_file = os.path.join(sim_path, 'out_err_key.txt')

                                data[0].append(
                                    [x for x in range(start, job_count)]
                                )  # note: last value is job_count - 1
                                data[1].append(inner_index_tally)
                                data[2].append(fiber_index_tally)

                                key_arr = np.transpose(
                                    np.array(
                                        [
                                            [x for xs in data[0] for x in xs],
                                            [y for ys in data[1] for y in ys],
                                            [z for zs in data[2] for z in zs],
                                        ]
                                    )
                                )

                                if fiber_file_ind == max_fibers_files_ind:
                                    with open(key_file, "ab") as f:
                                        np.savetxt(
                                            f,
                                            key_arr,
                                            fmt='%d',
                                            header='job_n, inner, fiber',
                                            comments='',
                                            delimiter=", ",
                                        )

                                    data = [[], [], []]

                                # submit batch job for fiber
                                job_name = f"{sim_name}_{sim_array_batch}"

                                command = [
                                    'sbatch{}'.format(' ' + args.slurm_params if args.slurm_params is not None else ''),
                                    '--job-name={}'.format(job_name),
                                    '--output={}%a.log'.format(out_dir),
                                    '--error={}%a.log'.format(err_dir),
                                    '--array={}-{}'.format(start, job_count - 1),
                                    '--mem={}'.format(mem),
                                    '--partition={}'.format(partition),
                                    '--cpus-per-task=1',
                                    'array_launch.slurm',
                                    start_path_base,
                                ]

                                if not args.verbose:
                                    with open(os.devnull, 'wb') as devnull:
                                        exit_code = subprocess.check_call(command, stdout=devnull)
                                else:
                                    exit_code = subprocess.check_call(command)
                                if exit_code != 0:
                                    sys.exit('Non-zero exit code during job array submission. Exiting.')

                                # allow job to start before removing slurm file
                                time.sleep(1.0)

                                array_index = 0
                                sim_array_batch += 1
                                start_paths_list = []
                                inner_index_tally = []
                                fiber_index_tally = []


def make_local_submission_list(run_number: int, args, summary_gen=False):
    # build configuration filename
    filename = os.path.join('runs', run_number + '.json')

    # create empty list of args (for local submission with parallelization) for each Run
    local_args_list = []

    # load in configuration data
    run = load(filename)

    # keys required for each local submission
    local_run_keys = ['start', 'output_log', 'error_log', 'sim_path']

    # assign appropriate configuration data
    samples = [run.get('sample', [])]
    models = run.get('models', [])
    sims = run.get('sims', [])

    for sample in samples:
        # loop models, sims
        for model in models:
            for sim in sims:
                sim_dir = os.path.join('n_sims')
                sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

                for sim_name in [x for x in os.listdir(sim_dir) if x.startswith(sim_name_base)]:
                    if not summary_gen and args.verbose:
                        print('\n\n################ {} ################\n\n'.format(sim_name))

                    sim_path = os.path.join(sim_dir, sim_name)
                    fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                    output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))
                    start_dir = os.path.join(sim_path, "start_scripts")

                    out_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'out'))
                    err_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'err'))

                    # ensure necessary directories exist
                    for cur_dir in [
                        fibers_path,
                        output_path,
                        out_dir,
                        err_dir,
                        start_dir,
                    ]:
                        ensure_dir(cur_dir)

                    # ensure blank.hoc exists
                    blank_path = os.path.join(sim_path, 'blank.hoc')
                    if not os.path.exists(blank_path):
                        open(blank_path, 'w').close()

                    # load JSON file with binary search amplitudes
                    n_sim = sim_name.split('_')[-1]
                    sim_config = load(os.path.join(sim_path, '{}.json'.format(n_sim)))
                    fiber_model = sim_config['fibers']['mode']

                    # load the inner x fiber -> diam key saved in the n_sim folder
                    inner_fiber_diam_key_file = os.path.join(fibers_path, 'inner_fiber_diam_key.obj')
                    inner_fiber_diam_key = None
                    if os.path.exists(inner_fiber_diam_key_file):
                        with open(inner_fiber_diam_key_file, 'rb') as f:
                            inner_fiber_diam_key = pickle.load(f)
                        f.close()
                    else:
                        diameter = sim_config['fibers']['z_parameters']['diameter']

                    for fiber_filename in [
                        x for x in os.listdir(fibers_path) if re.match('inner[0-9]+_fiber[' '0-9]+\\.dat', x)
                    ]:
                        master_fiber_name = str(fiber_filename.split('.')[0])
                        inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                        inner_ind = int(inner_name.split('inner')[-1])
                        fiber_ind = int(fiber_name.split('fiber')[-1])
                        if sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
                            n_amp = len(sim_config['protocol']['amplitudes'])
                            activation_path = os.path.join(
                                output_path,
                                'activation_inner{}_fiber{}_amp{}.dat'.format(inner_ind, fiber_ind, n_amp - 1),
                            )
                            if os.path.exists(activation_path):
                                if not summary_gen and args.verbose:
                                    print(
                                        'Found {} -->\t\tskipping inner ({}) fiber ({})'.format(
                                            activation_path, inner_ind, fiber_ind
                                        )
                                    )
                                continue
                        else:
                            thresh_path = os.path.join(
                                output_path,
                                'thresh_inner{}_fiber{}.dat'.format(inner_ind, fiber_ind),
                            )
                            if os.path.exists(thresh_path):
                                if not summary_gen and args.verbose:
                                    print(
                                        'Found {} -->\t\tskipping inner ({}) fiber ({})'.format(
                                            thresh_path, inner_ind, fiber_ind
                                        )
                                    )
                                continue

                        # local
                        start_path = os.path.join(
                            start_dir,
                            '{}_{}_start{}'.format(
                                inner_ind,
                                fiber_ind,
                                '.sh' if OS == 'UNIX-LIKE' else '.bat',
                            ),
                        )
                        stimamp_top, stimamp_bottom = get_thresh_bounds(args, sim_dir, sim_name, inner_ind)
                        if inner_fiber_diam_key is not None:
                            diameter = get_diameter(inner_fiber_diam_key, inner_ind, fiber_ind)
                        deltaz, neuron_flag = get_deltaz(fiber_model, diameter)
                        fiber_ve_path = os.path.join(
                            fibers_path,
                            'inner{}_fiber{}.dat'.format(inner_ind, fiber_ind),
                        )
                        fiber_ve = np.loadtxt(fiber_ve_path)
                        n_fiber_coords = int(fiber_ve[0])

                        if neuron_flag == 2:
                            axonnodes = int(1 + (n_fiber_coords - 1) / 11)
                        elif neuron_flag == 3:
                            axonnodes = int(n_fiber_coords)

                        if not summary_gen:
                            make_task(
                                OS,
                                'local',
                                start_path,
                                sim_path,
                                inner_ind,
                                fiber_ind,
                                stimamp_top,
                                stimamp_bottom,
                                diameter,
                                deltaz,
                                axonnodes,
                            )

                        # submit batch job for fiber
                        output_log = os.path.join(out_dir, '{}{}'.format(master_fiber_name, '.log'))
                        error_log = os.path.join(err_dir, '{}{}'.format(master_fiber_name, '.log'))

                        local_args = dict.fromkeys(local_run_keys, [])
                        local_args['start'] = os.path.join('start_scripts', start_path.split(os.path.sep)[-1])
                        local_args['output_log'] = os.path.join('logs', 'out', output_log.split(os.path.sep)[-1])
                        local_args['error_log'] = os.path.join('logs', 'err', error_log.split(os.path.sep)[-1])
                        local_args['sim_path'] = os.path.abspath(sim_path)
                        local_args_list.append(local_args.copy())

    return local_args_list


def submit_run(sub_context, run_index, args):
    if sub_context == 'local':
        filename = os.path.join('runs', run_index + '.json')
        run = load(filename)

        if args.num_cpu is not None:
            cpus = args.num_cpu

            if cpus > multiprocessing.cpu_count() - 1:
                raise ValueError('num_cpu argument is more than cpu_count-1 CPUs')

            print(f"Submitting Run {run_index} locally to {cpus} CPUs (defined by num_cpu argument)")

        elif 'local_avail_cpus' in run:
            cpus = run.get('local_avail_cpus')

            if cpus > multiprocessing.cpu_count() - 1:
                raise ValueError('local_avail_cpus in Run asking for more than cpu_count-1 CPUs')

            print(f"Submitting Run {run_index} locally to {cpus} CPUs (defined by local_avail_cpus in Run)")

        else:
            cpus = multiprocessing.cpu_count() - 1
            print(f"local_avail_cpus not defined in Run, so proceeding with cpu_count-1={cpus} CPUs")

        submit_list = make_local_submission_list(run_index, args)
        if len(submit_list) == 0:
            return
        with multiprocessing.Pool(cpus) as p:
            # open pool instance, set up progress bar, and iterate over each job
            total_iterations = len(submit_list)
            printProgressBar(0, total_iterations, length=40, prefix='Run {}:'.format(run_index))
            for i, _ in enumerate(p.imap_unordered(local_submit, submit_list, 1)):
                printProgressBar(
                    i,
                    total_iterations,
                    length=40,
                    prefix='Run {}:'.format(run_index),
                )

    elif sub_context == 'cluster':
        # load slurm params
        slurm_params = load(os.path.join('config', 'system', 'slurm_params.json'))

        # assign params for array submission
        partition = slurm_params['partition'] if args.partition is None else args.partition
        njobs = slurm_params['jobs_per_array'] if args.num_jobs is None else args.num_jobs
        mem = slurm_params['memory_per_fiber'] if args.job_mem is None else args.job_mem

        cluster_submit(run_index, partition, args, array_length_max=njobs, mem=mem)
    else:
        sys.exit('Invalid submission context: {}'.format(sub_context))


# %% main
def main():
    # validate inputs
    args = parser.parse_args()

    if args.all_runs is True:
        if len(args.run_indices) > 0:
            sys.exit('Error: Cannot use -A/--run-all argument and pass run indices.')
        args.run_indices = [int(os.path.splitext(file)[0]) for file in os.listdir('runs') if file.endswith('.json')]
    if len(args.run_indices) == 0:
        sys.exit("Error: No run indices to use.")

    run_inds = args.run_indices
    runs = []

    # compile MOD files if they have not yet been compiled
    auto_compile(args.force_recompile)

    summary = []
    rundata = []

    # check for submission context
    if args.cluster_submit:
        submission_context = 'cluster'
    elif args.local_submit:
        submission_context = 'local'
    else:
        submission_context = 'cluster' if shutil.which('sbatch') is not None else 'local'

    for run_number in run_inds:

        run_number = str(run_number)
        # run number is numeric
        assert re.search('[0-9]+', run_number), 'Encountered non-number run number argument: {}'.format(run_number)

        # build configuration filename
        filename = os.path.join('runs', run_number + '.json')
        runs.append(run_number)

        # configuration file exists
        assert os.path.exists(filename), 'Run configuration not found: {}'.format(run_number)

        # load in configuration data
        run = load(filename)

        # configuration is not empty
        assert len(run.items()) > 0, 'Encountered empty run configuration: {}'.format(filename)

        # get list of fibers to run
        if args.skip_summary:
            'Skipping summary generation, submitting fibers...'
        else:
            print('Generating run list for run {}'.format(run_number))
            summary.append(make_local_submission_list(run_number, args, summary_gen=True))
            rundata.append(
                {
                    'RUN': run_number,
                    'SAMPLE': run['sample'],
                    'MODELS': run['models'],
                    'SIMS': run['sims'],
                }
            )
    # check that all submission contexts are the same
    if not args.skip_summary:
        # format run data
        n_fibers = sum([len(x) for x in summary])
        df = pd.DataFrame(rundata)
        df.RUN = df.RUN.astype(int)
        df = df.sort_values('RUN')
        # print out and check that the user is happy
        print('Submitting the following runs (submission_context={}):'.format(submission_context))
        print(df.to_string(index=False))
        print('Will result in running {} fiber simulations'.format(n_fibers))
        if n_fibers == 0:
            sys.exit('Exiting...')
        proceed = input('\t Would you like to proceed?\n' '\t\t 0 = NO\n' '\t\t 1 = YES\n')
        if int(proceed) != 1:
            sys.exit()
        else:
            print('Proceeding...\n')

    for run_index in runs:
        try:
            submit_run(submission_context, run_index, args)
        except Exception:
            traceback.print_exc()
            print(
                f'WARNING: Error during submission of run {run_index}. '
                'See traceback for more information.\n '
                'Proceeding to next run...'
            )


if __name__ == "__main__":  # Allows for the safe importing of the main module
    main()
    print('done')
