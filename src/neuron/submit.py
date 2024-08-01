#!/usr/bin/env python3.7

"""Submits NEURON fiber simulations.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
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
import warnings
from json import JSONDecodeError

import numpy as np
import pandas as pd
from tqdm import tqdm


# %%Set up parser and top level args
class ListAction(argparse.Action):
    """Custom action for argparse to list run info."""

    def __call__(self, parser, values, *args, option_string=None, **kwargs):
        """Print run info and exit. # noqa: DAR101.

        This function is called when the --list option is used and should not be called directly.
        """
        run_path = 'runs'
        jsons = [file for file in os.listdir(run_path) if file.endswith('.json')]
        data = []
        for j in jsons:
            with open(run_path + '/' + j) as f:
                try:
                    rundata = json.load(f)
                except JSONDecodeError as e:
                    print(f'WARNING: Could not load {j}, check for syntax errors. Original error: {e}')
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
        print(f'Run indices available (defined by user .json files in {run_path}):\n')
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
    action=ListAction,
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

OS = 'UNIX-LIKE' if any(s in sys.platform for s in ['darwin', 'linux']) else 'WINDOWS'


# %% Set up utility functions


class WarnOnlyOnce:
    """Warn only once per instance."""

    warnings = set()

    @classmethod
    def warn(cls, message):
        """Print warning message if first call.

        :param message: Warning message to print
        """
        # storing int == less memory then storing raw message
        h = hash(message)
        if h not in cls.warnings:
            # do your warning
            print(f"Warning: {message}")
            cls.warnings.add(h)


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """Print or update a progress bar in the terminal.

    Call in a loop to create a terminal progress bar.
    Information such as the prefix and suffix can be changed with each call.

    :param iteration: The current iteration (current/total)
    :param total: The total number of iterations
    :param prefix: The prefix string to place before the progress bar
    :param suffix: The suffix string to place after the progress bar
    :param decimals: The number of decimals to show on the percentage progress
    :param length: The length of the progress bar
    :param fill: The character to fill the progress bar with
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    # Print New Line on Complete
    if iteration == total:
        print()


