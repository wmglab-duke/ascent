import copy
import os

import itertools
import shutil

import numpy as np

from .fiberset import FiberSet
from .waveform import Waveform
from src.core import Sample
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config, WriteMode, enums


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
        self.master_product_indices = []

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

        directory = os.path.join(sim_directory, 'fibersets')
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

        potentials_product = list(itertools.product(
            list(enumerate(active_srcs_list)),
            list(enumerate(self.fiberset_product))
        ))

        # loop over product
        output = [len(potentials_product)]
        for (active_src_select, fiberset_select) in potentials_product:
            output.append((active_src_select[0], fiberset_select[0]))

        # write to file
        key_file_dir = os.path.join(sim_directory, "potentials")
        key_filepath = os.path.join(sim_directory, "potentials", "key.dat")
        if not os.path.exists(key_file_dir):
            os.mkdir(key_file_dir)

        with open(key_filepath, 'w') as f:
            for row in output:
                if not isinstance(row, int):
                    for el in row:
                        f.write(str(el)+' ')
                else:
                    f.write(str(row)+' ')
                f.write("\n")

        return self

    ############################

    def build_sims(self, sim_dir) -> 'Simulation':
        # loop cartesian product

        key_filepath = os.path.join(sim_dir, "potentials", "key.dat")  # s is line number
        f = open(key_filepath, "r")
        contents = f.read()
        s_s = range(int(contents[0])-1)
        q_s = range(len(self.wave_product))

        prods = list(itertools.product(s_s, q_s))
        self.master_product_indices = prods
        for t, prod in enumerate(prods):
            s = prod[0]
            source_potentials_dir = os.path.join(sim_dir, "potentials", str(s))
            destination_potentials_dir = os.path.join(sim_dir, "n_sims", str(t), "data", "inputs")

            q = prod[1]
            source_waveform_path = os.path.join(sim_dir, "waveforms", "{}.dat".format(q))
            destination_waveform_path = os.path.join(sim_dir, "n_sims", str(t), "data", "inputs", "waveform.dat")

            self._build_file_structure(sim_dir, t)

            if not os.path.exists(destination_potentials_dir):
                os.makedirs(destination_potentials_dir)

            for root, dirs, files in os.walk(source_potentials_dir):
                for file in files:
                    shutil.copyfile(os.path.join(root, file), os.path.join(destination_potentials_dir, file))

            if not os.path.isfile(destination_waveform_path):
                shutil.copyfile(source_waveform_path, destination_waveform_path)
            # self._build_hoc(sim_obj_dir)


        # build_file_structure()
        # build paths
        # build_hoc()
        # copy_trees()
        return self

    @staticmethod
    def _build_file_structure(sim_obj_dir, t):
        sim_dir = os.path.join(sim_obj_dir, "n_sims", str(t))

        if not os.path.exists(sim_dir):
            subfolder_names = ["inputs", "outputs"]
            for subfolder_name in subfolder_names:
                os.makedirs(os.path.join(sim_dir, "data", subfolder_name))

    def _build_hoc(self, sim_obj_dir):
        """
        Write file LaunchSim###.hoc
        :return:
        """

        write_mode = WriteMode.HOC
        file_path = os.path.join(sim_obj_dir, "launch{}".format(WriteMode.file_endings.value[write_mode.value]))
        file_object = open(file_path, "w")

        # ENVIRONMENT
        file_object.write("\n//***************** Environment *****************\n")
        file_object.write("celsius   = %0.0f // [degC]\n" % self.search(Config.MODEL, "temperature", "value"))

        # TIME PARAMETERS
        file_object.write("\n//***************** Global Time ******************\n")
        #  extracellular_stim dict TODO
        extracellular_stim: dict = self.search(Config.SIM, "waveform", "global")
        dt = extracellular_stim.get("dt")
        file_object.write("dt        = %0.3f // [ms]\n" % dt)
        tstop = extracellular_stim.get("stop")
        file_object.write("tstop     = %0.0f // [ms]\n" % tstop)
        n_tsteps = np.math.floor(tstop / dt) + 1
        file_object.write("n_tsteps  = %0.0f // [unitless]\n" % n_tsteps)
        file_object.write("t_initSS  = %0.0f // [ms]\n" % extracellular_stim.get("initSS"))
        file_object.write("dt_initSS = %0.0f // [ms]\n" % extracellular_stim.get("dt_initSS"))

        # FIBER PARAMETERS
        file_object.write("\n//***************** Fiber Parameters *************\n")
        #  fiber model dict TODO
        fibers: dict = self.search(Config.SIM, "fibers")
        fiber_model = fibers.get("type")

        fiber_model_info: dict = self.search(Config.FIBER_Z, Config.MyelinationMode.parameters.value, fiber_model)

        file_object.write("fiber_type = %0.0f "
                          "// fiber_type = 1 for unmyelinated; fiber_type = 2 for myelinated; "
                          "fiber_type = 3 for c fiber built from cFiberBuilder.hoc\n"
                          % fiber_model_info.get("fiber_type"))

        file_object.write("strdef fiber_type_str\n")
        file_object.write("fiber_type_str = \"%s\"\n" %
                          fiber_model_info.get("fiber_type_str"))

        file_object.write("node_channels = %0.0f "
                          "// node_channels = 0 for MRG; node_channels = 1 for Schild 1994\n" %
                          fiber_model_info.get("node_channels"))

        axonnodes = 9999999  # TODO, what is the dimension in fiber manager
        file_object.write("axonnodes = %0.0f "
                          "// must match up with ExtractPotentials\n" % axonnodes)

        file_object.write("passive_end_nodes = %0.0f "
                          "// passive_end_nodes = 1 to make both end nodes passive; 0 otherwise\n" %
                          fiber_model_info.get("passive_end_nodes"))

        fiberD = self.search(Config.SIM, "fibers", "diameter")
        file_object.write("fiberD = %0.0f "
                          "// fiber diameter\n" % fiberD)

        fiberD_str = str(fiberD*1000) + "nm"
        file_object.write("strdef fiberD_str\n")
        file_object.write("fiberD_str = \"%s\" // fiber diameter\n" % fiberD_str)
        intracellular_stim: dict = self.search(Config.SIM, "intracellular_stim")

        file_object.write("\n//***************** Intracellular Stim ***********\n")
        file_object.write("IntraStim_PulseTrain_delay    = %0.0f // [ms]\n" % intracellular_stim.get("times").get("IntraStim_PulseTrain_delay"))
        file_object.write("IntraStim_PulseTrain_pw       = %0.0f // [ms]\n" % intracellular_stim.get("times").get("pw"))
        file_object.write("IntraStim_PulseTrain_traindur = tstop - IntraStim_PulseTrain_delay // [ms]\n")
        file_object.write("IntraStim_PulseTrain_freq     = %0.0f // [ms]\n" % intracellular_stim.get("freq").get("value"))
        file_object.write("IntraStim_PulseTrain_amp      = %0.4f // [nA]\n" % intracellular_stim.get("amp").get("value"))
        file_object.write("IntraStim_PulseTrain_ind      = %0.0f "
                          "// Index of node where intracellular stim is placed [unitless]\n" %
                          intracellular_stim.get("ind"))

        file_object.write("\n//***************** Extracellular Stim ***********\n")
        file_object.write("strdef VeTime_fname\n")
        file_object.write("VeTime_fname            = \"%s\"\n" % "TBD")
        file_object.write("flag_extracellular_stim = %0.0f\n" % 1)

        file_object.write("\n//***************** Recording ********************\n")
        save_flags: dict = self.search(Config.SIM, "save_flags")

        file_object.write("saveflag_Vm_time      = %0.0f\n" % save_flags.get("vm_time"))
        file_object.write("saveflag_gating_time  = %0.0f\n" % save_flags.get("gating_time"))
        file_object.write("saveflag_Vm_space     = %0.0f\n" % save_flags.get("vm_space"))
        file_object.write("saveflag_gating_space = %0.0f\n" % save_flags.get("gating_space"))
        file_object.write("saveflag_Ve           = %0.0f\n" % save_flags.get("ve"))
        file_object.write("saveflag_Istim        = %0.0f\n" % save_flags.get("istim"))

        file_object.write("\n//***************** Classification Checkpoints ***\n")
        check_points: dict = self.search(Config.SIM, "check_points")
        file_object.write("Nchecknodes = %0.0f\n" % check_points.get("n_checknodes"))
        file_object.write("Nchecktimes = %0.0f\n" % check_points.get("n_checktimes"))

        file_object.write("\n//***************** Threshold Parameters *********\n")
        threshold: dict = self.search(Config.SIM, "threshold")
        file_object.write("find_thresh = %0.0f "
                          "// find_thresh = 0 if not doing threshold search; "
                          "find_thresh = 1 if looking for threshold\n"
                          % threshold.get("thresh"))
        file_object.write("find_block_thresh = %0.0f "
                          "// If find_thresh==1, can also set find_block_thresh = 1 "
                          "to find block thresholds instead of activation threshold\n"
                          % threshold.get("block_thresh"))

        num_fasc = 7  # TODO number of fascicles here - get the dimension from fibermanager?
        file_object.write("\nobjref stimamp_bottom_init\n")
        file_object.write("objref stimamp_bottom_init = new Vector(%0.0f,%0.0f)\n" % (num_fasc, 0))

        file_object.write("objref stimamp_top_init\n")
        file_object.write("objref stimamp_top_init = new Vector(%0.0f,%0.0f)\n\n" % (num_fasc, 0))
        for fasc in range(num_fasc):  # TODO stimamptops and stimampbottoms
            file_object.write("stimamp_bottom_init.x[%0.0f]        "
                              "= %0.4f // [mA] initial lower bound of binary search for thresh\n" % (fasc, 0.090000))
            file_object.write("stimamp_top_init.x[%0.0f]           "
                              "= %0.4f // [mA] initial upper bound of binary search for thresh for extracellular stim\n" % (fasc, 0.100000))

        file_object.write("\nap_thresh = %0.0f\n" % threshold.get("thresh"))
        file_object.write("N_minAPs  = %0.0f\n" % threshold.get("n_min_aps"))
        file_object.write("\nflag_whichstim  = %0.0f\n" % 0)

        file_object.write("\n//***************** Batching Parameters **********\n")
        amps = [0]
        Namp = len(amps)
        freqs = [self.search(Config.MODEL, "frequency", "value")/1000]
        Nfreq = len(freqs)

        file_object.write("Nmodels  = %0.0f\n" % 1)
        file_object.write("ModelNum = %0.0f\n" % 0)  # todo
        file_object.write("Nfasc    = %0.0f\n" % 0)  # todo
        file_object.write("Namp     = %0.0f\n" % Namp)
        file_object.write("Nfreq    = %0.0f\n" % Nfreq)
        file_object.write("\nobjref stimamp_values\n")
        file_object.write("stimamp_values = new Vector(Namp,%0.0f)\n" % 0)
        for amp in range(len(amps)):
            file_object.write("stimamp_values.x[%0.0f] = %0.0f\n" % (amp, 0))

        file_object.write("strdef num_Axons_fname\n")
        file_object.write("num_Axons_fname = \"%s\"\n" % "TBD")

        file_object.write("\nobjref Vefreq_values\n")
        file_object.write("Vefreq_values = new Vector(Nfreq,%0.0f)\n" % 0)
        for freq in range(len(freqs)):
            file_object.write("Vefreq_values.x[%0.0f] = %0.0f\n" % (freq, 0))

        file_object.write("\nload_file(\"Wrapper.hoc\")\n")

        # if C Fiber then dz and len too

        file_object.close()

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