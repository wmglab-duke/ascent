import sys
import argparse


class versionAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        from config.system import _version
        print('ASCENT version {}'.format(_version.__version__))
        sys.exit()


# Set up parser and top level args
parser = argparse.ArgumentParser(description='ASCENT: Automated Simulations to Characterize Electrical Nerve Thresholds')
# parser.add_argument('-s','--silent',action='store_true', help = 'silence printing')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose printing')
parser.add_argument('-V', '--version', action=versionAction, nargs=0, help='print version')
parser.add_argument('-l', '--list', choices=['runs', 'samples', 'sims'], help='List all available indices for the specified option')

# add subparsers
subparsers = parser.add_subparsers(help='which script to run', dest='script')
pipeline_parser = subparsers.add_parser('pipeline', help='main ASCENT pipeline')
install_parser = subparsers.add_parser('install', help='install ASCENT')
env_parser = subparsers.add_parser('env_setup', help='Set ASCENT environment variables')
cs_parser = subparsers.add_parser('clean_samples', help='Remove all files except those specified from Sample directories')
nsims_parser = subparsers.add_parser('import_n_sims', help='Move NEURON outputs into ASCENT directories for analysis')
mmg_parser = subparsers.add_parser('mock_morphology_generator', help='Generate mock morpology for an ASCENT run')
ts_parser = subparsers.add_parser('tidy_samples', help='Remove specified files from Sample directories')

# add subparser arguments
pipeline_parser.add_argument('run_indices', type=int, nargs='+', help='Space separated indices to run the pipeline over')
pipeline_parser.add_argument('-b', '--break-point', choices=["pre_geom_run", "post_geom_run", "pre_java", "post_mesh_distal", "pre_mesh_distal", "post_material_assign", "pre_loop_currents", "pre_mesh_proximal", "post_mesh_proximal", "pre_solve"], help='Point in pipeline to exit and continue to next run')
pipeline_parser.add_argument('-w', '--wait-for-license', type=float, help="Wait the specified number of hours for a comsol license to become available.")
pipeline_parser.add_argument('-P', '--partial-fem', choices=["cuff_only", "nerve_only"], help="Only generate the specified geometry.")
pipeline_parser.add_argument('-E', '--export-behavior', choices=["overwrite", "error", "selective"], help="Behavior if n_sim export encounters extant data. Default is selective.")
pipeline_parser.add_argument('-e', '--endo-only-solution', action='store_true', help="Store basis solutions for endoneurial geometry ONLY")
pipeline_parser.add_argument('-r', '--render_deform', action='store_true', help="Pop-up window will render deformation operations")
pipeline_parser.add_argument('-S', '--auto-submit', action='store_true', help="Automatically submit fibers after each run")
prog_group = pipeline_parser.add_mutually_exclusive_group()
prog_group.add_argument('-c', '--comsol-progress', action='store_true', help="Print COMSOL progress to stdout")
prog_group.add_argument('-C', '--comsol-progress-popup', action='store_true', help="Show COMSOL progress in a pop-up window")
ts_parser.add_argument('sample_indices', nargs='+', type=int, help='Space separated sample indices to tidy')
nsims_parser.add_argument('run_indices', nargs='+', type=int, help='Space separated run indices to import')
nsims_group = nsims_parser.add_mutually_exclusive_group()
nsims_group.add_argument('-f', '--force', action='store_true', help='Import n_sims even if all thresholds are not found')
nsims_group.add_argument('-D', '--delete-nsims', action='store_true', help='After importing delete n_sim folder from NSIM_EXPORT_PATH')
cs_parser.add_argument('sample_indices', nargs='+', type=int, help='Space separated sample indices to clean')
mmg_parser.add_argument('mock_sample_index', type=int, help='Mock Sample Index to generate')
install_parser.add_argument('--no-conda', action='store_true', help='Skip conda portion of installation')


def parse():
    """parse all args"""

    def g0(args, argstring):
        """checks that argument is greater than 0"""
        if hasattr(args, argstring) and getattr(args, argstring) != None and getattr(args, argstring) <= 0:
            sys.exit('Arguments for {} must be greater than 0'.format(argstring))

    # parse arguments
    args = parser.parse_args()
    g0(args, 'wait_for_license')

    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit()

    return args
