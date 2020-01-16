import itertools
import math
from typing import List

import numpy as np

from src.utils import *


class SimulationBuilder(Exceptionable, Configurable, Saveable):
    def __init__(self, sim_config, exception_config):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.add(SetupMode.NEW, Config.FIBER_Z, os.path.join('config', 'system', 'fiber_z.json'))

    def define_sim_indices(self, args: List[List[np.array]]):
        return itertools.product(args)
        pass

    def write_launch_hocs(self):
        """
        Write file LaunchSim###.hoc
        :return:
        """
        write_mode = WriteMode.HOC
        file_name = "launch.{}".format(WriteMode.file_endings.value[write_mode.value])
        file_object = open(file_name, "w")

        # ENVIRONMENT
        file_object.write("\n//***************** Environment *****************\n")
        file_object.write("celsius   = %0.0f // [degC]\n" % self.search(Config.MODEL, "temperature", "value"))

        # TIME PARAMETERS
        file_object.write("\n//***************** Global Time ******************\n")
        #  extracellular_stim dict TODO
        extracellular_stim: dict = self.search(Config.SIM, "extracellular_stim", "global")
        dt = extracellular_stim.get("dt")
        file_object.write("dt        = %0.3f // [ms]\n" % dt)
        tstop = extracellular_stim.get("stop")
        file_object.write("tstop     = %0.0f // [ms]\n" % tstop)
        n_tsteps = math.floor(tstop / dt) + 1
        file_object.write("n_tsteps  = %0.0f // [unitless]\n" % n_tsteps)
        file_object.write("t_initSS  = %0.0f // [ms]\n" % extracellular_stim.get("initSS"))
        file_object.write("dt_initSS = %0.0f // [ms]\n" % extracellular_stim.get("dt_initSS"))

        # FIBER PARAMETERS
        file_object.write("\n//***************** Fiber Parameters *************\n")
        #  fiber model dict TODO
        fibers: dict = self.search(Config.SIM, "fibers")
        fiber_model = fibers.get("type")

        fiber_model_info: dict = self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_model)

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

    def write_slurm(self):
        """
        Write file StartSim###.slurm
        :return:
        """
        pass

    def make_folders(self):
        """
        :return:
        """






# need to save xy fiber data somewhere...
