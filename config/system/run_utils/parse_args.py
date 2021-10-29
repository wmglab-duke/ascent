import sys
import os
import argparse

#Set up parser and top level args
parser = argparse.ArgumentParser(description='ASCENT: Automated Simulations to Characterize Electrical Nerve Thresholds')
# parser.add_argument('-s','--silent',action='store_true', help = 'silence printing')
parser.add_argument('-v','--verbose',action='store_true', help = 'verbose printing')

#add subparsers
subparsers = parser.add_subparsers(help = 'which script to run', dest='script')
pipeline_parser = subparsers.add_parser('pipeline', help = 'main ASCENT pipeline')
install_parser = subparsers.add_parser('install', help = 'install ASCENT')
env_parser = subparsers.add_parser('env_setup', help = 'Set ASCENT environment variables')
cs_parser = subparsers.add_parser('clean_samples', help = 'clean_samples')
nsims_parser = subparsers.add_parser('import_n_sims', help = 'nsims')
mmg_parser = subparsers.add_parser('mock_morphology_generator', help = 'mmg')
ts_parser = subparsers.add_parser('tidy_samples', help = 'tidy_samples')

#add subparser arguments
# pipeline_parser.add_argument('-w','--wait',dest='wait_time', help = 'wait the specified amount of time (hours) for an available COMSOL license')
pipeline_parser.add_argument('run_indices', nargs = '+', help = 'Space separated indices to run the pipeline over')
ts_parser.add_argument('sample_indices', nargs = '+',type=int, help = 'Space separated sample indices to tidy')
nsims_parser.add_argument('run_indices', nargs = '+',type=int, help = 'Space separated run indices to import')
cs_parser.add_argument('sample_indices', nargs = '+',type=int, help = 'Space separated sample indices to clean')
mmg_parser.add_argument('mock_sample_index',type=int, help = 'Mock Sample Index to generate')
install_parser.add_argument('--no-conda',action='store_true', help = 'Skip conda portion of installation')


def parse():
 
    #parse arguments
    args = parser.parse_args()
    
    if args.script is None: 
        parser.print_help()
        sys.exit()
    
    return args
