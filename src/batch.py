#!/usr/bin/env python

import json
import os
import re
import sys
import time

# os.system('module load Neuron/7.6.2')

if not os.path.exists(os.path.join('MOD_Files/x86_64')):
    os.chdir(os.path.join('MOD_Files'))
    os.system('nrnivmodl')
    os.chdir('..')

for run_number in sys.argv[1:]:
    # if not run_number.isnumeric():
    #     raise Exception(
    #         'Invalid argument: {}\n'
    #         'All arguments must be positive integers.'.format(run_number)
    #     )

    filename = os.path.join('runs', run_number + '.json')

    if not os.path.exists(filename):
        raise Exception('Invalid run number: {}'.format(run_number))

    with open(filename, 'r') as file:
        run = json.load(file)

        sample = run.get('sample')
        models = run.get('models')
        sims = run.get('sims')

        for model in models:
            for sim in sims:
                sim_dir = os.path.join('n_sims')
                sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

                for sim_name in [x for x in os.listdir(sim_dir) if sim_name_base in x]:
                    sim_path = os.path.join(sim_dir, sim_name)
                    fibers_path = os.path.join(sim_path, 'data', 'inputs')
                    output_path = os.path.join(sim_path, 'data', 'outputs')
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

                    print('\n\n################ {} ################\n\n'.format(sim_name))

                    for fiber_filename in [x for x in os.listdir(fibers_path)
                                           if re.match('inner[0-9]+_fiber[0-9]+\\.dat', x)]:
                        master_fiber_name = str(fiber_filename.split('.')[0])
                        inner_name, fiber_name = tuple(master_fiber_name.split('_'))
                        inner_ind = int(inner_name.split('inner')[-1])
                        fiber_ind = int(fiber_name.split('fiber')[-1])

                        thresh_path = os.path.join(output_path, 'thresh_inner{}_fiber{}.dat'.format(inner_ind, fiber_ind))
                        if os.path.exists(thresh_path):
                            print('Found {} -->\t\tskipping inner ({}) fiber ({})'.format(thresh_path, inner_ind, fiber_ind))
                            continue

                        # write start.slurm
                        start_path = os.path.join(sim_path, 'start.slurm')
                        if os.path.exists(start_path):
                            raise Exception('start.slurm already exists (not expected) check path/implementation')

                        stimamp_top = -10
                        stimamp_bottom = -0.01

                        with open(start_path, 'w') as handle:
                            lines = [
                                '#!/bin/bash\n',
                                'cd {}\n'.format(sim_path),
                                'cp -p ../../MOD_Files/x86_64/special .\n',
                                'chmod a+rwx special\n',
                                './special -nobanner blank.hoc '
                                '-c \"strdef sim_path\" '
                                '-c \"sim_path=\\\"{}\\\"\" '
                                '-c \"inner_ind={}\" '
                                '-c \"fiber_ind={}\" '
                                '-c \"stimamp_top={}\" '
                                '-c \"stimamp_bottom={}\" '
                                '-c \"load_file(\\\"launch.hoc\\\")\"\n'.format(sim_path,
                                                                                inner_ind,
                                                                                fiber_ind,
                                                                                stimamp_top,
                                                                                stimamp_bottom)
                            ]
                            handle.writelines(lines)

                        # submit batch job for fiber
                        job_name = '{}_{}'.format(sim_name, master_fiber_name)
                        print('\n{}'.format(job_name))

                        # TODO this will change for local running
                        command = ' '.join([ 
                            'sbatch',
                            '--job-name={}'.format(job_name),
                            '--output={}'.format(os.path.join(out_dir, '{}{}'.format(master_fiber_name, '.log'))),
                            '--error={}'.format(os.path.join(err_dir, '{}{}'.format(master_fiber_name, '.log'))),
                            '--mem=8000',
                            '-p', 'wmglab',
                            '-c', '1',
                            start_path
                        ])
                        os.system(command)

                        # allow job to start
                        time.sleep(2.0)

                        # remove start.slurm
                        os.remove(start_path)

                        # to not crash the scheduler
                        time.sleep(2.0)
