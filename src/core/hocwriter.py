#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""


import itertools
import os
from typing import List

import numpy as np

from src.utils import (
    Config,
    Configurable,
    Exceptionable,
    FiberGeometry,
    FiberXYMode,
    MyelinationMode,
    NeuronRunMode,
    Saveable,
    SearchAmplitudeIncrementMode,
    SetupMode,
    TerminationCriteriaMode,
    WriteMode,
)


class HocWriter(Exceptionable, Configurable, Saveable):
    def __init__(self, source_dir, dest_dir, exception_config):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.source_dir = source_dir
        self.dest_dir = dest_dir

        self.add(
            SetupMode.NEW,
            Config.FIBER_Z,
            os.path.join('config', 'system', 'fiber_z.json'),
        )

    def define_sim_indices(self, args: List[List[np.array]]):
        return itertools.product(args)

    def build_hoc(self, n_tsteps):
        """
        Write file LaunchSim###.hoc
        :return:
        """

        if 'protocol' not in self.configs[Config.SIM.value].keys():
            self.configs[Config.SIM.value]['protocol'] = {
                "mode": "ACTIVATION_THRESHOLD",
                "initSS": -200,
                "dt_initSS": 10,
                "bounds_search": {
                    "mode": "PERCENT_INCREMENT",
                    "step": 10,
                    "top": -1,
                    "bottom": -0.01,
                },
                "termination_criteria": {"mode": "PERCENT_DIFFERENCE", "percent": 1},
                "threshold": {"value": -30, "n_min_aps": 1, "ap_detect_location": 0.9},
            }

        write_mode = WriteMode.HOC
        file_path = os.path.join(
            self.dest_dir,
            "launch{}".format(WriteMode.file_endings.value[write_mode.value]),
        )
        file_object = open(file_path, "w")

        # ENVIRONMENT
        file_object.write("\n//***************** Environment *****************\n")
        file_object.write("celsius   = %0.0f // [degC]\n" % self.search(Config.MODEL, "temperature"))

        # TIME PARAMETERS
        file_object.write("\n//***************** Global Time ******************\n")

        file_object.write("dt        = %0.3f // [ms]\n" % self.search(Config.SIM, "waveform", "global", "dt"))
        file_object.write("tstop     = %0.0f // [ms]\n" % self.search(Config.SIM, "waveform", "global", "stop"))
        file_object.write("n_tsteps  = %0.0f // [unitless]\n" % n_tsteps)
        file_object.write("t_initSS  = %0.0f // [ms]\n" % self.search(Config.SIM, "protocol", "initSS"))
        file_object.write("dt_initSS = %0.0f // [ms]\n" % self.search(Config.SIM, "protocol", "dt_initSS"))

        # FIBER PARAMETERS
        file_object.write("\n//***************** Fiber Parameters *************\n")
        fiber_model = self.search(Config.SIM, "fibers", "mode")
        fiber_model_info: dict = self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_model)

        # if myelinated
        if fiber_model_info.get("neuron_flag") == 2 and fiber_model != FiberGeometry.B_FIBER.value:
            file_object.write(
                "geometry_determination_method = %0.0f "
                "// geometry_determination_method = 0 for preset fiber diameters; "
                "geometry_determination_method = 1 for MRG-based geometry interpolation; "
                "geometry_determination_method = 2 for GeometryBuilder fits from SPARC Y2Q1\n"
                % fiber_model_info.get("geom_determination_method")
            )
            file_object.write("flag_model_b_fiber = %0.0f\n" % 0)

        if fiber_model_info.get("neuron_flag") == 2 and fiber_model == FiberGeometry.B_FIBER.value:
            file_object.write(
                "geometry_determination_method = %0.0f "
                "// geometry_determination_method = 0 for preset fiber diameters; "
                "geometry_determination_method = 1 for MRG-based geometry interpolation; "
                "geometry_determination_method = 2 for GeometryBuilder fits from SPARC Y2Q1\n"
                % fiber_model_info.get("geom_determination_method")
            )
            file_object.write("flag_model_b_fiber = %0.0f\n" % 1)

        file_object.write(
            "fiber_type = %0.0f "
            "// fiber_type = 1 for unmyelinated; fiber_type = 2 for myelinated; "
            "fiber_type = 3 for c fiber built from cFiberBuilder.hoc\n" % fiber_model_info.get("neuron_flag")
        )

        file_object.write(
            "node_channels = %0.0f "
            "// node_channels = 0 for MRG; node_channels = 1 for Schild 1994\n" % fiber_model_info.get("node_channels")
        )

        # Flag to change the end 2 nodes (either end) to 5 mm for SL only in NEURON
        xy_mode_name: str = self.search(Config.SIM, 'fibers', 'xy_parameters', 'mode')
        xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
        large_end_nodes = False if not xy_mode == FiberXYMode.SL_PSEUDO_INTERP else True
        file_object.write("large_end_nodes      = %0.0f\n" % int(large_end_nodes is True))

        if fiber_model_info.get("neuron_flag") == 3:
            channels = fiber_model_info.get("channels_type")
            file_object.write(
                "c_fiber_model_type            = {} // type: "
                "1:Sundt Model "
                "2:Tigerholm model "
                "3:Rattay model "
                "4:Schild model "
                "for c fiber built from cFiberBuilder.hoc\n".format(channels)
            )
            file_object.write("len                           = axonnodes*deltaz\n")

        file_object.write(
            "passive_end_nodes = %0.0f "
            "// passive_end_nodes = 1 to make both end nodes passive; 0 otherwise\n"
            % fiber_model_info.get("passive_end_nodes")
        )

        file_object.write("\n//***************** Intracellular Stim ***********\n")
        # use for keys only, get params with self.search() for error throwing if missing them
        intracellular_stim: dict = self.search(Config.SIM, "intracellular_stim")
        file_object.write(
            "IntraStim_PulseTrain_delay    = "
            "%0.2f // [ms]\n" % self.search(Config.SIM, "intracellular_stim", "times", "IntraStim_PulseTrain_delay")
        )
        file_object.write(
            "IntraStim_PulseTrain_pw       = %0.2f // [ms]\n"
            % self.search(Config.SIM, "intracellular_stim", "times", "pw")
        )

        if "IntraStim_PulseTrain_dur" in intracellular_stim.get("times").values():
            file_object.write(
                "IntraStim_PulseTrain_traindur = "
                "%0.2f // [ms]\n"
                % self.search(
                    Config.SIM,
                    "intracellular_stim",
                    "times",
                    "IntraStim_PulseTrain_dur",
                )
            )
        else:
            file_object.write("IntraStim_PulseTrain_traindur = tstop - IntraStim_PulseTrain_delay // [ms]\n")

        file_object.write(
            "IntraStim_PulseTrain_freq     = %0.2f // [Hz]\n"
            % self.search(Config.SIM, "intracellular_stim", "pulse_repetition_freq")
        )
        file_object.write(
            "IntraStim_PulseTrain_amp      = %0.4f // [nA]\n" % self.search(Config.SIM, "intracellular_stim", "amp")
        )
        file_object.write(
            "IntraStim_PulseTrain_ind      = %0.0f "
            "// Index of node where intracellular stim is placed [unitless]\n"
            % self.search(Config.SIM, "intracellular_stim", "ind")
        )

        file_object.write("\n//***************** Extracellular Stim ***********\n")
        file_object.write("strdef VeTime_fname\n")
        file_object.write("VeTime_fname            = \"%s\"\n" % "data/inputs/waveform.dat")
        file_object.write("flag_extracellular_stim = %0.0f // Set to zero for off; one for on \n" % 1)
        file_object.write("flag_whichstim = %0.0f // Set to zero for off; one for on \n" % 0)

        file_object.write("\n//***************** Recording ********************\n")
        if 'saving' not in self.configs[Config.SIM.value].keys():
            self.configs[Config.SIM.value]['saving'] = {
                "space": {"vm": False, "gating": False, "times": [0]},
                "time": {"vm": False, "gating": False, "istim": False, "locs": [0]},
                "runtimes": False,
            }
            # saving: dict = self.search(Config.SIM, "saving")
        else:
            pass
            # saving: dict = self.search(Config.SIM, "saving")

        file_object.write(
            "saveflag_Vm_time      = %0.0f\n" % int(self.search(Config.SIM, "saving", "time", "vm") is True)
        )
        file_object.write(
            "saveflag_gating_time  = %0.0f\n" % int(self.search(Config.SIM, "saving", "time", "gating") is True)
        )
        file_object.write(
            "saveflag_Vm_space     = %0.0f\n" % int(self.search(Config.SIM, "saving", "space", "vm") is True)
        )
        file_object.write(
            "saveflag_gating_space = %0.0f\n" % int(self.search(Config.SIM, "saving", "space", "gating") is True)
        )
        file_object.write("saveflag_Ve           = %0.0f\n" % int(False))
        file_object.write(
            "saveflag_Istim        = %0.0f\n" % int(self.search(Config.SIM, "saving", "time", "istim") is True)
        )

        if 'runtimes' not in self.configs[Config.SIM.value]['saving'].keys():
            file_object.write("saveflag_runtime     = %0.0f\n" % 0)
        else:
            file_object.write(
                "saveflag_runtime     = %0.0f\n" % int(self.search(Config.SIM, "saving", "runtimes") is True)
            )

        if 'end_ap_times' in self.configs[Config.SIM.value]['saving'].keys():
            loc_min = self.search(Config.SIM, "saving", "end_ap_times", "loc_min")
            loc_max = self.search(Config.SIM, "saving", "end_ap_times", "loc_max")

            if loc_min > loc_max:
                self.throw(114)
            if not ((1 >= loc_min >= 0) and (1 >= loc_max >= 0)):
                self.throw(115)
            if any([loc_min == 0, loc_min == 1, loc_max == 0, loc_max == 1]) and fiber_model_info.get(
                "passive_end_nodes"
            ):
                self.throw(116)

            file_object.write(
                "saveflag_end_ap_times = %0.0f\n\n" % 1
            )  # if Sim has "ap_end_times" defined, then we are recording them
            file_object.write("loc_min_end_ap        = %0.2f\n" % loc_min)
            file_object.write("loc_max_end_ap        = %0.2f\n" % loc_max)
            file_object.write(
                "ap_end_thresh         = %0.0f\n" % self.search(Config.SIM, "saving", "end_ap_times", "threshold")
            )

        file_object.write("\n//***************** Protocol Parameters *********\n")

        protocol_mode_name: str = self.search(Config.SIM, 'protocol', 'mode')
        try:
            protocol_mode: NeuronRunMode = [
                mode for mode in NeuronRunMode if str(mode).split('.')[-1] == protocol_mode_name
            ][0]
        except:
            self.throw(135)

        if protocol_mode != NeuronRunMode.FINITE_AMPLITUDES:
            find_thresh = 1
            if protocol_mode == NeuronRunMode.ACTIVATION_THRESHOLD:
                block_thresh_flag = NeuronRunMode.ACTIVATION_THRESHOLD.value
            elif protocol_mode == NeuronRunMode.BLOCK_THRESHOLD:
                block_thresh_flag = NeuronRunMode.BLOCK_THRESHOLD.value

            threshold: dict = self.search(Config.SIM, "protocol", "threshold")
            file_object.write("\nap_thresh = %0.0f\n" % self.search(Config.SIM, "protocol", "threshold", "value"))
            if self.search(Config.SIM, "protocol", "threshold", "n_min_aps") != 1:
                self.throw(142)
            file_object.write("N_minAPs  = %0.0f\n" % self.search(Config.SIM, "protocol", "threshold", "n_min_aps"))

            if 'ap_detect_location' not in threshold.keys():
                file_object.write("ap_detect_location  = 0.9\n")
            else:
                file_object.write(
                    "ap_detect_location  = %0.2f\n"
                    % self.search(Config.SIM, "protocol", "threshold", "ap_detect_location")
                )

            bounds_search_mode_name: str = self.search(Config.SIM, "protocol", "bounds_search", "mode")
            bounds_search_mode: SearchAmplitudeIncrementMode = [
                mode for mode in SearchAmplitudeIncrementMode if str(mode).split('.')[-1] == bounds_search_mode_name
            ][0]
            if bounds_search_mode == SearchAmplitudeIncrementMode.PERCENT_INCREMENT:
                increment_flag = SearchAmplitudeIncrementMode.PERCENT_INCREMENT.value
                step: float = self.search(Config.SIM, "protocol", "bounds_search", "step")
                file_object.write("\nrel_increment = %0.4f\n" % (step / 100))
            elif bounds_search_mode == SearchAmplitudeIncrementMode.ABSOLUTE_INCREMENT:
                increment_flag = SearchAmplitudeIncrementMode.ABSOLUTE_INCREMENT.value
                step: float = self.search(Config.SIM, "protocol", "bounds_search", "step")
                file_object.write("\nabs_increment = %0.4f\n" % step)
            file_object.write("increment_flag = %0.0f // \n" % increment_flag)

            termination_criteria_mode_name: str = self.search(Config.SIM, "protocol", "termination_criteria", "mode")
            termination_criteria_mode: TerminationCriteriaMode = [
                mode for mode in TerminationCriteriaMode if str(mode).split('.')[-1] == termination_criteria_mode_name
            ][0]
            if termination_criteria_mode == TerminationCriteriaMode.ABSOLUTE_DIFFERENCE:
                termination_flag = TerminationCriteriaMode.ABSOLUTE_DIFFERENCE.value
                res: float = self.search(Config.SIM, "protocol", "termination_criteria", "tolerance")
                file_object.write("\nabs_thresh_resoln = %0.4f\n" % res)
            elif termination_criteria_mode == TerminationCriteriaMode.PERCENT_DIFFERENCE:
                termination_flag = TerminationCriteriaMode.PERCENT_DIFFERENCE.value
                res: float = self.search(Config.SIM, "protocol", "termination_criteria", "percent")
                file_object.write("\nrel_thresh_resoln = %0.4f\n" % (res / 100))
            file_object.write("termination_flag = %0.0f // \n" % termination_flag)

            max_iter = self.search(Config.SIM, "protocol", "bounds_search").get("max_steps", 100)
            file_object.write("max_iter = %0.0f // \n" % max_iter)

            file_object.write("Namp = %0.0f\n" % 1)
            file_object.write("objref stimamp_values\n")
            file_object.write("stimamp_values = new Vector(Namp,%0.0f)\n" % 0)
            for amp_ind in range(1):
                file_object.write("stimamp_values.x[%0.0f] = %0.4f\n" % (amp_ind, 0))

        elif protocol_mode == NeuronRunMode.FINITE_AMPLITUDES:
            find_thresh = 0
            block_thresh_flag = 0
            amps = self.search(Config.SIM, "protocol", "amplitudes")
            num_amps = len(amps)
            file_object.write("\n//***************** Batching Parameters **********\n")
            file_object.write("Namp = %0.0f\n" % num_amps)
            file_object.write("objref stimamp_values\n")
            file_object.write("stimamp_values = new Vector(Namp,%0.0f)\n" % 0)
            file_object.write("\nap_thresh = %0.0f\n" % 1000)  # arbitrarily high, not ever used
            for amp_ind in range(num_amps):
                file_object.write("stimamp_values.x[%0.0f] = %0.4f\n" % (amp_ind, amps[amp_ind]))

        file_object.write(
            "\nfind_thresh = %0.0f "
            "// find_thresh = 0 if not doing threshold search; "
            "find_thresh = 1 if looking for threshold\n" % find_thresh
        )

        file_object.write(
            "find_block_thresh = %0.0f "
            "// If find_thresh==1, can also set find_block_thresh = 1 "
            "to find block thresholds instead of activation threshold\n" % block_thresh_flag
        )

        file_object.write("\n//***************** Classification Checkpoints ***\n")
        # Time points to record Vm and gating params vs x
        checktimes = self.search(Config.SIM, "saving", "space", "times")
        n_checktimes = len(checktimes)
        file_object.write("Nchecktimes = %0.0f \n" % n_checktimes)

        file_object.write("objref checktime_values_ms, checktime_values\n")
        file_object.write("checktime_values_ms = new Vector(Nchecktimes,0)\n")
        file_object.write("checktime_values = new Vector(Nchecktimes,0)\n\n")

        file_object.write("// Check times in milliseconds\n")
        for time_ind in range(n_checktimes):
            file_object.write("checktime_values_ms.x[{}] = {} \n".format(time_ind, checktimes[time_ind]))

        checknodes = self.search(Config.SIM, "saving", "time", "locs")
        if checknodes == 'all':
            file_object.write("\nNchecknodes = axonnodes\n")
        else:
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
        if checknodes != 'all':
            for node_ind in range(n_checknodes):
                file_object.write(
                    "\tchecknode_values.x[{}] = int(axon_length*{}/deltaz)\n".format(node_ind, checknodes[node_ind])
                )
        file_object.write("}\n")

        file_object.write("\nload_file(\"../../HOC_Files/Wrapper.hoc\")\n")

        file_object.close()
