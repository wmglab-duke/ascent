#!/usr/bin/env python3

import json
import os
import re
import subprocess
import sys
import time

my_n_sim_dest = '/work/wmglab/edm23/ascent'
print(my_n_sim_dest)
# TODO if this works, load this in from a file so user just sets it once and the code is universal

if not os.path.exists('MOD_Files/x86_64'):
    os.chdir('MOD_Files')
    os.system('module load Neuron/7.6.2')
    os.system('nrnivmodl')
    os.chdir('..')

for run_number in sys.argv[1:]:
    if not run_number.isnumeric():
        raise Exception(
            'Invalid argument: {}\n'
            'All arguments must be positive integers.'.format(run_number)
        )

    filename = os.path.join('runs', run_number + '.json')

    if not os.path.exists(filename):
        raise Exception('Invalid run number: {}'.format(run_number))

    with open(filename, 'r') as file:
        run: dict = json.load(file)

        sample = run.get('sample')
        models = run.get('models')
        sims = run.get('sims')

        for model in models:
            for sim in sims:
                sim_dir = os.path.join(my_n_sim_dest, 'n_sims')
                sim_name_base = '{}_{}_{}_'.format(sample, model, sim)

                for sim_name in [x for x in os.listdir(sim_dir) if sim_name_base in x]:
                    sim_path = os.path.join(sim_dir, sim_name)
                    fibers_path = os.path.join(sim_path, 'data', 'inputs')
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
                        # print('\t{}\t{}'.format(inner_ind, fiber_ind))

                        # write start.slurm
                        start_path = os.path.join(sim_path, 'start.slurm')
                        print(start_path)
                        if os.path.exists(start_path):
                            raise Exception('start.slurm already exists (not expected) check path/implementation')

                        stimamp_top = 0.1
                        stimamp_bottom = 0.01

                        with open(start_path, 'w') as handle:
                            lines = [
                                '#!/bin/bash\n',
                                'cd {}\n'.format(sim_path),
                                'cp -p ../../MOD_Files/x86_64/special .\n',
                                'chmod a+rwx special\n',
                                'mpirun -np 1 ./special -nobanner -mpi blank.hoc '
                                '-c \"inner_ind={}\" '
                                '-c \"fiber_ind={}\" '
                                '-c \"stimamp_top={}\" '
                                '-c \"stimamp_bottom={}\" '
                                '-c \"load_file(\\\"launch.hoc\\\")\"\n'.format(inner_ind,
                                                                                fiber_ind,
                                                                                stimamp_top,
                                                                                stimamp_bottom)
                            ]
                            handle.writelines(lines)

                        # submit batch job for fiber
                        command = [
                            'sbatch',
                            '--job-name={}_{}'.format(sim_name, master_fiber_name),
                            '--output={}'.format(os.path.join(out_dir, '{}{}'.format(master_fiber_name, '.log'))),
                            '--error={}'.format(os.path.join(err_dir, '{}{}'.format(master_fiber_name, '.log'))),
                            '--mem=8000',
                            '-p', 'wmglab',
                            '-c', '1',
                            start_path
                        ]
                        subprocess.call(command)

                        # remove start.slurm
                        os.remove(start_path)

                        # to not crash the scheduler
                        time.sleep(0.5)
