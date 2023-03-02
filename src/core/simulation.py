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
from src.utils import Config, Configurable, Env, ExportMode, IncompatibleParametersError, Saveable, SetupMode, WriteMode

from .fiberset import FiberSet
from .hocwriter import HocWriter
from .waveform import Waveform


def get_z_coords(root, file):
    """Get the z-coords for the fiber.

    :param root: root of the fiber file
    :param file: fiber file to get z-coords from
    :return: z-coords
    """
    with open(os.path.join(root, file), 'r') as coords_file:
        coords_file_lines = coords_file.readlines()[1:]
        coords = []
        for coords_file_line in coords_file_lines:
            coords = np.append(
                coords,
                float(coords_file_line.split(' ')[-2]),  # this is the z coord
            )
    return coords


class Simulation(Configurable, Saveable):
    """Class for managing the simulation."""

    def __init__(self, sample: Sample):
        """Initialize the simulation class.

        :param sample:  Sample object
        """
        # Initializes superclass
        Configurable.__init__(self)

        self.n_bases = None
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
        """Load in a simulation from a path.

        :param path: path to the Python object to load
        :return: Python object at path
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

        :raises ValueError: if n_dimensions in simulation does not match the number of looped parameters
        :return: Instance of Simulation
        """
        if len(self.factors.items()) > 0:
            self.factors = {}

        def search(dictionary, path):
            """Search for a key in a dictionary with value that is a list.

            :param dictionary: dictionary that will be searched
            :param path: path to the key to search for
            :raises ValueError: if any lists have length 1
            """
            for key, value in dictionary.items():
                if type(value) == list and len(value) > 1:
                    self.factors[path + '->' + key] = value
                elif type(value) == list and len(value) <= 1:
                    print("ERROR:", key, "is a list, but has length", len(value))
                    raise ValueError(
                        "If type list, loopable sim parameters must have length greater than 1. "
                        "For a single (non-looping) value, use a Double."
                    )
                elif type(value) == dict:
                    search(value, path + '->' + key)

        for flag in ['fibers', 'waveform', 'supersampled_bases']:
            if flag in self.configs[Config.SIM.value]:
                search(self.configs[Config.SIM.value][flag], flag)

        if len(self.factors.items()) != self.search(Config.SIM, "n_dimensions"):
            raise ValueError("sims->n_dimensions does not equal the number of parameter dimensions given in Sim")

        return self

    def write_fibers(self, sim_directory: str) -> 'Simulation':
        """Write fibers to files for each FiberSet in the simulation and create the fiberset_product and fiberset_keys.

        :param sim_directory: directory of the simulation
        :return: self
        """
        fibersets_directory = os.path.join(sim_directory, 'fibersets')
        # loop PARAMS in here, but loop HISTOLOGY in FiberSet object
        os.makedirs(fibersets_directory, exist_ok=True)

        fiberset_factors = {key: value for key, value in self.factors.items() if key.split('->')[0] == 'fibers'}

        self.fiberset_key = list(fiberset_factors.keys())

        self.fiberset_product = list(itertools.product(*fiberset_factors.values()))

        for i, fiberset_set in enumerate(self.fiberset_product):
            fiberset_directory = os.path.join(fibersets_directory, str(i))
            os.makedirs(fibersets_directory, exist_ok=True)

            sim_copy = self._copy_and_edit_config(self.configs[Config.SIM.value], self.fiberset_key, list(fiberset_set))

            fiberset = FiberSet(self.sample)
            fiberset.add(SetupMode.OLD, Config.SIM, sim_copy).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).generate(
                sim_directory, super_sample=False
            ).write(
                WriteMode.DATA, fiberset_directory
            )

            self.fiberset_map_pairs.append((fiberset.out_to_fib, fiberset.out_to_in))
            self.fibersets.append(fiberset)

        if self.search(Config.SIM, 'supersampled_bases', 'generate', optional=True):
            ss_fibercoords_directory = os.path.join(sim_directory, 'ss_coords')
            os.makedirs(ss_fibercoords_directory, exist_ok=True)

            fiberset = FiberSet(self.sample)
            fiberset.add(SetupMode.OLD, Config.SIM, self.configs[Config.SIM.value]).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).generate(
                sim_directory, super_sample=True
            ).write(
                WriteMode.DATA, ss_fibercoords_directory
            )

            self.ss_fiberset_map_pairs.append((fiberset.out_to_fib, fiberset.out_to_in))
            self.ss_fibersets.append(fiberset)

        return self

    def interpolate_2d(self, down_coords, super_coords, data_vector):
        """Interpolate the data vector onto the down-sampled coords to match section in NEURON.

        :param down_coords: down-sampled coords
        :param super_coords: super-sampled coords
        :param data_vector: data vector to interpolate
        :return: interpolated data vector at down-sampled coords
        """
        f = sci.interp1d(super_coords, data_vector)
        output = f(down_coords)

        return output

    def write_waveforms(self, sim_directory: str) -> 'Simulation':
        """Write waveforms to files for each Waveform in the simulation. Create the waveform_product and waveform_keys.

        :param sim_directory: directory of the simulation
        :return: self
        """
        directory = os.path.join(sim_directory, 'waveforms')
        os.makedirs(directory, exist_ok=True)

        wave_factors = {key: value for key, value in self.factors.items() if key.split('->')[0] == 'waveform'}

        self.wave_key = list(wave_factors.keys())
        self.wave_product = list(itertools.product(*wave_factors.values()))

        for i, wave_set in enumerate(self.wave_product):
            sim_copy = self._copy_and_edit_config(self.configs[Config.SIM.value], self.wave_key, list(wave_set))

            waveform = Waveform()

            waveform.add(SetupMode.OLD, Config.SIM, sim_copy).add(
                SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]
            ).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).init_post_config().generate().write(
                WriteMode.DATA, os.path.join(directory, str(i))
            )
            path = sim_directory + f'/plots/waveforms/{i}.png'
            os.makedirs(sim_directory + '/plots/waveforms', exist_ok=True)

            waveform.plot(final=True, path=path)

            if self.search(Config.RUN, "popup_plots", optional=True) is True:
                waveform.plot(final=True, path=None)

            self.waveforms.append(waveform)

        return self

    def validate_srcs(self, sim_directory) -> 'Simulation':
        """Validate the active_srcs in the simulation config.

        :param sim_directory: Path to simulation directory
        :raises IncompatibleParametersError: if supersampling and active_srcs is default
        :raises ValueError: if any active_srcs include a value greater than 1 or less than -1
        :raises ValueError: if active_srcs do not abide by unitary constraints
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
                raise IncompatibleParametersError(
                    "Using default active_srcs is not allowed when running supersampled bases"
                )
            # otherwise, use the default weights (generally you don't want to rely on this as cuffs have different
            # numbers of contacts
            active_srcs_list = self.search(Config.SIM, "active_srcs", "default")
            print(f"\t\tWARNING: Attempting to use default value for active_srcs: {active_srcs_list}")

        self.src_product = active_srcs_list

        #  loop over the contact weights, make sure the values obey two rules:
        #      (1) current conservation
        #      (2) unitary amounts solved for bases in COMSOL: if n_srcs > 1 then sum(abs) = 2, sum = 0
        #                                                      if n_srcs = 1 then = 1 (special case)
        for active_srcs in active_srcs_list:
            active_src_abs = [abs(src_weight) for src_weight in active_srcs]
            if not all(abs(i) <= 1 for i in active_src_abs):
                raise ValueError(
                    "Contact weight in Sim (active_srcs) is greater than +1 or less than -1 which is not allowed"
                )

            if len(active_srcs) == 1 and sum(active_srcs) not in [1, -1]:
                raise ValueError("active_srcs_list provided does not abide by unitary current input response")

        self.n_bases = len(active_srcs_list[0])

        self.potentials_product = list(
            itertools.product(
                list(range(len(active_srcs_list))),
                list(range(len(self.fiberset_product))),
            )
        )

        self.src_key = ['->'.join(['active_srcs', cuff])]

        # loop over product
        output = [len(self.potentials_product)]
        for active_src_select, fiberset_select in self.potentials_product:
            output.append((active_src_select, fiberset_select))

        s_s = range(len(self.potentials_product))
        q_s = range(len(self.wave_product))
        prods = list(itertools.product(s_s, q_s))
        self.master_product_indices = prods

        return self

    def n_sim_setup(self, potentials_ind, sim_dir, sim_num, t, waveform_ind):
        """Set up the neuron simulation directory and the inputs for the simulation.

        :param potentials_ind: indices of the potentials to use in the simulation
        :param sim_dir: directory of the simulation
        :param sim_num: index of the Sim
        :param t: master product index
        :param waveform_ind: index of the waveform to use in the simulation
        :return: active_src_vals, active_rec_vals, fiberset_ind, nsim_inputs_directory
        """
        # build file structure sim/#/n_sims/t/data/(inputs and outputs)
        self._build_file_structure(os.path.join(sim_dir, str(sim_num)), t)
        nsim_inputs_directory = os.path.join(sim_dir, str(sim_num), 'n_sims', str(t), 'data', 'inputs')
        # copy corresponding waveform to sim/#/n_sims/t/data/inputs
        source_waveform_path = os.path.join(sim_dir, str(sim_num), "waveforms", f"{waveform_ind}.dat")
        destination_waveform_path = os.path.join(
            sim_dir, str(sim_num), "n_sims", str(t), "data", "inputs", "waveform.dat"
        )
        if not os.path.isfile(destination_waveform_path):
            shutil.copyfile(source_waveform_path, destination_waveform_path)
        # get source, waveform, and fiberset values for the corresponding neuron simulation t
        active_src_ind, fiberset_ind = self.potentials_product[potentials_ind]
        active_src_vals = [self.src_product[active_src_ind]]
        wave_vals = self.wave_product[waveform_ind]
        fiberset_vals = self.fiberset_product[fiberset_ind]
        # pare down simulation config to no lists of parameters (corresponding to the neuron simulation index t)
        sim_copy = self._copy_and_edit_config(
            self.configs[Config.SIM.value], self.src_key, active_src_vals, copy_again=False
        )
        sim_copy = self._copy_and_edit_config(sim_copy, self.wave_key, wave_vals, copy_again=False)
        sim_copy = self._copy_and_edit_config(sim_copy, self.fiberset_key, fiberset_vals, copy_again=False)
        # save the paired down simulation config to its corresponding neuron simulation t folder
        with open(os.path.join(sim_dir, str(sim_num), "n_sims", str(t), f"{t}.json"), "w") as handle:
            handle.write(json.dumps(sim_copy, indent=2))
        n_tsteps = len(self.waveforms[waveform_ind].wave)
        # add config and write launch.hoc
        n_sim_dir = os.path.join(sim_dir, str(sim_num), "n_sims", str(t))
        hocwriter = HocWriter(os.path.join(sim_dir, str(sim_num)), n_sim_dir)
        hocwriter.add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]).add(
            SetupMode.OLD, Config.SIM, sim_copy
        ).add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]).build_hoc(n_tsteps)
        return active_src_vals[0], fiberset_ind, nsim_inputs_directory

    def get_bases(self, file: str, sim_dir: str, source_sim: int, fiberset_ind: int = None):
        """Get the bases potentials for the simulation, and the corresponding fiberset/ss coords.

        :param file: fiber file get bases from
        :param sim_dir: directory of the simulation
        :param source_sim: index of the source simulation from which the bases are taken
        :param fiberset_ind: index of the fiberset
        :raises ValueError: if the bases file or folder does not exist
        :return: coords, bases
        """
        bases = [None for _ in range(self.n_bases)]
        for basis_ind in range(self.n_bases):
            if fiberset_ind is not None:
                # NOT super sampled bases
                bases_path = os.path.join(
                    sim_dir, str(source_sim), 'fibersets_bases', str(fiberset_ind), str(basis_ind)
                )
                coords_path = os.path.join(sim_dir, str(source_sim), 'fibersets', str(fiberset_ind))
            else:
                # YES super sampled bases
                bases_path = os.path.join(sim_dir, str(source_sim), 'ss_bases', str(basis_ind))
                coords_path = os.path.join(sim_dir, str(source_sim), 'ss_coords')

            if not os.path.exists(bases_path):
                raise ValueError(f"bases_path {bases_path} does not exist")

            if not os.path.exists(os.path.join(bases_path, file)):
                raise ValueError(f"bases_path {os.path.join(bases_path, file)} does not exist")
            else:
                bases[basis_ind] = np.loadtxt(os.path.join(bases_path, file))[1:]

        return coords_path, bases

    def validate_ss_dz(self, supersampled_bases, sim_dir):
        """Validate the ss_dz in the simulation. Make sure that the parent SS dz is the same as this one.

        :param supersampled_bases: information about the supersampled bases from Sim
        :param sim_dir: directory of the source simulation with previously supersampled bases
        :raises FileNotFoundError: if the supersampled source sim is not found
        :raises ValueError: if the supersampled source sim has a different ss_dz
        :return: None
        """
        source_sim = supersampled_bases.get('source_sim')

        # check that dz in source_sim matches the dz (if provided) in current sim
        source_sim_obj_dir = os.path.join(sim_dir, str(source_sim))

        if not os.path.exists(source_sim_obj_dir):
            raise FileNotFoundError(
                "Source Sim (i.e. source_sim in Sim->supersampled_bases) does not exist. "
                "Either set proper source_sim that has your previously supersampled potentials or set use to false."
            )

        source_sim_obj_file = os.path.join(source_sim_obj_dir, 'sim.obj')

        source_simulation: Simulation = self.load(source_sim_obj_file)

        source_dz = source_simulation.configs['sims']['supersampled_bases']['dz']

        if 'dz' in supersampled_bases:
            if supersampled_bases.get('dz') != source_dz:
                raise ValueError("Supersampling dz does not match source simulation dz")
        elif 'dz' not in supersampled_bases:
            warnings.warn(
                f'dz not provided in Sim, so will accept dz={source_dz} specified in source Sim', stacklevel=2
            )

        return self

    def build_n_sims(self, sim_dir, sim_num) -> 'Simulation':
        """Set up the neuron simulation for the given simulation.

        :param sim_dir: directory of the simulation we are building n_sims for
        :param sim_num: index of the simulation we are building n_sims for
        :return: self
        """

        def make_inner_fiber_diam_key(my_fiberset_ind, my_nsim_inputs_directory, my_potentials_directory, my_file):
            """Make the key for the inner-fiber-diameter key file.

            :param my_fiberset_ind: index of the fiberset
            :param my_nsim_inputs_directory: directory of the neuron simulation inputs
            :param my_potentials_directory: directory of the potentials
            :param my_file: file we are making
            :return: None
            """
            inner_fiber_diam_key = []
            diams = np.loadtxt(os.path.join(my_potentials_directory, my_file), unpack=True)
            for fiber_ind in range(diams.size):
                diam = diams[fiber_ind]

                inner, fiber = self.indices_fib_to_n(my_fiberset_ind, fiber_ind)

                inner_fiber_diam_key.append((inner, fiber, diam))

            inner_fiber_diam_key_filename = os.path.join(my_nsim_inputs_directory, 'inner_fiber_diam_key.obj')
            with open(inner_fiber_diam_key_filename, 'wb') as f:
                pickle.dump(inner_fiber_diam_key, f)
                f.close()

            return None

        supersampled_bases: dict = self.search(Config.SIM, 'supersampled_bases', optional=True)
        do_supersample: bool = supersampled_bases is not None and supersampled_bases.get('use') is True

        for t, (potentials_ind, waveform_ind) in enumerate(self.master_product_indices):
            active_src_vals, fiberset_ind, nsim_inputs_directory = self.n_sim_setup(
                potentials_ind, sim_dir, sim_num, t, waveform_ind
            )

            src_bases_indices = self.srcs_mapping(sim_dir)

            fiberset_directory = os.path.join(sim_dir, str(sim_num), 'fibersets', str(fiberset_ind))

            for fname_prefix, weights, bases_indices in zip([''], [active_src_vals], [src_bases_indices]):
                if not any(np.isnan(weights)):
                    # get the weights in order of the bases,
                    # since the weights are for a single cuff, but the bases span cuffs
                    all_weights = list(np.zeros(self.n_bases))
                    for i, basis_index in enumerate(bases_indices):
                        all_weights[basis_index] = weights[i]

                    for root, _, files in os.walk(fiberset_directory):
                        for file in files:
                            if re.match('[0-9]+\\.dat', file):
                                master_fiber_index = int(file.split('.')[0])
                                inner_index, fiber_index = self.indices_fib_to_n(fiberset_ind, master_fiber_index)
                                filename_dat = f'{fname_prefix}inner{inner_index}_fiber{fiber_index}.dat'

                                if not do_supersample:
                                    # getting potentials from fibersets_bases
                                    # fibersets_bases\<fiberset_index>\<basis_index>\<fibers>
                                    _, bases = self.get_bases(file, sim_dir, sim_num, fiberset_ind)
                                    neuron_potentials_input = self.weight_bases(all_weights, bases)

                                else:
                                    # getting potentials from supersampled bases
                                    # ss_bases\<basis_index>\<fibers>
                                    self.validate_ss_dz(supersampled_bases, sim_dir)
                                    source_sim = supersampled_bases.get('source_sim')
                                    ss_coords_root, ss_bases = self.get_bases(file, sim_dir, source_sim)
                                    weighted_ss_bases = self.weight_bases(all_weights, ss_bases)
                                    fiber_coords = get_z_coords(root, file)
                                    ss_coords = get_z_coords(ss_coords_root, file)
                                    neuron_potentials_input = self.interpolate_2d(
                                        fiber_coords, ss_coords, weighted_ss_bases
                                    )

                                np.savetxt(
                                    os.path.join(nsim_inputs_directory, filename_dat),
                                    neuron_potentials_input,
                                    fmt='%0.18f',
                                    header=str(len(neuron_potentials_input)),
                                    comments='',
                                )
                            elif file == 'diams.txt':
                                make_inner_fiber_diam_key(
                                    fiberset_ind,
                                    nsim_inputs_directory,
                                    fiberset_directory,
                                    file,
                                )

        return self

    def srcs_mapping(self, sim_dir):
        """Get the bases indices of the sources contacts for the simulation from COMSOL's Identifier Manager.

        :param sim_dir: directory of the simulation
        :return: recording bases indices, sources bases indices
        """
        # using the cuff indices in Sim, what are the bases files using the cuff_indexes saved in im.json?
        im_path = os.path.join(os.path.split(sim_dir)[0], 'mesh', 'im.json')
        im_config = self.load_json(im_path)

        src_bases_indices = []
        current_ids = im_config['currentIDs']
        for c_id in current_ids.keys():
            src_bases_indices.append(int(c_id) - 1)

        src_bases_indices.sort()

        return src_bases_indices

    def get_ss_bases(self, active_src_vals, file, sim_dir, source_sim, ss_bases):
        """Get the supersampled bases for the given simulation.

        :param active_src_vals: active source values (weights)
        :param file: file we are getting the supersampled bases from
        :param sim_dir: directory of simulations
        :param source_sim: source simulation index where the supersampled bases are from
        :param ss_bases: supersampled bases values
        :raises FileNotFoundError: if the supersampled potentials are not found
        :return: the path to the supersampled bases coordinates, ss_bases
        """
        ss_fiberset_path = os.path.join(sim_dir, str(source_sim), 'ss_coords')

        for basis_ind in range(len(active_src_vals[0])):
            ss_bases_src_path = os.path.join(sim_dir, str(source_sim), 'ss_bases', str(basis_ind))

            if not os.path.exists(ss_bases_src_path) or not os.path.exists(os.path.join(ss_bases_src_path, file)):
                raise FileNotFoundError(
                    "Trying to use super-sampled potentials that do not exist. "
                    "(hint: check that if 'use' is true 'generate' was also true for the source Sim)."
                )
            else:
                ss_bases[basis_ind] = np.loadtxt(os.path.join(ss_bases_src_path, file))[1:]

        return ss_fiberset_path, ss_bases

    def weight_bases(self, weights, bases):
        """Weight the bases.

        :param weights: weights to weight the bases with (defined in Sim Config active_srcs, active_recs)
        :param bases: vector of bases to weight for each active source/rec
        :return: weighted bases
        """
        weighted_potentials = np.zeros(len(bases[0]))
        for src_ind, src_weight in enumerate(weights):
            weighted_potentials += bases[src_ind] * src_weight

        return weighted_potentials

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

        :param sim_obj_dir: simulation object directory for sim in question
        :param t: master production index
        """
        sim_dir = os.path.join(sim_obj_dir, "n_sims", str(t))

        if not os.path.exists(sim_dir):
            subfolder_names = ["inputs", "outputs"]
            for subfolder_name in subfolder_names:
                os.makedirs(os.path.join(sim_dir, "data", subfolder_name))

    def _copy_and_edit_config(self, config, key, param_list, copy_again=True):
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

        for path, value in zip(key, list(param_list)):
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
        """
        target_dir = os.path.join(target, 'runs')
        target_full = os.path.join(target_dir, str(num) + '.json')
        if overwrite and os.path.exists(target_full):
            os.remove(target_full)

        os.makedirs(target_dir, exist_ok=True)

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
        """
        # make NSIM_EXPORT_PATH (defined in Env.json) directory if it does not yet exist
        os.makedirs(target, exist_ok=True)

        # neuron files
        du.copy_tree(
            os.path.join(os.environ[Env.PROJECT_PATH.value], 'src', 'neuron'),
            target,
        )

        submit_target = os.path.join(target, 'submit.py')
        if os.path.isfile(submit_target):
            os.remove(submit_target)

        submit_source = os.path.join('src', 'neuron', 'submit.py')
        shutil.copy2(submit_source, submit_target)

    @staticmethod
    def export_system_config_files(target: str):
        """Export the system config files to the target directory.

        :param target: Target directory
        """
        # make NSIM_EXPORT_PATH (defined in Env.json) directory if it does not yet exist
        os.makedirs(target, exist_ok=True)

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
    def activations_exist(sample: int, model: int, sim: int, sim_dir: str, source: str, n_amps: int):
        """Check if the activations (Ap times) exist in the source directory.

        :param sim_dir: Simulation directory
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

    def bases_potentials_exist(self, sim_dir: str) -> bool:
        """Return bool deciding if fibersets bases potentials have already been written for each fiberset.

        :param sim_dir: directory of this simulation
        :return: True if bases potentials exist, False otherwise
        """
        return all(
            os.path.exists(os.path.join(sim_dir, 'fibersets_bases', str(fiberset_ind), str(basis)))
            for fiberset_ind, basis in list(itertools.product(range(len(self.fiberset_product)), range(self.n_bases)))
        )

    def ss_bases_exist(self, sim_dir: str) -> bool:
        """Return bool deciding if super sampled potentials have already been written.

        :param sim_dir: directory of this simulation
        :return: True if ss bases exist, False otherwise
        """
        return all(os.path.exists(os.path.join(sim_dir, 'ss_bases', str(basis))) for basis in range(self.n_bases))
