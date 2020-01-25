import copy
import os

import itertools
import shutil

import numpy as np

from .fiberset import FiberSet
from .waveform import Waveform
from src.core import Sample
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config, WriteMode


class Simulation(Exceptionable, Configurable, Saveable):

    def __init__(self, sample: Sample, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.sample = sample
        self.factors = dict()
        self.wave_product = []
        self.wave_key = []
        self.fiberset_product = []
        self.fiberset_key = []
        self.src_product = []
        self.master_product = []

    def resolve_factors(self) -> 'Simulation':

        if len(self.factors.items()) > 0:
            self.factors = dict()

        def search(dictionary, remaining_n_dims, path):
            if remaining_n_dims < 1:
                return
            for key, value in dictionary.items():
                if type(value) == list and len(value) > 1:
                    # print('adding key {} to sub {}'.format(key, sub))
                    self.factors[path + '.' + key] = value
                    remaining_n_dims -= 1
                elif type(value) == dict:
                    # print('recurse: {}'.format(value))
                    search(value, remaining_n_dims, path + '.' + key)

        for flag in ['fibers', 'waveform']:
            search(
                self.configs[Config.SIM.value][flag],
                self.search(Config.SIM, "n_dimensions"),
                flag
            )

        return self

    def write_fibers(self, sim_directory: str) -> 'Simulation':
        # loop PARAMS in here, but loop HISTOLOGY in FiberSet object
        # TODO: finish method!

        directory = os.path.join(sim_directory, 'fibers')
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.fibersets = []
        fiberset_factors = {key: value for key, value in self.factors.items() if key.split('.')[0] == 'fibers'}

        self.fiberset_key = list(fiberset_factors.keys())
        self.fiberset_product = list(itertools.product(*fiberset_factors.values()))

        for i, fiberset_set in enumerate(self.fiberset_product):

            fiberset_directory = os.path.join(directory, str(i))

            if not os.path.exists(fiberset_directory):
                os.makedirs(fiberset_directory)

            sim_copy = self._copy_and_edit_config(self.configs[Config.SIM.value], self.fiberset_key, list(fiberset_set))

            fiberset = FiberSet(self.sample, self.configs[Config.EXCEPTIONS.value])
            fiberset \
                .add(SetupMode.OLD, Config.SIM, sim_copy) \
                .add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]) \
                .generate() \
                .write(WriteMode.DATA, fiberset_directory)

            self.fibersets.append(fiberset)

        return self

    def write_waveforms(self, sim_directory: str) -> 'Simulation':
        directory = os.path.join(sim_directory, 'waveforms')
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.waveforms = []
        wave_factors = {key: value for key, value in self.factors.items() if key.split('.')[0] == 'waveform'}

        self.wave_key = list(wave_factors.keys())
        self.wave_product = list(itertools.product(*wave_factors.values()))

        for i, wave_set in enumerate(self.wave_product):

            sim_copy = self._copy_and_edit_config(self.configs[Config.SIM.value], self.wave_key, list(wave_set))

            # sim_copy = copy.deepcopy(self.configs[Config.SIM.value])
            # for path, value in zip(self.wave_key, list(wave_set)):
            #     path_parts = path.split('.')
            #     pointer = sim_copy
            #     for path_part in path_parts[:-1]:
            #         pointer = pointer[path_part]
            #     pointer[path_parts[-1]] = value

            waveform = Waveform(self.configs[Config.EXCEPTIONS.value])
            waveform \
                .add(SetupMode.OLD, Config.SIM, sim_copy) \
                .add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value]) \
                .init_post_config() \
                .generate() \
                .write(WriteMode.DATA, os.path.join(directory, str(i))) \
                # .plot()

            self.waveforms.append(waveform)

        # search(
        #     {key: value for key, value in self.configs[Config.SIM.value].items() if key in loopable},
        #     self.search(Config.SIM, "n_dimensions")
        # )

        return self

    def validate_srcs(self, sim_directory) -> 'Simulation':
        #  /potentials key (index ) - values pXsrcs
        # index of the line is s, write row containing of p and src index to file
        cuff = self.search(Config.MODEL, "cuff", "preset")
        if cuff in self.configs[Config.SIM.value]["active_srcs"].keys():
            active_srcs_list = self.search(Config.SIM, "active_srcs", cuff)

        else:
            active_srcs_list = self.search(Config.SIM, "active_srcs", "default")
            print("WARNING: Attempting to use default value for active_srcs: {}".format(active_srcs_list))

        for active_srcs in active_srcs_list:
            active_src_abs = [abs(src_weight) for src_weight in active_srcs]
            if len(active_srcs) == 1:
                if sum(active_srcs) is not 1:
                    self.throw(50)
            else:
                if sum(active_srcs) is not 0:
                    self.throw(49)
                if sum(active_src_abs) is not 2:
                    self.throw(50)

        potentials_product = list(itertools.product(list(enumerate(active_srcs_list)),
                                                    list(enumerate(self.fiberset_product))
                                                    ))

        # loop over product
        output = [len(potentials_product)]
        for (active_src_select, fiberset_select) in potentials_product:
            output.append((active_src_select[0], fiberset_select[0]))

        # write to file
        filepath = os.path.join(sim_directory, "potentials", "key.dat")

        with open(filepath, 'w') as f:
            for row in output:
                if not isinstance(row, int):
                    for el in row:
                        f.write(str(el)+' ')
                else:
                    f.write(str(row)+' ')
                f.write("\n")

        return self

    ############################

    def build_sims(self, sim_obj_dir) -> 'Simulation':
        # loop cartesian product
        s_s = [0, 1]
        r_s = [0, 1]

        prods = list(itertools.product(s_s, r_s))
        for t, prod in enumerate(prods):
            s = prod[0]
            source_potentials_dir = os.path.join(sim_obj_dir, "potentials", str(s))
            destination_potentials_dir = os.path.join(sim_obj_dir, str(t), "data", "inputs")

            r = prod[1]
            source_waveform_path = os.path.join(sim_obj_dir, "waveforms", "{}.dat".format(r))
            destination_waveform_path = os.path.join(sim_obj_dir, str(t), "data", "inputs", "waveform.dat")

            self._build_file_structure(sim_obj_dir, t)
            shutil.copyfile(source_waveform_path, destination_waveform_path)
            shutil.copytree(source_potentials_dir, destination_potentials_dir)
            # self._build_hoc()


        # build_file_structure()
        # build paths
        # build_hoc()
        # copy_trees()
        return self

    @staticmethod
    def _build_file_structure(sim_obj_dir, t):
        sim_dir = os.path.join(sim_obj_dir, str(t))

        if not os.path.exists(sim_dir):
            subfolder_names = ["inputs", "outputs"]
            for subfolder_name in subfolder_names:
                os.makedirs(os.path.join(sim_dir, "data", subfolder_name))

    @staticmethod
    def _copy_trees(self, trees=None):
        if trees is None:
            trees = ['potentials', 'waveforms']

    def _build_hoc(self):
        pass

    ############################

    def _copy_and_edit_config(self, config, key, set):
        cp = copy.deepcopy(config)
        for path, value in zip(key, list(set)):
            path_parts = path.split('.')
            pointer = cp
            for path_part in path_parts[:-1]:
                pointer = pointer[path_part]
            pointer[path_parts[-1]] = value
        return cp