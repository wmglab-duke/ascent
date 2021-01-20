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


def auto_compile():
    if (not os.path.exists(os.path.join('MOD_Files/x86_64')) and OS == 'UNIX-LIKE') or \
            (not os.path.exists(os.path.join('MOD_Files', 'nrnmech.dll')) and OS == 'WINDOWS'):
        print('compile')
        os.chdir(os.path.join('MOD_Files'))
        subprocess.run(['nrnivmodl'], shell=True)
        os.chdir('..')
        compiled = True
    else:
        print('skipped compile')
        compiled = False
    return compiled


def local_submit(my_local_args):
    sim_path = my_local_args['sim_path']
    os.chdir(sim_path)

    start = my_local_args['start']
    out_filename = my_local_args['output_log']
    err_filename = my_local_args['error_log']

    with open(out_filename, "w+") as fo, open(err_filename, "w+") as fe:
        p = subprocess.call(['bash', start] if OS == 'UNIX-LIKE' else [start], stdout=fo, stderr=fe)


#  TODO update (this is only used to make lists for local submissions)
def make_local_submission_lists():
    local_args_lists = []
    submission_contexts = []
    run_filenames = []

    for run_number in sys.argv[1:]:
        # run number is numeric
        assert re.search('[0-9]+', run_number), 'Encountered non-number run number argument: {}'.format(run_number)

        # build configuration filename
        filename = os.path.join('runs', run_number + '.json')
        run_filenames.append(filename)

        # configuration file exists
        assert os.path.exists(filename), 'Run configuration not found: {}'.format(run_number)

        local_args_list = []

        # load in configuration data
        run: dict = {}
        with open(filename, 'r') as file:
            run = json.load(file)

        # configuration is not empty
        assert len(run.items()) > 0, 'Encountered empty run configuration: {}'.format(filename)

        submission_context = run.get('submission_context', 'cluster')
        submission_contexts.append(submission_context)

        # submission context is valid
        assert submission_context in ALLOWED_SUBMISSION_CONTEXTS, 'Invalid submission context: {}'.format(
            submission_context)

        if submission_context == 'local':
            local_run_keys = ['start', 'output_log', 'error_log', 'sim_path']
            local_args = dict.fromkeys(local_run_keys, [])

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
                    array_job_number = 1
                    start_paths_list = []

                    sim_path = os.path.join(sim_dir, sim_name)
                    fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                    output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))
                    out_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'out'))
                    err_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'err'))

                    # ensure log directories exist
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

                    print('\n\n################ {} ################\n\n'.format(sim_name))

                    for fiber_filename in [x for x in os.listdir(fibers_path)
                                           if re.match('inner[0-9]+_fiber[0-9]+\\.dat', x)]:
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

                        # cluster
                        if submission_context == 'cluster':
                            start_path_base = os.path.join(sim_path, 'start_')
                            start_path = '{}{}{}'.format(start_path_base,
                                                         array_job_number,
                                                         '.sh' if OS == 'UNIX-LIKE' else '.bat')

                        else:
                            # local
                            start_path = os.path.join(sim_path, '{}_{}_start{}'.format(inner_ind, fiber_ind,
                                                                                       '.sh' if OS == 'UNIX-LIKE'
                                                                                       else '.bat'))

                        if sim_config['protocol']['mode'] == 'ACTIVATION_THRESHOLD' \
                                or sim_config['protocol']['mode'] == 'BLOCK_THRESHOLD':
                            if 'scout_sim' in sim_config['protocol']['bounds_search'].keys():
                                # load in threshold from scout_sim
                                # (example use would be to run centroid first,
                                # then any other xy-mmode after to save computation)

                                scout_sim = sim_config['protocol']['bounds_search']['scout_sim']
                                scout_sim_dir = os.path.join('n_sims')
                                scout_sim_name = '{}_{}_{}_{}'.format(sample, model, scout_sim, n_sim)
                                scout_sim_path = os.path.join(scout_sim_dir, scout_sim_name)
                                scout_output_path = os.path.abspath(os.path.join(scout_sim_path, 'data', 'outputs'))
                                scout_thresh_path = os.path.join(scout_output_path,
                                                                 'thresh_inner{}_fiber{}.dat'.format(inner_ind,
                                                                                                     0))
                                if os.path.exists(scout_thresh_path):
                                    stimamp = abs(np.loadtxt(thresh_path))
                                else:
                                    raise Exception('Sorry, no fiber threshold exists for '
                                                    'scout sim: inner{} fiber0'.format(inner_ind))

                                if len(np.atleast_1d(stimamp)) > 1:
                                    stimamp = stimamp[-1]

                                step = sim_config['protocol']['bounds_search']['step'] / 100
                                stimamp_top = (1 + step) * stimamp
                                stimamp_bottom = (1 - step) * stimamp

                                unused_protocol_keys = ['top', 'bottom']

                                if any(unused_protocol_key in sim_config['protocol']['bounds_search'].keys()
                                       for unused_protocol_key in unused_protocol_keys):
                                    warnings.warn('WARNING: scout_sim is defined in Sim, so no using "top" or "bottom" '
                                                  'which you also defined \n')
                            else:
                                stimamp_top = sim_config['protocol']['bounds_search']['top']
                                stimamp_bottom = sim_config['protocol']['bounds_search']['bottom']

                        elif sim_config['protocol']['mode'] == 'FINITE_AMPLITUDES':
                            stimamp_top, stimamp_bottom = 0, 0

                        start_paths_list.append(start_path)
                        array_job_number += 1

                        with open(start_path, 'w+') as handle:
                            lines = []
                            if OS == 'UNIX-LIKE':
                                lines = [
                                    '#!/bin/bash\n',
                                    'cd \"{}\"\n'.format(sim_path if submission_context == 'cluster' else '.'),
                                    'chmod a+rwx special\n',
                                    './special -nobanner '
                                    '-c \"strdef sim_path\" '
                                    '-c \"sim_path=\\\"{}\\\"\" '
                                    '-c \"inner_ind={}\" '
                                    '-c \"fiber_ind={}\" '
                                    '-c \"stimamp_top={}\" '
                                    '-c \"stimamp_bottom={}\" '
                                    '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'.format(sim_path,
                                                                                              inner_ind,
                                                                                              fiber_ind,
                                                                                              stimamp_top,
                                                                                              stimamp_bottom)
                                ]

                                # copy special files ahead of time to avoid 'text file busy error'
                                shutil.copy(os.path.join('MOD_Files', 'x86_64', 'special'), sim_path)

                            else:  # OS is 'WINDOWS'
                                sim_path_win = os.path.join(*sim_path.split(os.pathsep)).replace('\\', '\\\\')
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
                                                                                              inner_ind,
                                                                                              fiber_ind,
                                                                                              stimamp_top,
                                                                                              stimamp_bottom)
                                ]

                            handle.writelines(lines)
                            handle.close()

                        # submit batch job for fiber
                        job_name = '{}_{}'.format(sim_name, master_fiber_name)
                        output_log = os.path.join(out_dir, '{}{}'.format(master_fiber_name, '.log'))
                        error_log = os.path.join(err_dir, '{}{}'.format(master_fiber_name, '.log'))

                        if submission_context == 'cluster':
                            if len(start_paths_list) == job_number_max:

                                # command = ' '.join([
                                #     'sbatch',
                                #     '--job-name={}'.format(job_name),
                                #     '--output={}'.format(output_log),
                                #     '--error={}'.format(error_log),  # --array=1-10
                                #     '--array=1-{}'.format(job_number_max),
                                #     '--mem=8000',
                                #     '-p', 'wmglab',
                                #     '-c', '1',
                                #     '{}${{SLURM_ARRAY_TASK_ID}}{}'.format(start_path_base, '.sh')  #
                                # ])
                                #
                                # print(command)
                                #
                                # os.system(command)

                                os.system('sbatch --job-name={} --output={} --error={} '
                                          '--array=1-{} test.slurm {}'.format(job_name,
                                                                              output_log,
                                                                              error_log,
                                                                              len(start_paths_list),
                                                                              start_path_base))

                                # allow job to start before removing slurm file
                                time.sleep(1.0)

                                # remove start.slurm
                                # for my_start_path in start_paths_list:
                                #     os.remove(my_start_path)

                                # reset
                                array_job_number = 1
                                start_paths_list = []

                            else:
                                pass

                        elif submission_context == 'local':
                            local_args['start'] = start_path.split(os.path.sep)[-1]
                            local_args['output_log'] = os.path.join('logs', 'out', output_log.split(os.path.sep)[-1])
                            local_args['error_log'] = os.path.join('logs', 'err', error_log.split(os.path.sep)[-1])
                            local_args['sim_path'] = os.path.abspath(sim_path)
                            local_args_list.append(local_args.copy())

        local_args_lists.append(local_args_list)

        # catch the remaining tasks at the end
        if len(start_paths_list) > 0:
            # command = ' '.join([
            #     'sbatch',
            #     '--job-name={}'.format(job_name),
            #     '--output={}'.format(output_log),
            #     '--error={}'.format(error_log),  # --array=1-10
            #     '--mem=8000',
            #     '--array=1-{}'.format(len(start_paths_list)),
            #     '-p', 'wmglab',
            #     '-c', '1',
            #     '{}$SLURM_ARRAY_TASK_ID{}'.format(start_path_base, '.sh')
            # ])
            #
            # os.system(command)
            os.system('sbatch --job-name={} --output={} --error={} '
                      '--array=1-{} test.slurm {}'.format(job_name,
                                                          output_log,
                                                          error_log,
                                                          len(start_paths_list),
                                                          start_path_base))

            # allow job to start before removing slurm file
            time.sleep(1.0)

            # remove start.slurm
            # for my_start_path in start_paths_list:
            #     os.remove(my_start_path)

            # reset
            array_job_number = 1
            start_paths_list = []

    return local_args_lists, submission_contexts, run_filenames  # TODO


