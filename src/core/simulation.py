#!/usr/bin/env python3.7

"""Defines Simulation class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""

import copy
import distutils.dir_util as du
import itertools
import json
import os
import pickle
import re
import shutil
import sys
import warnings
from typing import List, Tuple

import numpy as np
import scipy.interpolate as sci

from src.core import Sample
from src.utils import Config, Configurable, Env, Exceptionable, ExportMode, Saveable, SetupMode, WriteMode

from .fiberset import FiberSet
from .waveform import Waveform


class Simulation(Exceptionable, Configurable, Saveable):
    """Class for managing the simulation."""

    def __init__(self, sample: Sample, exception_config: list):
        """Initialize the simulation class.

        :param sample:  Sample object
        :param exception_config: list of exceptions to be thrown
        """
        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.waveforms = []
        self.fibersets = []
        self.ss_fibersets = []
        self.sample = sample
        self.factors = {}
        self.wave_product = []
        self.wave_key = []
        self.fiberset_product = []
        self.fiberset_key = []
        self.fiberset_map_pairs: List[Tuple[List, List]] = []
        self.ss_fiberset_map_pairs: List[Tuple[List, List]] = []
        self.src_product = []
        self.src_key = []
        self.potentials_product = []
        self.master_product_indices = []  # order: potentials (active_src, fiberset), waveform
        self.ss_product = []  # order: (contact index, fiberset)

    def load(self, path: str) -> 'Simulation':
        """Load a pickled object from a file.

        :param path: path to object file
        :return: loaded object
        """
        with open(path, 'rb') as f:
            return pickle.load(f)

    def load_json(self, config_path: str):
        """Load in json data and returns to user, assuming it has already been validated.

        :param config_path: the string path to load up
        :return: json data (usually dict or list)
        """
        with open(config_path, "r") as h:
            return json.load(h)

    def resolve_factors(self) -> 'Simulation':
        """Find the factors that are used in the simulation from fibers, waveform, and supersampled_bases.

        :return: self
        """
        if len(self.factors.items()) > 0:
            self.factors = {}

        def search(dictionary, path):
            """Search for a key in a dictionary with value that is a list.

            :param dictionary: dictionary that will be searched
            :param path: path to the key to search for
            :return: self with updated factors
            """
            for key, value in dictionary.items():
                if type(value) == list and len(value) > 1:
                    self.factors[path + '->' + key] = value
                elif type(value) == list and len(value) <= 1:
                    print("ERROR:", key, "is a list, but has length", len(value))
                    self.throw(137)
                elif type(value) == dict:
                    search(value, path + '->' + key)

        for flag in ['fibers', 'waveform', 'supersampled_bases']:
            if flag in self.configs[Config.SIM.value]:
                search(self.configs[Config.SIM.value][flag], flag)

        if len(self.factors.items()) != self.search(Config.SIM, "n_dimensions"):
            self.throw(106)

        return self

    def write_fibers(self, sim_directory: str) -> 'Simulation':
        """Write fibers to files for each FiberSet in the simulation and create the fiberset_product and fiberset_keys.

        :param sim_directory: directory of the simulation
        :return: self
        """
        fibersets_directory = os.path.join(sim_directory, 'fibersets')
        # loop PARAMS in here, but loop HISTOLOGY in FiberSet object
        if not os.path.exists(fibersets_directory):
            os.makedirs(fibersets_directory)

        fiberset_factors = {key: value for key, value in self.factors.items() if key.split('->')[0] == 'fibers'}

        self.fiberset_key = list(fiberset_factors.keys())

        self.fiberset_product = list(itertools.product(*fiberset_factors.values()))

        for i, fiberset_set in enumerate(self.fiberset_product):

            fiberset_directory = os.path.join(fibersets_directory, str(i))
            if not os.path.exists(fiberset_directory):
                os.makedirs(fiberset_directory)

            sim_copy = self._copy_and_edit_config(self.configs[Config.SIM.value], self.fiberset_key, list(fiberset_set))

            fiberset = FiberSet(self.sample, self.configs[Config.EXCEPTIONS.value])
            fiberset.add(SetupMode.OLD, Config.SIM, sim_copy).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).generate(
                sim_directory
            ).write(
                WriteMode.DATA, fiberset_directory
            )

            self.fiberset_map_pairs.append((fiberset.out_to_fib, fiberset.out_to_in))
            self.fibersets.append(fiberset)

        if 'supersampled_bases' not in self.configs[Config.SIM.value]:
            generate_ss_bases = False
        else:
            generate_ss_bases: bool = self.search(Config.SIM, 'supersampled_bases', 'generate')

        if not generate_ss_bases:
            pass

        else:

            ss_fibercoords_directory = os.path.join(sim_directory, 'ss_coords')

            if not os.path.exists(ss_fibercoords_directory):
                os.makedirs(ss_fibercoords_directory)

            fiberset = FiberSet(self.sample, self.configs[Config.EXCEPTIONS.value])
            fiberset.add(SetupMode.OLD, Config.SIM, self.configs[Config.SIM.value]).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).generate(
                sim_directory, super_sample=generate_ss_bases
            ).write(
                WriteMode.DATA, ss_fibercoords_directory
            )

            self.ss_fiberset_map_pairs.append((fiberset.out_to_fib, fiberset.out_to_in))
            self.ss_fibersets.append(fiberset)

        return self

    def write_waveforms(self, sim_directory: str) -> 'Simulation':
        """Write waveforms to files for each Waveform in the simulation. Create the waveform_product and waveform_keys.

        :param sim_directory:
        :return:
        """
        directory = os.path.join(sim_directory, 'waveforms')
        if not os.path.exists(directory):
            os.makedirs(directory)

        wave_factors = {key: value for key, value in self.factors.items() if key.split('->')[0] == 'waveform'}

        self.wave_key = list(wave_factors.keys())
        self.wave_product = list(itertools.product(*wave_factors.values()))

        for i, wave_set in enumerate(self.wave_product):
            sim_copy = self._copy_and_edit_config(self.configs[Config.SIM.value], self.wave_key, list(wave_set))

            waveform = Waveform(self.configs[Config.EXCEPTIONS.value])

            waveform.add(SetupMode.OLD, Config.SIM, sim_copy).add(
                SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]
            ).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).init_post_config().generate().write(
                WriteMode.DATA, os.path.join(directory, str(i))
            )
            path = sim_directory + f'/plots/waveforms/{i}.png'
            if not os.path.exists(sim_directory + '/plots/waveforms'):
                os.makedirs(sim_directory + '/plots/waveforms')

            waveform.plot(final=True, path=path)

            if self.search(Config.RUN, "popup_plots", optional=True) is True:
                waveform.plot(final=True, path=None)

            self.waveforms.append(waveform)

        return self

    def validate_srcs(self, sim_directory) -> 'Simulation':
        """Validate the active_srcs in the simulation config.

        :param sim_directory: Path to simulation directory
        :return: self
        """
        # potentials key (s) = (r x p)
        # index of line in output is s, write row containing of (r and p) to file

        # if active_srcs in sim config has key for the cuff in your model, use the list of contact weights
        cuff = self.search(Config.MODEL, "cuff", "preset")
        if cuff in self.configs[Config.SIM.value]["active_srcs"]:
            active_srcs_list = self.search(Config.SIM, "active_srcs", cuff)
        else:
            ss = self.search(Config.SIM, 'supersampled_bases', optional=True)
            if ss is not None and ss['use'] is True:
                self.throw(130)
            # otherwise, use the default weights (generally you don't want to rely on this as cuffs have different
            # numbers of contacts
            active_srcs_list = self.search(Config.SIM, "active_srcs", "default")
            print(f"\t\tWARNING: Attempting to use default value for active_srcs: {active_srcs_list}")

        #  loop over the contact weights, make sure the the values obey two rules:
        #      (1) current conservation
        #      (2) unitary amounts solved for bases in COMSOL: if n_srcs > 1 then sum(abs) = 2, sum = 0
        #                                                      if n_srcs = 1 then = 1 (special case)
        for active_srcs in active_srcs_list:
            active_src_abs = [abs(src_weight) for src_weight in active_srcs]
            if not all(abs(i) <= 1 for i in active_src_abs):
                self.throw(93)

            if len(active_srcs) == 1:
                if sum(active_srcs) not in [1, -1]:
                    self.throw(50)
            else:
                pass

        self.potentials_product = list(
            itertools.product(
                list(range(len(active_srcs_list))),
                list(range(len(self.fiberset_product))),
            )
        )

        self.ss_product = list(itertools.product(list(range(len(active_srcs_list[0]))), [0]))

        self.src_key = ['->'.join(['active_srcs', cuff])]
        self.src_product = active_srcs_list

        # loop over product
        output = [len(self.potentials_product)]
        for active_src_select, fiberset_select in self.potentials_product:
            output.append((active_src_select, fiberset_select))

        # write to file
        key_file_dir = os.path.join(sim_directory, "potentials")
        key_filepath = os.path.join(sim_directory, "potentials", "key.dat")
        if not os.path.exists(key_file_dir):
            os.makedirs(key_file_dir)

        with open(key_filepath, 'w') as f:
            for row in output:
                if not isinstance(row, int):
                    for el in row:
                        f.write(str(el) + ' ')
                else:
                    f.write(str(row) + ' ')
                f.write("\n")

        s_s = range(int(output[0]))
        q_s = range(len(self.wave_product))
        prods = list(itertools.product(s_s, q_s))
        self.master_product_indices = prods

        return self

    def validate_ss_dz(self, supersampled_bases, sim_dir):
        """Validate the ss_dz in the simulation. Make sure that the parent SS dz is the same as this one.

        :param supersampled_bases: information about the supersampled bases from Sim
        :param sim_dir: directory of the source simulation with previously supersampled bases
        :return: self
        """
        source_sim = supersampled_bases.get('source_sim')

        # check that dz in source_sim matches the dz (if provided) in current sim
        source_sim_obj_dir = os.path.join(sim_dir, str(source_sim))

        if not os.path.exists(source_sim_obj_dir):
            self.throw(94)

        source_sim_obj_file = os.path.join(source_sim_obj_dir, 'sim.obj')

        source_simulation: Simulation = self.load(source_sim_obj_file)

        source_dz = source_simulation.configs['sims']['supersampled_bases']['dz']

        if 'dz' in supersampled_bases:
            if supersampled_bases.get('dz') != source_dz:
                self.throw(79)
        elif 'dz' not in supersampled_bases:
            warnings.warn(f'dz not provided in Sim, so will accept dz={source_dz} specified in source Sim')

    def build_n_sims(self, sim_dir, sim_num) -> 'Simulation':
        """Set up the neuron simulation for the given simulation.

        :param sim_dir: directory of the simulation we are building n_sims for
        :param sim_num: index of the simulation we are building n_sims for
        :return: self
        """

        def make_inner_fiber_diam_key(my_fiberset_ind, my_nsim_inputs_directory, my_potentials_directory, my_file):
            """Make the key for the inner-fiber-diameter key file.

            :param my_fiberset_ind: index of the fiberset we are building the key for
            :param my_nsim_inputs_directory: directory of the nsim inputs
            :param my_potentials_directory: directory of the potentials
            :param my_file: file we are making
            """
            inner_fiber_diam_key = []
            diams = np.loadtxt(os.path.join(my_potentials_directory, my_file))
            for fiber_ind in range(len(diams)):
                diam = diams[fiber_ind]

                inner, fiber = self.indices_fib_to_n(my_fiberset_ind, fiber_ind)

                inner_fiber_diam_key.append((inner, fiber, diam))

            inner_fiber_diam_key_filename = os.path.join(nsim_inputs_directory, 'inner_fiber_diam_key.obj')
            with open(inner_fiber_diam_key_filename, 'wb') as f:
                pickle.dump(inner_fiber_diam_key, f)
                f.close()

        n_inners = 0
        for fascicle in self.sample.morphology['Fascicles']:
            n_inners += len(fascicle["inners"])

        n_fiber_coords = []
        for fiberset in self.fibersets:
            n_fiber_coords.append(len(fiberset.fibers[0]))

        for t, (potentials_ind, waveform_ind) in enumerate(self.master_product_indices):
            nsim_inputs_directory, fiberset_ind, active_src_vals = self.n_sim_setup(
                sim_dir, sim_num, potentials_ind, waveform_ind, t
            )
            # copy in potentials data into neuron simulation data/inputs folder
            # the potentials files are matched to their inner and fiber index, and saved in destination folder with
            # this naming convention... this allows for control of upper/lower bounds for thresholds by fascicle
            # (useful since within a fascicle thresholds should be similar)
            inner_list = []
            fiber_list = []

            supersampled_bases: dict = self.search(Config.SIM, 'supersampled_bases', optional=True)
            do_supersample: bool = supersampled_bases is not None and supersampled_bases.get('use') is True

            potentials_directory = os.path.join(sim_dir, str(sim_num), 'potentials', str(fiberset_ind))
            fiberset_directory = os.path.join(sim_dir, str(sim_num), 'fibersets', str(fiberset_ind))

            for root, _, files in os.walk(fiberset_directory):
                for file in files:
                    if re.match('[0-9]+\\.dat', file):

                        master_fiber_index = int(file.split('.')[0])

                        inner_index: int
                        fiber_index: int

                        inner_index, fiber_index = self.indices_fib_to_n(fiberset_ind, master_fiber_index)

                        filename_dat = f'inner{inner_index}_fiber{fiber_index}.dat'

                        if do_supersample:
                            # SUPER SAMPLING - PROBED COMSOL AT SS_COORDS --> /SS_BASES
                            self.validate_ss_dz(supersampled_bases, sim_dir)
                            source_sim = supersampled_bases.get('source_sim')
                            ss_bases = [None for _ in active_src_vals[0]]

                            ss_fiberset_path, ss_bases = self.get_ss_bases(
                                active_src_vals, file, sim_dir, source_sim, ss_bases
                            )

                            neuron_potentials_input = self.weight_potentials(
                                active_src_vals, file, root, ss_bases, ss_fiberset_path
                            )
                            np.savetxt(
                                os.path.join(nsim_inputs_directory, filename_dat),
                                neuron_potentials_input,
                                fmt='%0.18f',
                                header=str(len(neuron_potentials_input)),
                                comments='',
                            )
                        else:
                            # NOT SUPER SAMPLING - PROBED COMSOL AT /FIBERSETS --> /POTENTIALS
                            is_member = np.in1d(inner_index, inner_list)
                            if not is_member:
                                inner_list.append(inner_index)
                                if len(fiber_list) < len(inner_list):
                                    fiber_list.append(0)
                                fiber_list[inner_list.index(inner_index)] += 1
                            shutil.copyfile(
                                os.path.join(
                                    sim_dir,
                                    str(sim_num),
                                    'potentials',
                                    str(potentials_ind),
                                    str(fiber_index) + '.dat',
                                ),
                                os.path.join(nsim_inputs_directory, filename_dat),
                            )
                    elif file == 'diams.txt':
                        make_inner_fiber_diam_key(
                            fiberset_ind,
                            potentials_directory,
                            file,
                        )
        return self

    def get_ss_bases(self, active_src_vals, file, sim_dir, source_sim, ss_bases):
        """Get the supersampled bases for the given simulation.

        :param active_src_vals:
        :param file:
        :param sim_dir:
        :param source_sim:
        :param ss_bases:
        :return:
        """
        ss_fiberset_path = os.path.join(sim_dir, str(source_sim), 'ss_coords')

        for basis_ind in range(len(active_src_vals[0])):

            ss_bases_src_path = os.path.join(sim_dir, str(source_sim), 'ss_bases', str(basis_ind))

            if not os.path.exists(ss_bases_src_path):
                self.throw(81)

            if not os.path.exists(os.path.join(ss_bases_src_path, file)):
                self.throw(81)
            else:
                ss_bases[basis_ind] = np.loadtxt(os.path.join(ss_bases_src_path, file))[1:]

        return ss_fiberset_path, ss_bases

    def weight_potentials(self, active_src_vals, file, root, ss_bases, ss_fiberset_path):
        """Calculate the sum of weighted bases.

        :param active_src_vals:
        :param file:
        :param root:
        :param ss_bases:
        :param ss_fiberset_path:
        :return:
        """
        ss_weighted_bases_vec = np.zeros(len(ss_bases[0]))
        for src_ind, src_weight in enumerate(active_src_vals[0]):
            ss_weighted_bases_vec += ss_bases[src_ind] * src_weight
        # down-sample super_save_vec
        with open(os.path.join(root, file), 'r') as neuron_fiberset_file:
            neuron_fiberset_file_lines = neuron_fiberset_file.readlines()[1:]
            neuron_fiber_coords = []
            for neuron_fiberset_file_line in neuron_fiberset_file_lines:
                neuron_fiber_coords = np.append(
                    neuron_fiber_coords,
                    float(neuron_fiberset_file_line.split(' ')[-2]),
                )
        with open(os.path.join(ss_fiberset_path, file), 'r') as ss_fiberset_file:
            ss_fiberset_file_lines = ss_fiberset_file.readlines()[1:]
            ss_fiber_coords = []
            for ss_fiberset_file_line in ss_fiberset_file_lines:
                ss_fiber_coords = np.append(
                    ss_fiber_coords,
                    float(ss_fiberset_file_line.split(' ')[2]),
                )
        # create interpolation from super_coords and super_bases
        f = sci.interp1d(ss_fiber_coords, ss_weighted_bases_vec)
        neuron_potentials_input = f(neuron_fiber_coords)
        return neuron_potentials_input

    def indices_fib_to_n(self, fiberset_ind, fiber_ind) -> Tuple[int, int]:
        """Get inner and fiber indices from fiber index and fiberset_index.

        :param fiberset_ind: fiberset index
        :param fiber_ind: fiber index within fiberset
        :return: (l, k) as in "inner<l>_fiber<k>.dat" for NEURON sim
        """

        def search(arr, target) -> Tuple[int, int, int]:
            for a, outer in enumerate(arr):
                for b, inner in enumerate(outer):
                    for c, fib in enumerate(inner):
                        if fib == target:
                            return a, b, c

        out_fib, out_in = self.fiberset_map_pairs[fiberset_ind]
        i, j, k = search(out_fib, fiber_ind)
        return out_in[i][j], k

    def indices_n_to_fib(self, fiberset_index, inner_index, local_fiber_index) -> Tuple[int, int]:
        """Get fiber index from inner and local fiber indices.

        :param fiberset_index: fiberset index
        :param inner_index: inner index
        :param local_fiber_index: local fiber index
        :return: fiber index within fiberset
        """

        def search(arr, target) -> Tuple[int, int]:
            for a, outer in enumerate(arr):
                for b, inner in enumerate(outer):
                    if inner == target:
                        return a, b

        out_fib, out_in = self.fiberset_map_pairs[fiberset_index]
        i, j = search(out_in, inner_index)
        return out_fib[i][j][local_fiber_index]

    @staticmethod
    def _build_file_structure(sim_obj_dir, t):
        """Build the file structure for the simulation.

        :param sim_obj_dir:
        :param t: master production index
        :return: None
        """
        sim_dir = os.path.join(sim_obj_dir, "n_sims", str(t))

        if not os.path.exists(sim_dir):
            subfolder_names = ["inputs", "outputs"]
            for subfolder_name in subfolder_names:
                os.makedirs(os.path.join(sim_dir, "data", subfolder_name))

    def _copy_and_edit_config(self, config, key, setval, copy_again=True):
        """Copy the config file and edits the key to set.

        :param config: config file to copy
        :param key: key to edit/reduce
        :param param_list: list of parameters to set
        :param copy_again: make deep copy of config file
        :return: new (reduced) config file
        """
        cp = config
        if copy_again:
            cp = copy.deepcopy(config)

        for path, value in zip(key, list(setval)):
            path_parts = path.split('->')
            pointer = cp
            for path_part in path_parts[:-1]:
                pointer = pointer[path_part]
            pointer[path_parts[-1]] = value
        return cp

    @staticmethod
    def export_run(num: int, project_root: str, target: str, overwrite: bool = True):
        """Export the run config to the target directory.

        :param num: run number
        :param project_root: project root
        :param target:  target directory
        :param overwrite: overwrite existing run config if it exists
        :return: None
        """
        target_dir = os.path.join(target, 'runs')
        target_full = os.path.join(target_dir, str(num) + '.json')
        if overwrite and os.path.exists(target_full):
            os.remove(target_full)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        source = os.path.join(project_root, 'config', 'user', 'runs', str(num) + '.json')

        shutil.copy2(source, target_full)

    @staticmethod
    def export_n_sims(
        sample: int,
        model: int,
        sim: int,
        sim_obj_dir: str,
        target: str,
        export_behavior=None,
    ):
        """Export the n_sims to the target directory.

        :param sample: Sample index
        :param model: Model index
        :param sim: Sim index
        :param sim_obj_dir: Simulation object directory
        :param target: Target directory
        :param export_behavior: If the directory exists, what to do (i.e., override or error or skip
        :return: None
        """
        sim_dir = os.path.join(sim_obj_dir, str(sim), 'n_sims')
        sim_export_base = os.path.join(target, 'n_sims', f'{sample}_{model}_{sim}_')

        for product_index in [f for f in os.listdir(sim_dir) if os.path.isdir(os.path.join(sim_dir, f))]:
            target = sim_export_base + product_index

            if os.path.exists(target):
                if export_behavior == ExportMode.OVERWRITE.value:
                    shutil.rmtree(target)
                elif export_behavior == ExportMode.ERROR.value:
                    sys.exit(f'{target} already exists, exiting...')
                elif export_behavior == ExportMode.SELECTIVE.value or export_behavior is None:
                    print(f'\tSkipping n_sim export for {target} because folder already exists.')
                    continue
                else:
                    sys.exit('Invalid export_behavior')

            shutil.copytree(os.path.join(sim_dir, product_index), sim_export_base + product_index)

    @staticmethod
    def export_neuron_files(target: str):
        """Export the neuron files to the target directory.

        :param target: Target directory
        :return: None
        """
        # make NSIM_EXPORT_PATH (defined in Env.json) directory if it does not yet exist
        if not os.path.exists(target):
            os.makedirs(target)

        # neuron files
        try:
            du.copy_tree(
                os.path.join(os.environ[Env.PROJECT_PATH.value], 'src', 'neuron'),
                target,
            )
        except Exception:
            pass

        submit_target = os.path.join(target, 'submit.py')
        if os.path.isfile(submit_target):
            os.remove(submit_target)

        submit_source = os.path.join('src', 'neuron', 'submit.py')
        shutil.copy2(submit_source, submit_target)

    @staticmethod
    def export_system_config_files(target: str):
        """Export the system config files to the target directory.

        :param target: Target directory
        :return: None
        """
        # make NSIM_EXPORT_PATH (defined in Env.json) directory if it does not yet exist
        if not os.path.exists(target):
            os.makedirs(target)

        # fiber_z.json files
        shutil.copy2(
            os.path.join(os.environ[Env.PROJECT_PATH.value], 'config', 'system', 'fiber_z.json'),
            target,
        )
        shutil.copy2(
            os.path.join(
                os.environ[Env.PROJECT_PATH.value],
                'config',
                'system',
                'slurm_params.json',
            ),
            target,
        )

    @staticmethod
    def import_n_sims(
        sample: int,
        model: int,
        sim: int,
        sim_dir: str,
        source: str,
        delete: bool = False,
    ):
        """Import the n_sims from the submit directory.

        :param sample: Sample index
        :param model: Model index
        :param sim: Sim index
        :param sim_dir: Simulation directory
        :param source: Source directory (where n_sims are located)
        :param delete: Delete n_sims from source directory after import
        :return: None
        """
        print(f'sample: {sample}, model: {model}, sim: {sim}, sim_dir: {sim_dir}, source: {source}')

        sim_dir = os.path.join(sim_dir, 'n_sims')

        for dirname in [f for f in os.listdir(source) if os.path.isdir(os.path.join(source, f))]:
            this_sample, this_model, this_sim, product_index = tuple(dirname.split('_'))
            if sample == int(this_sample) and model == int(this_model) and sim == int(this_sim):
                if os.path.isdir(os.path.join(sim_dir, product_index)):
                    shutil.rmtree(os.path.join(sim_dir, product_index))
                shutil.copytree(os.path.join(source, dirname), os.path.join(sim_dir, product_index))
                if delete:
                    shutil.rmtree(os.path.join(source, dirname))

    @staticmethod
    def thresholds_exist(sample: int, model: int, sim: int, source: str):
        """Check if the thresholds exist in the source directory.

        :param sample: Sample index
        :param model: Model index
        :param sim: Sim index
        :param sim_dir: Simulation directory
        :param source: Source directory (where n_sims are located)
        :return: True if thresholds exist, False otherwise
        """
        allthresh = True
        for dirname in [f for f in os.listdir(source) if os.path.isdir(os.path.join(source, f))]:
            this_sample, this_model, this_sim, product_index = tuple(dirname.split('_'))
            if sample == int(this_sample) and model == int(this_model) and sim == int(this_sim):
                nsim_dir = os.path.join(source, dirname)
                outdir = os.path.join(nsim_dir, 'data', 'outputs')
                indir = os.path.join(nsim_dir, 'data', 'inputs')
                for file in [f for f in os.listdir(indir) if f.startswith('inner') and f.endswith('.dat')]:
                    if not os.path.exists(os.path.join(outdir, 'thresh_' + file)):
                        print(f"Missing threshold {os.path.join(outdir, 'thresh_' + file)}")
                        allthresh = False
        return allthresh

    @staticmethod
    def activations_exist(sample: int, model: int, sim: int, source: str, n_amps: int):
        """Check if the activations (Ap times) exist in the source directory.

        :param sample: Sample index
        :param model: Model index
        :param sim: Sim index
        :param source: Source directory (where n_sims are located)
        :param n_amps: Number of amplitudes that were simulated
        :return: True if activations exist, False otherwise
        """
        allamp = True
        for dirname in [f for f in os.listdir(source) if os.path.isdir(os.path.join(source, f))]:
            this_sample, this_model, this_sim, product_index = tuple(dirname.split('_'))
            if sample == int(this_sample) and model == int(this_model) and sim == int(this_sim):
                nsim_dir = os.path.join(source, dirname)
                outdir = os.path.join(nsim_dir, 'data', 'outputs')
                indir = os.path.join(nsim_dir, 'data', 'inputs')
                for file in [f for f in os.listdir(indir) if f.startswith('inner') and f.endswith('.dat')]:
                    for amp in range(n_amps):
                        target = os.path.join(outdir, 'activation_' + file.replace('.dat', f'_amp{amp}.dat'))
                        if not os.path.exists(target):
                            print(f'Missing finite amp {target}')
                            allamp = False
        return allamp

    def potentials_exist(self, sim_dir: str) -> bool:
        """Return bool deciding if potentials have already been written.

        :param sim_dir: directory of this simulation
        :return: boolean!
        """
        return all(os.path.exists(os.path.join(sim_dir, 'potentials', str(p))) for p, _ in self.master_product_indices)

    def ss_bases_exist(self, sim_dir: str) -> bool:
        """Return bool deciding if potentials have already been written.

        :param sim_dir: directory of this simulation
        :return: boolean!
        """
        return all(os.path.exists(os.path.join(sim_dir, 'ss_bases', str(basis))) for basis, _ in self.ss_product)
