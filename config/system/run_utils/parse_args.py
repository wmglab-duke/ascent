import sys
import os
import argparse

#Set up parser and top level args
parser = argparse.ArgumentParser(description='ASCENT: Automated Simulations to Characterize Electrical Nerve Thresholds')
# parser.add_argument('-s','--silent',action='store_true', help = 'silence printing')
parser.add_argument('-v','--verbose',action='store_true', help = 'verbose printing')
parser.add_argument('-l','--list',choices=['runs'],help='List all available indices for the specified option')

#add subparsers
subparsers = parser.add_subparsers(help = 'which script to run', dest='script')
pipeline_parser = subparsers.add_parser('pipeline', help = 'main ASCENT pipeline')
install_parser = subparsers.add_parser('install', help = 'install ASCENT')
env_parser = subparsers.add_parser('env_setup', help = 'Set ASCENT environment variables')
cs_parser = subparsers.add_parser('clean_samples', help = 'Remove all files except those specified from Sample directories')
nsims_parser = subparsers.add_parser('import_n_sims', help = 'Move NEURON outputs into ASCENT directories for analysis')
mmg_parser = subparsers.add_parser('mock_morphology_generator', help = 'Generate mock morpology for an ASCENT run')
ts_parser = subparsers.add_parser('tidy_samples', help = 'Remove specified files from Sample directories')

#add subparser arguments
pipeline_parser.add_argument('run_indices', nargs = '+', help = 'Space separated indices to run the pipeline over')
pipeline_parser.add_argument('-b','--break-point',choices = ["pre_geom_run","post_geom_run","pre_java","post_mesh_distal","pre_mesh_distal","post_material_assign","pre_loop_currents","pre_mesh_proximal","post_mesh_proximal"], help = 'Point in pipeline to exit and continue to next run')
pipeline_parser.add_argument('-w','--wait-for-license',type=float,help = "Wait the specified number of hours for a comsol license to become available.")
pipeline_parser.add_argument('-P','--partial-fem',choices = ["cuff_only","nerve_only"],help = "Only generate the specified geometry.")
ts_parser.add_argument('sample_indices', nargs = '+',type=int, help = 'Space separated sample indices to tidy')
nsims_parser.add_argument('run_indices', nargs = '+',type=int, help = 'Space separated run indices to import')
cs_parser.add_argument('sample_indices', nargs = '+',type=int, help = 'Space separated sample indices to clean')
mmg_parser.add_argument('mock_sample_index',type=int, help = 'Mock Sample Index to generate')
install_parser.add_argument('--no-conda',action='store_true', help = 'Skip conda portion of installation')


def parse():
    """parse all args"""
    
    def g0(args, argstring):
        """checks that argument is greater than 0"""
        if hasattr(args,argstring) and getattr(args,argstring)!=None and getattr(args,argstring)<=0:
            sys.exit('Arguments for {} must be greater than 0'.format(argstring))
    
    #parse arguments
    args = parser.parse_args()
    
    g0(args,'wait_for_license')
    
    if not len(sys.argv)>1:
        parser.print_help()
        sys.exit()

    return args

