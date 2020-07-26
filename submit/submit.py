import multiprocessing
import os
import shutil
import subprocess
import sys
import re
import json
import time

from src.utils import NeuronRunMode

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


def make_submission_list():
    if (not os.path.exists(os.path.join('MOD_Files/x86_64')) and OS == 'UNIX-LIKE') or \
            (not os.path.exists(os.path.join('MOD_Files', 'nrnmech.dll')) and OS == 'WINDOWS'):
        print('compile')
        os.chdir(os.path.join('MOD_Files'))
        subprocess.run(['nrnivmodl'], shell=True)
        os.chdir('..')

    local_args_lists = []

    for run_number in sys.argv[1:]:
        # run number is numeric
        assert re.search('[0-9]+', run_number), 'Encountered non-number run number argument: {}'.format(run_number)

        # build configuration filename
        filename = os.path.join('runs', run_number + '.json')

        # configuration file exists
        assert os.path.exists(filename), 'Run configuration not found: {}'.format(run_number)

        local_args_list = []

        # load in configuration data
        run: dict = {}
        with open(filename, 'r') as file:
            run = json.load(file)

        # configuration is not empty
        assert len(run.items()) > 0, 'Encountered empty run configuration: {}'.format(filename)

        # assign appropriate configuration data
        sample = run.get('sample', [])
        models = run.get('models', [])
        sims = run.get('sims', [])
        submission_context = run.get('submission_context', 'cluster')

        # submission context is valid
        assert submission_context in ALLOWED_SUBMISSION_CONTEXTS, 'Invalid submission context: {}'.format(
            submission_context)

        if submission_context == 'local':
            local_run_keys = ['start', 'output_log', 'error_log', 'sim_path']
            local_args = dict.fromkeys(local_run_keys, [])

        # loop models, sims
        for model in models:
            for sim in sims:
                sim_dir = os.path.join('n_sims')
                sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

                for sim_name in [x for x in os.listdir(sim_dir) if sim_name_base in x]:
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

                    if sim_config['protocol']['mode'] == NeuronRunMode.ACTIVATION_THRESHOLD.name \
                            or sim_config['protocol']['mode'] == NeuronRunMode.BLOCK_THRESHOLD.name:
                        stimamp_top = sim_config['protocol']['bounds_search']['top']
                        stimamp_bottom = sim_config['protocol']['bounds_search']['bottom']
                    elif sim_config['protocol']['mode'] == NeuronRunMode.FINITE_AMPLITUDES:
                        stimamp_top, stimamp_bottom = 0, 0

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
                            start_path = os.path.join(sim_path, 'start{}'.format('.sh' if OS == 'UNIX_LIKE'
                                                                                 else '.bat'))
                        else:
                            # local
                            start_path = os.path.join(sim_path, '{}_{}_start{}'.format(inner_ind, fiber_ind,
                                                                                       '.sh' if OS == 'UNIX-LIKE'
                                                                                       else '.bat'))

                        with open(start_path, 'w+') as handle:
                            lines = []
                            if OS == 'UNIX-LIKE':
                                lines = [
                                    '#!/bin/bash\n',
                                    'cd {}\n'.format(sim_path if submission_context == 'cluster' else '.'),
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
                                    '-dll {}/MOD_Files/nrnmech.dll '
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
                            command = ' '.join([
                                'sbatch',
                                '--job-name={}'.format(job_name),
                                '--output={}'.format(output_log),
                                '--error={}'.format(error_log),
                                '--mem=8000',
                                '-p', 'wmglab',
                                '-c', '1',
                                start_path
                            ])
                            os.system(command)

                            # allow job to start before removing slurm file
                            time.sleep(1.0)

                            # remove start.slurm
                            os.remove(start_path)

                        elif submission_context == 'local':
                            local_args['start'] = start_path.split(os.path.sep)[-1]
                            local_args['output_log'] = os.path.join('logs', 'out', output_log.split(os.path.sep)[-1])
                            local_args['error_log'] = os.path.join('logs', 'err', error_log.split(os.path.sep)[-1])
                            local_args['sim_path'] = os.path.abspath(sim_path)
                            local_args_list.append(local_args.copy())

        local_args_lists.append(local_args_list)

    return local_args_lists


def local_submit(my_local_args):
    sim_path = my_local_args['sim_path']
    os.chdir(sim_path)

    start = my_local_args['start']
    out_filename = my_local_args['output_log']
    err_filename = my_local_args['error_log']

    if OS == 'UNIX-LIKE':
        run_command = ['bash', start, 'stdout', out_filename, 'stderr', err_filename, 'capture_output=True']
        p = subprocess.call(run_command)

    else:
        with open(out_filename, "w+") as fo, open(err_filename, "w+") as fe:
            p = subprocess.call([start], stdout=fo, stderr=fe)


def main():
    submit_lists = make_submission_list()
    for submit_list in submit_lists:
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        result = pool.map(local_submit, submit_list)


if __name__ == "__main__":  # Allows for the safe importing of the main module
    main()
