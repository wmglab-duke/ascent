import multiprocessing
import os
import shutil
import subprocess
import sys
import re
import json
import time
import numpy as np
import warnings

ALLOWED_SUBMISSION_CONTEXTS = ['cluster', 'local']
OS = 'UNIX-LIKE' if any([s in sys.platform for s in ['darwin', 'linux']]) else 'WINDOWS'


def load(config_path: str):
    """
    Loads in json data and returns to user, assuming it has already been validated.
    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path, "r") as handle:
        # print('load "{}" --> key "{}"'.format(config, key))
        return json.load(handle)


def auto_compile(override: bool = False):
    if (not os.path.exists(os.path.join('MOD_Files/x86_64')) and OS == 'UNIX-LIKE') or \
            (not os.path.exists(os.path.join('MOD_Files', 'nrnmech.dll')) and OS == 'WINDOWS') or override:
        print('compile')
        os.chdir(os.path.join('MOD_Files'))
        subprocess.run(['nrnivmodl'], shell=True)
        os.chdir('..')
        compiled = True
    else:
        print('skipped compile')
        compiled = False
    return compiled


def get_thresh_bounds(sim_dir: str, sim_name: str, inner_ind: int):
    top, bottom = None, None

    sample = sim_name.split('_')[0]
    model = sim_name.split('_')[1]
    sim = sim_name.split('_')[2]
    n_sim = sim_name.split('_')[3]

    sim_config = load(os.path.join(sim_dir, sim_name, '{}.json'.format(n_sim)))

    if sim_config['protocol']['mode'] == 'ACTIVATION_THRESHOLD' or sim_config['protocol']['mode'] == 'BLOCK_THRESHOLD':
        if 'scout_sim' in sim_config['protocol']['bounds_search'].keys():
            # load in threshold from scout_sim (example use: run centroid first, then any other xy-mode after)

            scout_sim = sim_config['protocol']['bounds_search']['scout_sim']
            scout_sim_dir = os.path.join('n_sims')
            scout_sim_name = '{}_{}_{}_{}'.format(sample, model, scout_sim, n_sim)
            scout_sim_path = os.path.join(scout_sim_dir, scout_sim_name)
            scout_output_path = os.path.abspath(os.path.join(scout_sim_path, 'data', 'outputs'))
            scout_thresh_path = os.path.join(scout_output_path, 'thresh_inner{}_fiber{}.dat'.format(inner_ind, 0))

            if os.path.exists(scout_thresh_path):
                stimamp = abs(np.loadtxt(scout_thresh_path))

                if len(np.atleast_1d(stimamp)) > 1:
                    stimamp = stimamp[-1]

                step = sim_config['protocol']['bounds_search']['step'] / 100
                top = (1 + step) * stimamp
                bottom = (1 - step) * stimamp

                unused_protocol_keys = ['top', 'bottom']

                if any(unused_protocol_key in sim_config['protocol']['bounds_search'].keys()
                       for unused_protocol_key in unused_protocol_keys):
                    warnings.warn('WARNING: scout_sim is defined in Sim, so not using "top" or "bottom" '
                                  'which you also defined \n')

            else:
                warnings.warn(f"No fiber threshold exists for scout sim: inner{inner_ind} fiber0")

        else:
            top = sim_config['protocol']['bounds_search']['top']
            bottom = sim_config['protocol']['bounds_search']['bottom']

    elif sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
        top, bottom = 0, 0

    return top, bottom


def make_task(my_os: str, start_p: str, sim_p: str, inner: int, fiber: int, top: float, bottom: float):
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
                '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'.format(sim_p,
                                                                          inner,
                                                                          fiber,
                                                                          top,
                                                                          bottom)
            ]

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
                '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'.format(os.getcwd(),
                                                                          sim_path_win,
                                                                          inner,
                                                                          fiber,
                                                                          top,
                                                                          bottom)
            ]

        handle.writelines(lines)
        handle.close()


def local_submit(my_local_args: dict):
    sim_path = my_local_args['sim_path']
    os.chdir(sim_path)

    start = my_local_args['start']
    out_filename = my_local_args['output_log']
    err_filename = my_local_args['error_log']

    with open(out_filename, "w+") as fo, open(err_filename, "w+") as fe:
        p = subprocess.call(['bash', start] if OS == 'UNIX-LIKE' else [start], stdout=fo, stderr=fe)


def cluster_submit(run_number: int, array_length_max: int = 10):
    # configuration is not empty
    assert array_length_max > 0, 'SLURM Job Array length is not > 0: array_length_max={}'.format(array_length_max)

    # build configuration filename
    filename: str = os.path.join('runs', run_number + '.json')

    # load in configuration data
    run: dict = load(filename)

    # assign appropriate configuration data
    sample = run.get('sample', [])
    models = run.get('models', [])
    sims = run.get('sims', [])

    job_count = 1
    data = [[], [], []]

    # loop models, sims
    for model in models:
        for sim in sims:
            sim_dir = os.path.join('n_sims')
            sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

            for sim_name in [x for x in os.listdir(sim_dir) if sim_name_base in x]:
                print('\n\n################ {} ################\n\n'.format(sim_name))

                array_index = 1
                start_paths_list = []
                sim_array_batch = 1
                sim_config = []

                sim_path = os.path.join(sim_dir, sim_name)
                fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))
                start_path_base = os.path.join(sim_path, 'start_')

                # ensure log directories exist
                out_dir = os.path.join(sim_path, 'logs', 'out', '')
                err_dir = os.path.join(sim_path, 'logs', 'err', '')
                for cur_dir in [out_dir, err_dir]:
                    if not os.path.exists(cur_dir):
                        os.makedirs(cur_dir)

                # ensure blank.hoc exists
                blank_path = os.path.join(sim_path, 'blank.hoc')
                if not os.path.exists(blank_path):
                    open(blank_path, 'w').close()

                fibers_files = [x for x in os.listdir(fibers_path) if re.match('inner[0-9]+_fiber[0-9]+\\.dat', x)]
                max_fibers_files_ind = len(fibers_files) - 1

                inner_index_tally = []
                fiber_index_tally = []

                missing_total = 0
                for fiber_file_ind, fiber_filename in enumerate(fibers_files):
                    master_fiber_name = str(fiber_filename.split('.')[0])
                    inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                    inner_ind = int(inner_name.split('inner')[-1])
                    fiber_ind = int(fiber_name.split('fiber')[-1])

                    thresh_path = os.path.join(output_path, f"thresh_inner{inner_ind}_fiber{fiber_ind}.dat")
                    if os.path.exists(thresh_path):
                        continue
                    else:
                        missing_total += 1
                        inner_ind_solo = inner_ind
                        fiber_ind_solo = fiber_ind
                        master_fiber_name_solo = master_fiber_name

                if missing_total == 0:
                    continue

                elif missing_total == 1:
                    stimamp_top, stimamp_bottom = get_thresh_bounds(sim_dir, sim_name, inner_ind_solo)
                    start_path_solo = os.path.join(sim_path, 'start{}'.format('.sh' if OS == 'UNIX_LIKE' else '.bat'))

                    if stimamp_top is not None and stimamp_bottom is not None:
                        make_task(OS, start_path_solo, sim_path, inner_ind_solo, fiber_ind_solo, stimamp_top, stimamp_bottom)

                        # submit batch job for fiber
                        job_name = '{}_{}'.format(sim_name, master_fiber_name_solo)
                        output_log = os.path.join(out_dir, '{}{}'.format(master_fiber_name_solo, '.log'))
                        error_log = os.path.join(err_dir, '{}{}'.format(master_fiber_name_solo, '.log'))

                        print('========= SUBMITTING SOLO: {} ==========='.format(job_name))

                        command = ' '.join([
                            'sbatch',
                            '--job-name={}'.format(job_name),
                            '--output={}'.format(output_log),
                            '--error={}'.format(error_log),
                            '--mem=8000',
                            '-p', 'wmglab',
                            '-c', '1',
                            start_path_solo
                        ])
                        os.system(command)

                        # allow job to start before removing slurm file
                        time.sleep(1.0)
                    else:
                        print('MISSING DEFINITION OF TOP AND BOTTOM ==========================')
                        continue

                else:

                    print('================= ARRAY SUBMITTING ====================')
                    for fiber_file_ind, fiber_filename in enumerate(fibers_files):
                        master_fiber_name = str(fiber_filename.split('.')[0])
                        inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                        inner_ind = int(inner_name.split('inner')[-1])
                        fiber_ind = int(fiber_name.split('fiber')[-1])

                        thresh_path = os.path.join(output_path, f"thresh_inner{inner_ind}_fiber{fiber_ind}.dat")
                        if os.path.exists(thresh_path):
                            # print(f"Found {thresh_path} -->\t\tskipping inner ({inner_ind}) fiber ({fiber_ind})")
                            continue
                        else:
                            # print(f"MISSING {thresh_path} -->\t\trunning inner ({inner_ind}) fiber ({fiber_ind})")
                            time.sleep(1)
                            start_path = '{}{}{}'.format(start_path_base, job_count, '.sh' if OS == 'UNIX-LIKE' else '.bat')
                            start_paths_list.append(start_path)

                            inner_index_tally.append(inner_ind)
                            fiber_index_tally.append(fiber_ind)

                            stimamp_top, stimamp_bottom = get_thresh_bounds(sim_dir, sim_name, inner_ind)
                            if stimamp_top is not None and stimamp_bottom is not None:
                                make_task(OS, start_path, sim_path, inner_ind, fiber_ind, stimamp_top, stimamp_bottom)
                                array_index += 1
                                job_count += 1

                            if array_index == array_length_max or fiber_file_ind == max_fibers_files_ind:
                                # output key, since we lose this in array method
                                start = 1 + job_count - len(start_paths_list)
                                key_file = os.path.join(sim_path, 'out_err_key.txt')

                                data[0].append([x for x in range(start, job_count + 1)])
                                data[1].append(inner_index_tally)
                                data[2].append(fiber_index_tally)

                                if fiber_file_ind == max_fibers_files_ind:
                                    with open(key_file, "ab") as f:
                                        np.savetxt(f,
                                                   ([x for xs in data[0] for x in xs],
                                                    [y for ys in data[1] for y in ys],
                                                    [z for zs in data[2] for z in zs]),
                                                   fmt='%d')

                                    data = [[], [], []]

                                # submit batch job for fiber
                                job_name = f"{sim_name}_{sim_array_batch}"
                                print('================== SUBMITTING ARRAY: {}'.format(job_name))
                                os.system(f"sbatch --job-name={job_name} --output={out_dir}%a.log "
                                          f"--error={err_dir}%a.log --array={start}-{job_count} "
                                          f"array_launch.slurm {start_path_base}")

                                # allow job to start before removing slurm file
                                time.sleep(1.0)

                                array_index = 1
                                sim_array_batch += 1
                                start_paths_list = []
                                inner_index_tally = []
                                fiber_index_tally = []


def make_local_submission_list(run_number: int):

    # build configuration filename
    filename = os.path.join('runs', run_number + '.json')

    # create empty list of args (for local submission with parallelization) for each Run
    local_args_list = []

    # load in configuration data
    run = load(filename)

    # keys required for each local submission
    local_run_keys = ['start', 'output_log', 'error_log', 'sim_path']

    # assign appropriate configuration data
    sample = run.get('sample', [])
    models = run.get('models', [])
    sims = run.get('sims', [])

    # loop models, sims
    for model in models:
        for sim in sims:
            sim_dir = os.path.join('n_sims')
            sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

            for sim_name in [x for x in os.listdir(sim_dir) if sim_name_base in x]:
                print('\n\n################ {} ################\n\n'.format(sim_name))

                sim_path = os.path.join(sim_dir, sim_name)
                fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))

                # ensure log directories exist
                out_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'out'))
                err_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'err'))
                for cur_dir in [out_dir, err_dir]:
                    if not os.path.exists(cur_dir):
                        os.makedirs(cur_dir)

                # ensure blank.hoc exists
                blank_path = os.path.join(sim_path, 'blank.hoc')
                if not os.path.exists(blank_path):
                    open(blank_path, 'w').close()

                # load JSON file with binary search amplitudes
                n_sim = sim_name.split('_')[-1]
                sim_config = load(os.path.join(sim_path, '{}.json'.format(n_sim)))

                for fiber_filename in [x for x in os.listdir(fibers_path) if re.match('inner[0-9]+_fiber['
                                                                                      '0-9]+\\.dat', x)]:
                    master_fiber_name = str(fiber_filename.split('.')[0])
                    inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                    inner_ind = int(inner_name.split('inner')[-1])
                    fiber_ind = int(fiber_name.split('fiber')[-1])

                    thresh_path = os.path.join(output_path,
                                               'thresh_inner{}_fiber{}.dat'.format(inner_ind, fiber_ind))
                    if os.path.exists(thresh_path):
                        print('Found {} -->\t\tskipping inner ({}) fiber ({})'.format(thresh_path, inner_ind,
                                                                                      fiber_ind))
                        continue

                    # local
                    start_path = os.path.join(sim_path, '{}_{}_start{}'.format(inner_ind, fiber_ind,
                                                                               '.sh' if OS == 'UNIX-LIKE'
                                                                               else '.bat'))
                    stimamp_top, stimamp_bottom = get_thresh_bounds(sim_dir, sim_name, inner_ind)
                    make_task(OS, start_path, sim_path, inner_ind, fiber_ind, stimamp_top, stimamp_bottom)

                    # submit batch job for fiber
                    output_log = os.path.join(out_dir, '{}{}'.format(master_fiber_name, '.log'))
                    error_log = os.path.join(err_dir, '{}{}'.format(master_fiber_name, '.log'))

                    local_args = dict.fromkeys(local_run_keys, [])
                    local_args['start'] = start_path.split(os.path.sep)[-1]
                    local_args['output_log'] = os.path.join('logs', 'out', output_log.split(os.path.sep)[-1])
                    local_args['error_log'] = os.path.join('logs', 'err', error_log.split(os.path.sep)[-1])
                    local_args['sim_path'] = os.path.abspath(sim_path)
                    local_args_list.append(local_args.copy())

    return local_args_list


def main():
    # validate inputs
    runs = []
    submission_contexts = []

    # compile MOD files if they have not yet been compiled, can provide override=True to compile no matter what
    auto_compile()

    for run_number in sys.argv[1:]:
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

        submission_context = run.get('submission_context', 'cluster')
        # submission context is valid
        assert submission_context in ALLOWED_SUBMISSION_CONTEXTS, 'Invalid submission context: {}'.format(
            submission_context)
        submission_contexts.append(submission_context)

    # submit_lists, sub_contexts, run_filenames = make_submission_list()
    for sub_context, run_index in zip(submission_contexts, runs):

        if sub_context == 'local':
            filename = os.path.join('runs', run_index + '.json')
            run = load(filename)

            if 'local_avail_cpus' in run:
                cpus = run.get('local_avail_cpus')

                if cpus > multiprocessing.cpu_count() - 1:
                    raise ValueError('local_avail_cpus in Run asking for more than cpu_count-1 CPUs')

                print(f"Submitting Run {run_index} locally to {cpus} CPUs (defined by local_avail_cpus in Run)")

            else:
                cpus = multiprocessing.cpu_count() - 1
                print(f"local_avail_cpus not defined in Run, so proceeding with cpu_count-1={cpus} CPUs")

            submit_list = make_local_submission_list(run_index)
            pool = multiprocessing.Pool(cpus)
            result = pool.map(local_submit, submit_list)

        elif sub_context == 'cluster':
            cluster_submit(run_index)

        else:
            # something went horribly wrong
            pass



if __name__ == "__main__":  # Allows for the safe importing of the main module
    main()
