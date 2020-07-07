import itertools
from typing import List

import numpy as np

from src.utils import *


class HocWriter(Exceptionable, Configurable, Saveable):
    def __init__(self, source_dir, dest_dir, exception_config):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.source_dir = source_dir
        self.dest_dir = dest_dir

        self.add(SetupMode.NEW, Config.FIBER_Z, os.path.join('config', 'system', 'fiber_z.json'))

    def define_sim_indices(self, args: List[List[np.array]]):
        return itertools.product(args)
        pass

    def build_hoc(self, n_inners, n_fiber_coords, n_tsteps):
        """
        Write file LaunchSim###.hoc
        :return:
        """

        write_mode = WriteMode.HOC
        file_path = os.path.join(self.dest_dir, "launch{}".format(WriteMode.file_endings.value[write_mode.value]))
        file_object = open(file_path, "w")

        # ENVIRONMENT
        file_object.write("\n//***************** Environment *****************\n")
        file_object.write("celsius   = %0.0f // [degC]\n" % self.search(Config.MODEL, "temperature"))

        # TIME PARAMETERS
        file_object.write("\n//***************** Global Time ******************\n")
        extracellular_stim: dict = self.search(Config.SIM, "waveform", "global")
        dt = extracellular_stim.get("dt")
        file_object.write("dt        = %0.3f // [ms]\n" % dt)
        tstop = extracellular_stim.get("stop")
        file_object.write("tstop     = %0.0f // [ms]\n" % tstop)
        file_object.write("n_tsteps  = %0.0f // [unitless]\n" % n_tsteps)
        file_object.write("t_initSS  = %0.0f // [ms]\n" % extracellular_stim.get("initSS"))
        file_object.write("dt_initSS = %0.0f // [ms]\n" % extracellular_stim.get("dt_initSS"))

        # FIBER PARAMETERS
        file_object.write("\n//***************** Fiber Parameters *************\n")
        fibers: dict = self.search(Config.SIM, "fibers")
        fiber_model = fibers.get("mode")

        fiber_model_info: dict = self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_model)
        diameter = self.search(Config.SIM, "fibers", "z_parameters", "diameter")

        # if myelinated
        if fiber_model_info.get("neuron_flag") == 2 and fiber_model != FiberGeometry.B_FIBER.value:
            file_object.write("geometry_determination_method = %0.0f "
                              "// geometry_determination_method = 0 for preset fiber diameters; "
                              "geometry_determination_method = 1 for MRG-based geometry interpolation; "
                              "geometry_determination_method = 2 for GeometryBuilder fits from SPARC Y2Q1\n"
                              % fiber_model_info.get("geom_determination_method"))
            file_object.write("flag_model_b_fiber = %0.0f\n" % 0)

            if fiber_model_info.get("geom_determination_method") == 0:
                fiber_geometry_mode_name: str = self.search(Config.SIM, 'fibers', 'mode')
                diameters, delta_zs, paranodal_length_2s = (
                    self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_geometry_mode_name, key)
                    for key in ('diameters', 'delta_zs', 'paranodal_length_2s')
                )
                diameter_index = diameters.index(diameter)
                delta_z = delta_zs[diameter_index]
                file_object.write("deltaz = %0.4f \n" % delta_z)

            elif fiber_model_info.get("geom_determination_method") == 1:
                fiber_geometry_mode_name: str = self.search(Config.SIM, 'fibers', 'mode')
                paranodal_length_2_str, delta_z_str, inter_length_str = (
                    self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_geometry_mode_name, key)
                    for key in ('paranodal_length_2', 'delta_z', 'inter_length')
                )

                if diameter > 16.0 or diameter < 2.0:
                    self.throw(77)
                if diameter >= 5.643:
                    delta_z = eval(delta_z_str["diameter_greater_or_equal_5.643um"])
                else:
                    delta_z = eval(delta_z_str["diameter_less_5.643um"])

                file_object.write("deltaz = %0.4f \n" % delta_z)

        if fiber_model_info.get("neuron_flag") == 2 and fiber_model == FiberGeometry.B_FIBER.value:
            file_object.write("geometry_determination_method = %0.0f "
                              "// geometry_determination_method = 0 for preset fiber diameters; "
                              "geometry_determination_method = 1 for MRG-based geometry interpolation; "
                              "geometry_determination_method = 2 for GeometryBuilder fits from SPARC Y2Q1\n"
                              % fiber_model_info.get("geom_determination_method"))
            file_object.write("flag_model_b_fiber = %0.0f\n" % 1)

            # TODO add delta_z for B-Fiber eventually

        file_object.write("fiber_type = %0.0f "
                          "// fiber_type = 1 for unmyelinated; fiber_type = 2 for myelinated; "
                          "fiber_type = 3 for c fiber built from cFiberBuilder.hoc\n"
                          % fiber_model_info.get("neuron_flag"))

        file_object.write("node_channels = %0.0f "
                          "// node_channels = 0 for MRG; node_channels = 1 for Schild 1994\n" %
                          fiber_model_info.get("node_channels"))

        if fiber_model_info.get("neuron_flag") == 2:
            axonnodes = 1 + (n_fiber_coords - 1) / 11
        elif fiber_model_info.get("neuron_flag") == 3:
            axonnodes = n_fiber_coords

        file_object.write("axonnodes = %0.0f "
                          "// must match up with ExtractPotentials\n" % axonnodes)

        if fiber_model_info.get("neuron_flag") == 3:
            channels = fiber_model_info.get("channels_type")
            file_object.write("c_fiber_model_type            = {} // type: "
                              "1:Sundt Model "
                              "2:Tigerholm model "
                              "3:Rattay model "
                              "4:Schild model "
                              "for c fiber built from cFiberBuilder.hoc\n".format(channels))
            deltaz = fiber_model_info.get("delta_zs")
            file_object.write("deltaz = %0.4f \n" % deltaz)
            file_object.write("len                           = axonnodes*deltaz\n")

        file_object.write("passive_end_nodes = %0.0f "
                          "// passive_end_nodes = 1 to make both end nodes passive; 0 otherwise\n" %
                          fiber_model_info.get("passive_end_nodes"))

        file_object.write("fiberD = %0.1f "
                          "// fiber diameter\n" % diameter)

        intracellular_stim: dict = self.search(Config.SIM, "intracellular_stim")

        file_object.write("\n//***************** Intracellular Stim ***********\n")
        file_object.write("IntraStim_PulseTrain_delay    = %0.0f // [ms]\n" % intracellular_stim.get("times").get(
            "IntraStim_PulseTrain_delay"))
        file_object.write("IntraStim_PulseTrain_pw       = %0.0f // [ms]\n" % intracellular_stim.get("times").get("pw"))
        file_object.write("IntraStim_PulseTrain_traindur = tstop - IntraStim_PulseTrain_delay // [ms]\n")
        file_object.write(
            "IntraStim_PulseTrain_freq     = %0.0f // [ms]\n" % intracellular_stim.get("pulse_repetition_freq"))
        file_object.write("IntraStim_PulseTrain_amp      = %0.4f // [nA]\n" % intracellular_stim.get("amp"))
        file_object.write("IntraStim_PulseTrain_ind      = %0.0f "
                          "// Index of node where intracellular stim is placed [unitless]\n" %
                          intracellular_stim.get("ind"))

        file_object.write("\n//***************** Extracellular Stim ***********\n")
        file_object.write("strdef VeTime_fname\n")
        file_object.write("VeTime_fname            = \"%s\"\n" % "data/inputs/waveform.dat")
        file_object.write("flag_extracellular_stim = %0.0f // Set to zero for off; one for on \n" % 1)

        file_object.write("\n//***************** Recording ********************\n")
        if 'saving' not in self.configs[Config.SIM.value].keys():
            self.configs[Config.SIM.value]['saving'] = {
                "space": {
                    "vm": False,
                    "gating": False,
                    "times": [0]
                },
                "time": {
                    "vm": False,
                    "gating": False,
                    "istim": False,
                    "locs": [0]
                }
            }

        saving: dict = self.search(Config.SIM, "saving")

        file_object.write("saveflag_Vm_time      = %0.0f\n" % int(saving.get("time").get("vm") == True))
        file_object.write("saveflag_gating_time  = %0.0f\n" % int(saving.get("time").get("gating") == True))
        file_object.write("saveflag_Vm_space     = %0.0f\n" % int(saving.get("space").get("vm") == True))
        file_object.write("saveflag_gating_space = %0.0f\n" % int(saving.get("space").get("gating") == True))
        file_object.write("saveflag_Ve           = %0.0f\n" % int(False))
        file_object.write("saveflag_Istim        = %0.0f\n" % int(saving.get("time").get("istim") == True))

        file_object.write("\n//***************** Protocol Parameters *********\n")

        if 'protocol' not in self.configs[Config.SIM.value].keys():
            self.configs[Config.SIM.value]['protocol'] = {
                "mode": "ACTIVATION_THRESHOLD",
                "bounds_search": {
                    "mode": "PERCENT_INCREMENT",
                    "relative_step": 0.1
                },
                "termination_criteria": {
                    "mode": "RELATIVE_DIFFERENCE",
                    "percent": 0.01
                },
                "threshold": {
                    "thresh_flag": 1,
                    "block_thresh": 0,
                    "resolution": 0.01,
                    "value": -30,
                    "n_min_aps": 1
                }
            }

        protocol_mode_name: str = self.search(Config.SIM, 'protocol', 'mode')
        protocol_mode: NeuronRunMode = \
            [mode for mode in NeuronRunMode if str(mode).split('.')[-1] == protocol_mode_name][0]

        if protocol_mode != NeuronRunMode.FINITE_AMPLITUDES:
            find_thresh = 1
            if protocol_mode == NeuronRunMode.ACTIVATION_THRESHOLD:
                block_thresh_flag = NeuronRunMode.ACTIVATION_THRESHOLD.value
            elif protocol_mode == NeuronRunMode.BLOCK_THRESHOLD:
                block_thresh_flag = NeuronRunMode.BLOCK_THRESHOLD.value

            threshold: dict = self.search(Config.SIM, "protocol", "threshold")
            file_object.write("\nap_thresh = %0.0f\n" % threshold.get("value"))
            file_object.write("N_minAPs  = %0.0f\n" % threshold.get("n_min_aps"))

            bounds_search_mode_name: str = self.search(Config.SIM, "protocol", "bounds_search", "mode")
            bounds_search_mode: SearchAmplitudeIncrementMode = \
                [mode for mode in SearchAmplitudeIncrementMode if str(mode).split('.')[-1] == bounds_search_mode_name][
                    0]
            if bounds_search_mode == SearchAmplitudeIncrementMode.PERCENT_INCREMENT:
                increment_flag = SearchAmplitudeIncrementMode.PERCENT_INCREMENT.value
                step: float = self.search(Config.SIM, "protocol", "bounds_search", "step")
                file_object.write("\nrel_increment = %0.4f\n" % step)
            elif bounds_search_mode == SearchAmplitudeIncrementMode.ABSOLUTE_INCREMENT:
                increment_flag = SearchAmplitudeIncrementMode.ABSOLUTE_INCREMENT.value
                step: float = self.search(Config.SIM, "protocol", "bounds_search", "step")
                file_object.write("\nabs_increment = %0.4f\n" % step)
            file_object.write("increment_flag = %0.0f // \n" % increment_flag)

            termination_criteria_mode_name: str = self.search(Config.SIM, "protocol", "termination_criteria", "mode")
            termination_criteria_mode: TerminationCriteriaMode = \
                [mode for mode in TerminationCriteriaMode if
                 str(mode).split('.')[-1] == termination_criteria_mode_name][0]
            if termination_criteria_mode == TerminationCriteriaMode.ABSOLUTE_DIFFERENCE:
                termination_flag = TerminationCriteriaMode.ABSOLUTE_DIFFERENCE.value
                res: float = self.search(Config.SIM, "protocol", "termination_criteria", "tolerance")
                file_object.write("\nabs_thresh_resoln = %0.4f\n" % res)
            elif termination_criteria_mode == TerminationCriteriaMode.PERCENT_DIFFERENCE:
                termination_flag = TerminationCriteriaMode.PERCENT_DIFFERENCE.value
                res: float = self.search(Config.SIM, "protocol", "termination_criteria", "percent")
                file_object.write("\nrel_thresh_resoln = %0.4f\n" % res)
            file_object.write("termination_flag = %0.0f // \n" % termination_flag)

            file_object.write("Namp = %0.0f\n" % 1)
            file_object.write("objref stimamp_values\n")
            file_object.write("stimamp_values = new Vector(Namp,%0.0f)\n" % 0)
            for amp_ind in range(1):
                file_object.write("stimamp_values.x[%0.0f] = %0.4f\n" % (amp_ind, 0))

        elif protocol_mode == NeuronRunMode.FINITE_AMPLITUDES:
            find_thresh = 0
            block_thresh_flag = 0
            amps = self.search(Config.SIM, "protocol", "amplitudes", "value")
            num_amps = len(amps)
            file_object.write("\n//***************** Batching Parameters **********\n")
            file_object.write("Namp = %0.0f\n" % num_amps)
            file_object.write("objref stimamp_values\n")
            file_object.write("stimamp_values = new Vector(Namp,%0.0f)\n" % 0)
            for amp_ind in range(num_amps):
                file_object.write("stimamp_values.x[%0.0f] = %0.4f\n" % (amp_ind, amps[amp_ind]))

        file_object.write("\nfind_thresh = %0.0f "
                          "// find_thresh = 0 if not doing threshold search; "
                          "find_thresh = 1 if looking for threshold\n" % find_thresh)

        file_object.write("find_block_thresh = %0.0f "
                          "// If find_thresh==1, can also set find_block_thresh = 1 "
                          "to find block thresholds instead of activation threshold\n"
                          % block_thresh_flag)

        file_object.write("\n//***************** Classification Checkpoints ***\n")
        # Time points to record Vm and gating params vs x
        checktimes = self.configs[Config.SIM.value]['saving']['space']['times']
        n_checktimes = len(checktimes)
        file_object.write("Nchecktimes = %0.0f \n" % n_checktimes)

        file_object.write("objref checktime_values_ms, checktime_values\n")
        file_object.write("checktime_values_ms = new Vector(Nchecktimes,0)\n")
        file_object.write("checktime_values = new Vector(Nchecktimes,0)\n\n")

        file_object.write("// Check times in milliseconds\n")
        for time_ind in range(n_checktimes):
            file_object.write("checktime_values_ms.x[{}] = {} \n".format(time_ind, checktimes[time_ind]))

        checknodes = self.configs[Config.SIM.value]['saving']['time']['locs']
        n_checknodes = len(checknodes)
        file_object.write("\nNchecknodes = %0.0f\n" % n_checknodes)
        file_object.write("objref checknode_values\n")
        file_object.write("checknode_values = new Vector(Nchecknodes,0)\n")
        file_object.write("if (Nchecknodes == axonnodes) {\n")
        file_object.write("\tfor i = 0, axonnodes - 1 {\n")
        file_object.write("\t\tchecknode_values.x[i] = i\n")
        file_object.write("\t}\n")
        file_object.write("} else {\n")
        file_object.write("\taxon_length = (axonnodes-1)*deltaz				// length of axon [um]\n")
        for node_ind in range(n_checknodes):
            file_object.write("\tchecknode_values.x[{}] = int(axon_length*{}/deltaz)\n".format(node_ind, checknodes[node_ind]))
        file_object.write("}\n")

        file_object.write("\nload_file(\"../../HOC_Files/Wrapper.hoc\")\n")

        file_object.close()