def cluster_submit(run_number: int, array_length_max: int = 10):
    # build configuration filename
    filename: str = os.path.join('runs', run_number + '.json')

    # load in configuration data
    run: dict = load(filename)

    # assign appropriate configuration data
    sample = run.get('sample', [])
    models = run.get('models', [])
    sims = run.get('sims', [])

    job_count = 1

    # loop models, sims
    for model in models:
        for sim in sims:
            sim_dir = os.path.join('n_sims')
            sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

            for sim_name in [x for x in os.listdir(sim_dir) if sim_name_base in x]:
                array_index = 1
                start_paths_list = []

                sim_path = os.path.join(sim_dir, sim_name)
                fibers_path = os.path.abspath(os.path.join(sim_path, 'data', 'inputs'))
                output_path = os.path.abspath(os.path.join(sim_path, 'data', 'outputs'))
                out_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'out'))
                err_dir = os.path.abspath(os.path.join(sim_path, 'logs', 'err'))
                start_path_base = os.path.join(sim_path, 'start_')

                # ensure log directories exist
                for cur_dir in [out_dir, err_dir]:
                    if not os.path.exists(cur_dir):
                        os.makedirs(cur_dir)

                # ensure blank.hoc exists
                blank_path = os.path.join(sim_path, 'blank.hoc')
                if not os.path.exists(blank_path):
                    open(blank_path, 'w').close()

                fibers_files = [x for x in os.listdir(fibers_path) if re.match('inner[0-9]+_fiber[0-9]+\\.dat', x)]
                max_fibers_files_ind = len(fibers_files) - 1

                for fiber_file_ind, fiber_filename in enumerate(fibers_files):
                    master_fiber_name = str(fiber_filename.split('.')[0])
                    inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                    inner_ind = int(inner_name.split('inner')[-1])
                    fiber_ind = int(fiber_name.split('fiber')[-1])

                    thresh_path = os.path.join(output_path, f"thresh_inner{inner_ind}_fiber{fiber_ind}.dat")
                    if os.path.exists(thresh_path):
                        print(f"Found {thresh_path} -->\t\tskipping inner ({inner_ind}) fiber ({fiber_ind})")
                        continue
                    else:
                        start_path = '{}{}{}'.format(start_path_base, job_count, '.sh' if OS == 'UNIX-LIKE' else '.bat')
                        start_paths_list.append(start_path)

                        stimamp_top = -1  # TODO
                        stimamp_bottom = -0.1  # TODO

                        with open(start_path, 'w+') as handle:
                            lines = []
                            if OS == 'UNIX-LIKE':
                                lines = [
                                    '#!/bin/bash\n',
                                    'cd \"{}\"\n'.format(sim_path),
                                    'chmod a+rwx special\n',
                                    './special -nobanner '
                                    '-c \"strdef sim_path\" '
                                    '-c \"sim_path=\\\"{}\\\"\" '
                                    '-c \"inner_ind={}\" '
                                    '-c \"fiber_ind={}\" '
                                    '-c \"stimamp_top={}\" '
                                    '-c \"stimamp_bottom={}\" '
                                    '-c \"load_file(\\\"launch.hoc\\\")\" blank.hoc\n'.format(sim_path,
                                                                                              inner_ind,
                                                                                              fiber_ind,
                                                                                              stimamp_top,
                                                                                              stimamp_bottom)
                                ]

                                # TODO only if doesnt exist
                                # copy special files ahead of time to avoid 'text file busy error'
                                shutil.copy(os.path.join('MOD_Files', 'x86_64', 'special'), sim_path)

                            else:  # OS is 'WINDOWS'
                                sim_path_win = os.path.join(*sim_path.split(os.pathsep)).replace('\\', '\\\\')
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
                                                                                              inner_ind,
                                                                                              fiber_ind,
                                                                                              stimamp_top,
                                                                                              stimamp_bottom)
                                ]

                            handle.writelines(lines)
                            handle.close()

                        if array_index == array_length_max or fiber_file_ind == max_fibers_files_ind:
                            # submit batch job for fiber
                            job_name = '{}_{}'.format(sim_name, master_fiber_name)  # TODO (sim_array_batch?)
                            output_log = os.path.join(out_dir, '{}{}'.format(master_fiber_name, '.log'))  # TODO
                            error_log = os.path.join(err_dir, '{}{}'.format(master_fiber_name, '.log'))  # TODO
                            # print('begin range: {}'.format(1 + job_count - len(start_paths_list)))
                            # print('end range: {}'.format(job_count))

                            os.system(f"sbatch --job-name={job_name} --output={output_log} --error={error_log} "
                                      f"--array={1 + job_count - len(start_paths_list)}-{job_count} array_launch.slurm {start_path_base}")  # TODO better name for test.slurm

                            # allow job to start before removing slurm file
                            time.sleep(1.0)
                            start_paths_list = []
                            array_index = 1
                        else:
                            array_index += 1

                        job_count += 1


def main():
    # validate inputs
    runs = []
    submission_contexts = []

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

            submit_list = make_local_submission_lists()  # TODO
            pool = multiprocessing.Pool(cpus)
            result = pool.map(local_submit, submit_list)

        elif sub_context == 'cluster':
            cluster_submit(run_index)


if __name__ == "__main__":  # Allows for the safe importing of the main module
    main()