def load(config_path: str):
    """Load in json data and returns to user, assuming it has already been validated.

    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path) as handle:
        return json.load(handle)


def ensure_dir(directory):
    """Ensure that a directory exists. If it does not, create it.

    :param directory: the string path to the directory
    """
    os.makedirs(directory, exist_ok=True)


def auto_compile(override: bool = False):
    """Compile NEURON files if they have not been compiled yet.

    :param override: if True, compile regardless of whether the files have already been compiled
    :return: True if ran compilation, False if not
    """
    if (
        (not os.path.exists(os.path.join('MOD_Files', 'x86_64', 'special')) and OS == 'UNIX-LIKE')
        or (not os.path.exists(os.path.join('MOD_Files', 'nrnmech.dll')) and OS == 'WINDOWS')
        or override
    ):
        print('compiling NEURON files...')
        os.chdir(os.path.join('MOD_Files'))
        exit_data = subprocess.run(['nrnivmodl'], shell=True, capture_output=True, text=True)
        # note, nrnivmodl always returns 0, even if it fails
        if (
            exit_data.returncode != 0
            or (not os.path.exists(os.path.join('x86_64', 'special')) and OS == 'UNIX-LIKE')
            or (not os.path.exists(os.path.join('nrnmech.dll')) and OS == 'WINDOWS')
        ):
            print(exit_data.stderr)
            sys.exit("Error in compiling of NEURON files. Exiting...")
        os.chdir('..')
        return True

    print('skipped compile')
    return False


def get_diameter(my_inner_fiber_diam_key, my_inner_ind, my_fiber_ind):
    """Get the diameter of the fiber from the inner fiber diameter key.

    :param my_inner_fiber_diam_key: the key for the fiber diameters
    :param my_inner_ind: the index of the inner
    :param my_fiber_ind: the index of the fiber within the inner
    :return: the diameter for this fiber
    """
    for item in my_inner_fiber_diam_key:
        if item[0] == my_inner_ind and item[1] == my_fiber_ind:
            my_diameter = item[2]
            break

    if isinstance(my_diameter, list) and len(my_diameter) == 1:
        my_diameter = my_diameter[0]

    return my_diameter


def get_deltaz(fiber_model, diameter):
    """Get the deltaz (node spacing) for a given fiber model and diameter.

    :param fiber_model: the string name of the fiber model
    :param diameter: the diameter of the fiber in microns
    :return: the deltaz for this fiber, the neuron flag for the fiber model
    """
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

    elif fiber_model_info.get("geom_determination_method") == 2:  # SMALL_MRG_INTERPOLATION_V1 fiber
        paranodal_length_2_str, delta_z_str, inter_length_str = (
            fiber_model_info[key] for key in ('paranodal_length_2', 'delta_z', 'inter_length')
        )
        delta_z = eval(delta_z_str)

    elif fiber_model_info.get("neuron_flag") == 3:  # C Fiber
        delta_z = fiber_model_info["delta_zs"]

    neuron_flag = fiber_model_info.get("neuron_flag")

    return delta_z, neuron_flag


def get_thresh_bounds(sim_dir: str, sim_name: str, inner_ind: int):
    """Get threshold bounds (upper and lower) for this simulation.

    :param sim_dir: the string path to the simulation directory
    :param sim_name: the string name of the n_sim
    :param inner_ind: the index of the inner this fiber is in
    :return: the upper and lower threshold bounds
    """
    top, bottom = None, None

    sample = sim_name.split('_')[0]
    n_sim = sim_name.split('_')[3]

    sim_config = load(os.path.join(sim_dir, sim_name, f'{n_sim}.json'))

    if sim_config['protocol']['mode'] == 'ACTIVATION_THRESHOLD' or sim_config['protocol']['mode'] == 'BLOCK_THRESHOLD':
        if 'scout' in sim_config['protocol']['bounds_search']:
            # load in threshold from scout_sim (example use: run centroid first, then any other xy-mode after)
            scout = sim_config['protocol']['bounds_search']['scout']
            scout_sim_dir = os.path.join('n_sims')
            scout_sim_name = f"{sample}_{scout['model']}_{scout['sim']}_{n_sim}"
            scout_sim_path = os.path.join(scout_sim_dir, scout_sim_name)
            scout_output_path = os.path.abspath(os.path.join(scout_sim_path, 'data', 'outputs'))
            scout_thresh_path = os.path.join(scout_output_path, f'thresh_inner{inner_ind}_fiber{0}.dat')

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
                            'which you also defined \n',
                            stacklevel=2,
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
                        f"inner{inner_ind} fiber0, using standard top and bottom",
                        stacklevel=2,
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
    sub_con: str,
    my_os: str,
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
    """Create shell script used to run a fiber simulation.

    :param sub_con: the string name of the submission context.
    :param my_os: the string name of the operating system
    :param start_p: the string path to the start_dir
    :param sim_p: the string path to the sim_dir
    :param inner: the index of the inner this fiber is in
    :param fiber: the index of the fiber this simulation is for
    :param top: the upper threshold bound
    :param bottom: the lower threshold bound
    :param diam: the diameter of the fiber
    :param deltaz: the deltaz for the fiber
    :param axonnodes: the number of axon nodes
    """
    with open(start_p, 'w+') as handle:
        if my_os == 'UNIX-LIKE':
            lines = [
                '#!/bin/bash\n',
                f'cd "{sim_p}\"\n',
                'chmod a+rwx special\n',
                './special -nobanner '
                '-c \"strdef sim_path\" '
                f'-c \"sim_path=\\\"{sim_p}\\\"\" '
                f'-c \"inner_ind={inner}\" '
                f'-c \"fiber_ind={fiber}\" '
                f'-c \"stimamp_top={top}\" '
                f'-c \"stimamp_bottom={bottom}\" '
                f'-c \"fiberD={diam:.6f}\" '
                f'-c \"deltaz={deltaz:.4f}\" '
                f'-c \"axonnodes={axonnodes}\" '
                '-c \"saveflag_end_ap_times=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"saveflag_runtime=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n',
            ]
            if sub_con != 'cluster':
                lines.remove(f'cd "{sim_p}\"\n')

            # copy special files ahead of time to avoid 'text file busy error'
            if not os.path.exists('special'):
                shutil.copy(os.path.join('MOD_Files', 'x86_64', 'special'), sim_p)

        else:  # OS is 'WINDOWS'
            sim_path_win = os.path.join(*sim_p.split(os.pathsep)).replace('\\', '\\\\')
            main_path_win = os.getcwd().replace('\\', '/')
            lines = [
                'nrniv -nobanner '
                f'-dll \"{main_path_win}/MOD_Files/nrnmech.dll\" '
                '-c \"strdef sim_path\" '
                f'-c \"sim_path=\\\"{sim_path_win}\"\" '
                f'-c \"inner_ind={inner}\" '
                f'-c \"fiber_ind={fiber}\" '
                f'-c \"stimamp_top={top}\" '
                f'-c \"stimamp_bottom={bottom}\" '
                f'-c \"fiberD={diam:.6f}\" '
                f'-c \"deltaz={deltaz:.4f}\" '
                f'-c \"axonnodes={axonnodes}\" '
                '-c \"saveflag_end_ap_times=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"saveflag_runtime=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"saveflag_ap_loctime=0\" '  # for backwards compatible, overwritten in launch.hoc if 1
                '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'
            ]

        handle.writelines(lines)
        handle.close()


def local_submit(fiber_data: dict):
    """Submit a fiber simulation to the local machine.

    :param fiber_data: the dictionary of fiber data for suvbmission
    """
    a = fiber_data["job_number"]
    out_path = os.path.join('logs', 'out', f'{a}.log')
    err_path = os.path.join('logs', 'err', f'{a}.log')
    start = os.path.join('start_scripts', f'start_{a}')
    with open(out_path, "w+") as fo, open(err_path, "w+") as fe:
        subprocess.run(['bash', start + '.sh'] if OS == 'UNIX-LIKE' else [start + '.bat'], stdout=fo, stderr=fe)

    # print fiber completion
    if fiber_data['verbose']:
        print(f'Completed NEURON simulation for inner {fiber_data["inner"]} fiber {fiber_data["fiber"]}.')


def submit_fibers(submission_context, submission_data):
    """Submit fiber simulations, either locally or to a cluster.

    :param submission_context: the string name of the submission_context
    :param submission_data: the dictionary of data for fiber submission
    :raises ValueError: IF the specified cpu count is higher than the number of cores on the machine
    """
    # configuration is not empty
    ran_fibers = 0
    sim_dir = os.path.join('n_sims')
    n_fibers = sum(len(v) for v in submission_data.values())

    progress_bar = tqdm(total=n_fibers, dynamic_ncols=True, disable=args.verbose, desc='Fibers submitted')

    for sim_name, runfibers in submission_data.items():
        if args.verbose:
            print(f'\n\n################ {sim_name} ################\n\n')
        # skip if no fibers to run for this nsim
        if len(runfibers) == 0:
            continue
        sim_path = os.path.join(sim_dir, sim_name)
        start_dir = os.path.join(sim_path, 'start_scripts')
        start_path_base = os.path.join(start_dir, 'start_')

        if submission_context == 'cluster':
            cluster_submit(runfibers, sim_name, sim_path, start_path_base)
            ran_fibers += len(runfibers)
            progress_bar.update(len(runfibers))
        else:
            if args.num_cpu is not None:
                cpus = args.num_cpu

                if cpus > multiprocessing.cpu_count() - 1:
                    raise ValueError('num_cpu argument is more than cpu_count-1 CPUs')

                print(f"Submitting locally to {cpus} CPUs")

            else:
                cpus = int(multiprocessing.cpu_count() / 2)
                warnings.warn(
                    f"You did not define number of cores to use (-n), so proceeding with int(cpu_core_count/2)={cpus}",
                    stacklevel=2,
                )
            os.chdir(sim_path)
            with multiprocessing.Pool(cpus) as p:
                for x in runfibers:
                    x['verbose'] = args.verbose
                # open pool instance, set up progress bar, and iterate over each job
                for _ in p.imap_unordered(local_submit, runfibers, 1):
                    progress_bar.update(1)
            os.chdir("../..")


def cluster_submit(runfibers, sim_name, sim_path, start_path_base):
    """Submit fiber simulations on a slurm-based high performance computing cluster.

    :param runfibers: the list of fiber data for submission
    :param sim_name: the string name of the n_sim
    :param sim_path: the string path to the simulation
    :param start_path_base: the string prefix for all start scripts
    """
    slurm_params = load(os.path.join('config', 'system', 'slurm_params.json'))
    out_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'out', '%a.log'))
    err_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'err', '%a.log'))
    # assign params for array submission
    partition = slurm_params['partition'] if args.partition is None else args.partition
    njobs = slurm_params['jobs_per_array'] if args.num_jobs is None else args.num_jobs
    mem = slurm_params['memory_per_fiber'] if args.job_mem is None else args.job_mem
    array_fibertasks = [runfibers[x : x + njobs] for x in range(0, len(runfibers), njobs)]
    for tasklist in array_fibertasks:
        array_indices = [task['job_number'] for task in tasklist]

        # print fiber submission
        if args.verbose:
            for task in tasklist:
                print(f"RUNNING inner ({task['inner']}) fiber ({task['fiber']})")
                time.sleep(1)

        # submit batch job for fiber

        command = [
            'sbatch',
            *([args.slurm_params] if args.slurm_params else []),
            f'--job-name={sim_name}',
            f'--output={out_dir}',
            f'--error={err_dir}',
            f"--array={','.join([str(x) for x in array_indices])}",
            f'--mem={mem}',
            f'--partition={partition}',
            '--cpus-per-task=1',
            'array_launch.slurm',
            start_path_base,
        ]

        if not args.verbose:
            exit_data = subprocess.run(command, capture_output=True, text=True)
        else:
            exit_data = subprocess.run(command, capture_output=True, text=True)
            print(exit_data.stdout)
        if exit_data.returncode != 0:
            print(exit_data.stderr)
            sys.exit('Non-zero exit code during job array submission. Exiting.')

        # allow job to start before removing slurm file
        time.sleep(1.0)


def make_fiber_tasks(submission_list, submission_context):
    """Create all shell scripts for fiber submission tasks.

    :param submission_list: the list of fibers to be submitted
    :param submission_context: the string name of the submission_context
    """
    # assign appropriate configuration data
    sim_dir = os.path.join('n_sims')
    for sim_name, runfibers in submission_list.items():
        sim_path = os.path.join(sim_dir, sim_name)
        fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
        output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))
        start_dir = os.path.join(sim_path, 'start_scripts')
        start_path_base = os.path.join(start_dir, 'start_')

        # ensure log directories exist
        out_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'out', ''))
        err_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'err', ''))
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
            with open(blank_path, 'w'):
                pass

        # load JSON file with bisection search amplitudes
        n_sim = sim_name.split('_')[-1]
        sim_config = load(os.path.join(sim_path, f'{n_sim}.json'))
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

        for fiber_data in runfibers:
            cuff_type, inner_ind, fiber_ind = fiber_data['cuff_type'], fiber_data['inner'], fiber_data['fiber']

            if inner_fiber_diam_key is not None:
                diameter = get_diameter(inner_fiber_diam_key, inner_ind, fiber_ind)
            deltaz, neuron_flag = get_deltaz(fiber_model, diameter)

            # get the axonnodes from data/inputs/inner{}_fiber{}.dat top line
            if cuff_type:
                fiber_ve_path = os.path.join(
                    fibers_path,
                    f'{cuff_type[0]}_inner{inner_ind}_fiber{fiber_ind}.dat',
                )
            else:  # Backwards compatibility
                fiber_ve_path = os.path.join(
                    fibers_path,
                    f'inner{inner_ind}_fiber{fiber_ind}.dat',
                )

            fiber_ve = np.loadtxt(fiber_ve_path)
            n_fiber_coords = int(fiber_ve[0])

            if neuron_flag == 2:
                axonnodes = int(1 + (n_fiber_coords - 1) / 11)
            elif neuron_flag == 3:
                axonnodes = int(n_fiber_coords)

            start_path = f"{start_path_base}{fiber_data['job_number']}{'.sh' if OS == 'UNIX-LIKE' else '.bat'}"

            stimamp_top, stimamp_bottom = get_thresh_bounds(sim_dir, sim_name, inner_ind)
            if stimamp_top is not None and stimamp_bottom is not None:
                make_task(
                    submission_context,
                    OS,
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


def make_run_sub_list(run_number: int):
    """Create a list of all fiber simulations to be run. Skips fiber sims with existing output.

    :param run_number: the number of the run
    :return: a dict of all fiber simulations to be run
    """
    # build configuration filename
    filename: str = os.path.join('runs', f'{run_number}.json')
    # load in configuration data
    run = load(filename)

    submit_list = {}

    # assign appropriate configuration data
    samples = [run.get('sample', [])]
    models = run.get('models', [])
    sims = run.get('sims', [])

    for sample in samples:
        # loop models, sims
        for model in models:
            for sim in sims:
                sim_dir = os.path.join('n_sims')
                sim_name_base = f'{sample}_{model}_{sim}_'
                nsim_list = [x for x in os.listdir(sim_dir) if x.startswith(sim_name_base)]
                for sim_name in nsim_list:
                    submit_list[sim_name] = []

                    sim_path = os.path.join(sim_dir, sim_name)
                    fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                    output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))

                    n_sim = sim_name.split('_')[-1]
                    sim_config = load(os.path.join(sim_path, f'{n_sim}.json'))

                    fibers_files = [
                        x for x in os.listdir(fibers_path) if re.match('(?:(src)_)?inner[0-9]+_fiber[0-9]+\\.dat', x)
                    ]  # First regex group with ? is optional - for backwards compatibility

                    for i, fiber_filename in enumerate(fibers_files):
                        master_fiber_name = str(fiber_filename.split('.')[0])
                        *cuff_type, inner_name, fiber_name = tuple(
                            master_fiber_name.split('_')
                        )  # not backwards compatible
                        inner_ind = int(inner_name.split('inner')[-1])
                        fiber_ind = int(fiber_name.split('fiber')[-1])

                        if sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
                            n_amp = len(sim_config['protocol']['amplitudes'])
                            search_path = os.path.join(
                                output_path,
                                f'activation_inner{inner_ind}_fiber{fiber_ind}_amp{n_amp - 1}.dat',
                            )
                        else:
                            search_path = os.path.join(
                                output_path,
                                f'thresh_inner{inner_ind}_fiber{fiber_ind}.dat',
                            )

                        if os.path.exists(search_path):
                            if args.verbose:
                                print(f'Found {search_path} -->\t\tskipping inner ({inner_ind}) fiber ({fiber_ind})')
                                time.sleep(1)
                            continue

                        submit_list[sim_name].append(
                            {"job_number": i, "cuff_type": cuff_type, "inner": inner_ind, "fiber": fiber_ind}
                        )
                    # save_submit list as csv
                    pd.DataFrame(submit_list[sim_name]).to_csv(os.path.join(sim_path, 'out_err_key.csv'), index=False)

    return submit_list


def confirm_submission(n_fibers, rundata, submission_context):
    """Confirm that the user wants to submit the simulations.

    :param n_fibers: the number of fibers to be run
    :param rundata: the run data (JSON config)
    :param submission_context: the submission context (e.g. cluster or local)
    """
    if n_fibers == 0:
        sys.exit('No fibers to run. Exiting...')
    if not args.skip_summary:
        # format run data
        df = pd.DataFrame(rundata)
        df.RUN = df.RUN.astype(int)
        df = df.sort_values('RUN')
        # print out and check that the user is happy
        print(f'Submitting the following runs (submission_context={submission_context}):')
        print(df.to_string(index=False))
        print(f'Will result in running {n_fibers} fiber simulations')
        proceed = input('\t Would you like to proceed?\n' '\t\t 0 = NO\n' '\t\t 1 = YES\n')
        if int(proceed) != 1:
            sys.exit()
        else:
            print('Proceeding...')
    else:
        print(f'Skipping summary, submitting {n_fibers} fibers...')


def get_submission_list(run_inds):
    """Get the list of simulations to be submitted for all runs.

    :param run_inds: the list of run indices
    :return: summary of runs, a list of all simulations to be submitted
    """
    rundata = []
    submission_list = {}
    for run_number in run_inds:
        # build configuration filename
        filename = os.path.join('runs', f'{run_number}.json')

        # configuration file exists
        assert os.path.exists(filename), f'Run configuration not found: {run_number}'

        # load in configuration data
        run = load(filename)

        # configuration is not empty
        assert len(run.items()) > 0, f'Encountered empty run configuration: {filename}'

        print(f'Generating run list for run {run_number}')
        # sleep to make it not too fast
        time.sleep(1)
        # get list of fibers to run
        submission_addition = make_run_sub_list(run_number)
        # check for duplicate nsims
        if any(x in submission_list for x in submission_addition.keys()):
            warnings.warn(f'Duplicate nsims found in run {run_number}. Continuing', stacklevel=2)
        submission_list.update(submission_addition)
        rundata.append(
            {
                'RUN': run_number,
                'SAMPLE': run['sample'],
                'MODELS': run['models'],
                'SIMS': run['sims'],
            }
        )
    return rundata, submission_list


def pre_submit_setup():
    """Perform setup for submitting simulations.

    :return: the list of runs to be submitted, submission_context
    """
    # validate inputs
    global args
    args = parser.parse_args()
    if args.all_runs is True:
        if len(args.run_indices) > 0:
            sys.exit('Error: Cannot use -A/--run-all argument and pass run indices.')
        args.run_indices = [int(os.path.splitext(file)[0]) for file in os.listdir('runs') if file.endswith('.json')]
    if len(args.run_indices) == 0:
        sys.exit("Error: No run indices to use.")
    run_inds = args.run_indices
    # compile MOD files if they have not yet been compiled
    auto_compile(args.force_recompile)
    # check for submission context
    if args.cluster_submit:
        submission_context = 'cluster'
    elif args.local_submit:
        submission_context = 'local'
    else:
        submission_context = 'cluster' if shutil.which('sbatch') is not None else 'local'

    return run_inds, submission_context


# main
def main():
    """Prepare fiber submissions and run NEURON sims."""
    # pre submit setup
    run_inds, submission_context = pre_submit_setup()
    # get list of simulations to be submitted
    rundata, submission_list = get_submission_list(run_inds)
    # confirm that the user wants to submit the simulations
    n_fibers = sum([len(x) for x in submission_list.values()])
    confirm_submission(n_fibers, rundata, submission_context)
    # make shell scripts for fiber submission
    print('Performing setup for fiber submission...')
    make_fiber_tasks(submission_list, submission_context)
    # submit fibers
    print('Submitting...')
    submit_fibers(submission_context, submission_list)


if __name__ == "__main__":  # Allows for the safe importing of the main module
    main()
    print('done')
