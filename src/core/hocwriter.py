#!/usr/bin/env python3.7

"""Defines HOCWriter class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""


import itertools
import os
import warnings

import numpy as np

from src.utils import (
    Config,
    Configurable,
    FiberGeometry,
    MyelinationMode,
    NeuronRunMode,
    Saveable,
    SearchAmplitudeIncrementMode,
    SetupMode,
    TerminationCriteriaMode,
    WriteMode,
)


class HocWriter(Configurable, Saveable):
    """Make launch.hoc file for each simulation run."""

    def __init__(self, source_dir, dest_dir):
        """Initialize HocWriter.

        :param source_dir: Path to source directory.
        :param dest_dir: Path to destination directory.
        """
        # Initializes superclass
        Configurable.__init__(self)

        self.source_dir = source_dir
        self.dest_dir = dest_dir

        self.add(
            SetupMode.NEW,
            Config.FIBER_Z,
            os.path.join('config', 'system', 'fiber_z.json'),
        )

    def define_sim_indices(self, args: list[list[np.array]]):
        """Define simulation indices.

        :param args: List of lists of arrays of simulation indices.
        :return: List of all simulation indices (flattened).
        """
        return itertools.product(args)

    def build_hoc(self, n_tsteps):
        """Write file launch.hoc for launching NEURON simulations.

        :param n_tsteps: Number of time steps in simulation.
        """
        write_mode = WriteMode.HOC
        file_path = os.path.join(
            self.dest_dir,
            f"launch{WriteMode.file_endings.value[write_mode.value]}",
        )
        with open(file_path, "w") as file_object:
            self.write_base_parameters(file_object, n_tsteps)

            fiber_model_info = self.write_fiber_parameters(file_object)

            self.write_intracellular_stim(file_object)

            self.write_extracellular_stim(file_object)

            self.write_saving(fiber_model_info, file_object)

            self.write_protocol(file_object)

            self.write_classification_checkpoints(file_object)

            file_object.write("}\n")
            file_object.write("\nload_file(\"../../HOC_Files/Wrapper.hoc\")\n")

    def write_base_parameters(self, file_object, n_tsteps):
        """Write base parameters to launch.hoc.

        :param file_object: File object to write to.
        :param n_tsteps: Number of time steps in simulation.
        """
        # ENVIRONMENT
        file_object.write("\n//***************** Environment *****************\n")
        file_object.write(f"celsius   = {self.search(Config.MODEL, 'temperature'):0.0f} // [degC]\n")
        # TIME PARAMETERS
        file_object.write("\n//***************** Global Time ******************\n")
        file_object.write(f"dt        = {self.search(Config.SIM, 'waveform', 'global', 'dt'):0.4f} // [ms]\n")
        file_object.write(f"tstop     = {self.search(Config.SIM, 'waveform', 'global', 'stop'):0.0f} // [ms]\n")
        file_object.write(f"n_tsteps  = {n_tsteps:0.0f} // [unitless]\n")
        file_object.write(f"t_initSS  = {self.search(Config.SIM, 'protocol', 'initSS'):0.0f} // [ms]\n")
        file_object.write(f"dt_initSS = {self.search(Config.SIM, 'protocol', 'dt_initSS'):0.0f} // [ms]\n")

    def write_fiber_parameters(self, file_object):
        """Write fiber parameters to launch.hoc.

        :param file_object: File object to write to.
        :return: Fiber model information.
        """
        # FIBER PARAMETERS
        file_object.write("\n//***************** Fiber Parameters *************\n")
        fiber_model = self.search(Config.SIM, "fibers", "mode")
        fiber_model_info: dict = self.search(Config.FIBER_Z, MyelinationMode.parameters.value, fiber_model)
        # if myelinated
        if fiber_model_info.get("neuron_flag") == 2 and fiber_model != FiberGeometry.SMALL_MRG_INTERPOLATION_V1.value:
            file_object.write(
                f"geometry_determination_method = {fiber_model_info.get('geom_determination_method'):0.0f} "
                f"// geometry_determination_method = 0 for preset fiber diameters; "
                f"geometry_determination_method = 1 for MRG-based geometry interpolation; "
                f"geometry_determination_method = 2 for GeometryBuilder fits from SPARC Y2Q1\n"
            )
            file_object.write(f"flag_model_small_mrg_interp_v1 = {0}\n")
        if fiber_model_info.get("neuron_flag") == 2 and fiber_model == FiberGeometry.SMALL_MRG_INTERPOLATION_V1.value:
            file_object.write(
                f"geometry_determination_method = {fiber_model_info.get('geom_determination_method')} "
                "// geometry_determination_method = 0 for preset fiber diameters; "
                "geometry_determination_method = 1 for MRG-based geometry interpolation; "
                "geometry_determination_method = 2 for GeometryBuilder fits from SPARC Y2Q1\n"
            )
            file_object.write(f"flag_model_small_mrg_interp_v1 = {1}\n")
        file_object.write(
            f"fiber_type = {fiber_model_info.get('neuron_flag')} "
            "// fiber_type = 1 for unmyelinated; fiber_type = 2 for myelinated; "
            "fiber_type = 3 for c fiber built from cFiberBuilder.hoc\n"
        )
        file_object.write(
            f"node_channels = {fiber_model_info.get('node_channels')} "
            "// node_channels = 0 for MRG; node_channels = 1 for Schild 1994\n"
        )
        # Flag to change the end 2 nodes (either end) to 5 mm
        file_object.write(f"large_end_nodes      = {0}\n")
        if fiber_model_info.get("neuron_flag") == 3:
            channels = fiber_model_info.get("channels_type")
            file_object.write(
                f"c_fiber_model_type            = {channels} // type: "
                "1:Sundt Model "
                "2:Tigerholm model "
                "3:Rattay model "
                "4:Schild model "
                "for c fiber built from cFiberBuilder.hoc\n"
            )
            file_object.write("len                           = axonnodes*deltaz\n")
        file_object.write(
            f"passive_end_nodes = {fiber_model_info.get('passive_end_nodes')} "
            "// passive_end_nodes = 1 to make both end nodes passive; 0 otherwise\n"
        )
        return fiber_model_info

    def write_extracellular_stim(self, file_object):
        """Write extracellular stimulation parameters to launch.hoc.

        :param file_object: File object to write to.
        """
        file_object.write("\n//***************** Extracellular Stim ***********\n")
        file_object.write("strdef VeTime_fname\n")
        file_object.write(f"VeTime_fname            = \"{'data/inputs/waveform.dat'}\"\n")
        stim_cuff_present = int(bool(self.search(Config.SIM, "active_srcs", optional=True)))
        file_object.write(f"flag_extracellular_stim = {stim_cuff_present} // Set to zero for off; one for on \n")
        rec_cuff_present = int(bool(self.search(Config.SIM, "active_recs", optional=True)))
        file_object.write(f"flag_extracellular_rec = {rec_cuff_present} // Set to zero for off; one for on \n")
        file_object.write(f"flag_whichstim = {0} // Set to zero for off; one for on \n")

    def write_classification_checkpoints(self, file_object):
        """Write classification checkpoints to launch.hoc.

        :param file_object: File object to write to.
        """
        file_object.write("\n//***************** Classification Checkpoints ***\n")
        # Time points to record Vm and gating params vs x
        checktimes = self.search(Config.SIM, "saving", "space", "times")
        n_checktimes = len(checktimes)
        file_object.write(f"Nchecktimes = {n_checktimes:0.0f} \n")
        file_object.write("objref checktime_values_ms, checktime_values\n")
        file_object.write("checktime_values_ms = new Vector(Nchecktimes,0)\n")
        file_object.write("checktime_values = new Vector(Nchecktimes,0)\n\n")
        file_object.write("// Check times in milliseconds\n")
        for time_ind in range(n_checktimes):
            file_object.write(f"checktime_values_ms.x[{time_ind}] = {checktimes[time_ind]} \n")
        checknodes = self.search(Config.SIM, "saving", "time", "locs")
        if checknodes == 'all':
            file_object.write("\nNchecknodes = axonnodes\n")
        else:
            n_checknodes = len(checknodes)
            file_object.write(f"\nNchecknodes = {n_checknodes:0.0f}\n")
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
                    f"\tchecknode_values.x[{node_ind}] = int(axon_length*{checknodes[node_ind]}/deltaz)\n"
                )

    def write_protocol(self, file_object):
        """Write protocol to launch.hoc.

        :raises ValueError: If protocol is not supported.
        :param file_object: File object to write to.
        """
        file_object.write("\n//***************** Protocol Parameters *********\n")
        protocol_mode_name: str = self.search(Config.SIM, 'protocol', 'mode')
        try:
            protocol_mode: NeuronRunMode = [
                mode for mode in NeuronRunMode if str(mode).split('.')[-1] == protocol_mode_name
            ][0]
        except IndexError:
            raise ValueError("Invalid protocol mode defined in sim configuration file")
        if protocol_mode != NeuronRunMode.FINITE_AMPLITUDES:
            find_thresh = 1
            if protocol_mode == NeuronRunMode.ACTIVATION_THRESHOLD:
                block_thresh_flag = NeuronRunMode.ACTIVATION_THRESHOLD.value
            elif protocol_mode == NeuronRunMode.BLOCK_THRESHOLD:
                block_thresh_flag = NeuronRunMode.BLOCK_THRESHOLD.value

            threshold: dict = self.search(Config.SIM, "protocol", "threshold")
            file_object.write(f"\nap_thresh = {self.search(Config.SIM, 'protocol', 'threshold', 'value'):0.0f}\n")
            if self.search(Config.SIM, "protocol", "threshold", "n_min_aps") != 1:
                raise ValueError("Currently SIM configuration only supports protocol>threshold>n_min_aps = 1")
            file_object.write(f"N_minAPs  = {self.search(Config.SIM, 'protocol', 'threshold', 'n_min_aps'):0.0f}\n")

            if 'ap_detect_location' not in threshold:
                file_object.write("ap_detect_location  = 0.9\n")
            else:
                file_object.write(
                    f"ap_detect_location  = "
                    f"{self.search(Config.SIM, 'protocol', 'threshold', 'ap_detect_location'):.2f}\n"
                )

            bounds_search_mode_name: str = self.search(Config.SIM, "protocol", "bounds_search", "mode")
            bounds_search_mode: SearchAmplitudeIncrementMode = [
                mode for mode in SearchAmplitudeIncrementMode if str(mode).split('.')[-1] == bounds_search_mode_name
            ][0]
            if bounds_search_mode == SearchAmplitudeIncrementMode.PERCENT_INCREMENT:
                increment_flag = SearchAmplitudeIncrementMode.PERCENT_INCREMENT.value
                step: float = self.search(Config.SIM, "protocol", "bounds_search", "step")
                file_object.write(f"\nrel_increment = {step / 100:0.4f}\n")
            elif bounds_search_mode == SearchAmplitudeIncrementMode.ABSOLUTE_INCREMENT:
                increment_flag = SearchAmplitudeIncrementMode.ABSOLUTE_INCREMENT.value
                step: float = self.search(Config.SIM, "protocol", "bounds_search", "step")
                file_object.write(f"\nabs_increment = {step:0.4f}\n")
            file_object.write(f"increment_flag = {increment_flag:0.0f} // \n")

            termination_criteria_mode_name: str = self.search(Config.SIM, "protocol", "termination_criteria", "mode")
            termination_criteria_mode: TerminationCriteriaMode = [
                mode for mode in TerminationCriteriaMode if str(mode).split('.')[-1] == termination_criteria_mode_name
            ][0]
            if termination_criteria_mode == TerminationCriteriaMode.ABSOLUTE_DIFFERENCE:
                termination_flag = TerminationCriteriaMode.ABSOLUTE_DIFFERENCE.value
                res: float = self.search(Config.SIM, "protocol", "termination_criteria", "tolerance")
                file_object.write(f"\nabs_thresh_resoln = {res:0.4f}\n")
            elif termination_criteria_mode == TerminationCriteriaMode.PERCENT_DIFFERENCE:
                termination_flag = TerminationCriteriaMode.PERCENT_DIFFERENCE.value
                res: float = self.search(Config.SIM, "protocol", "termination_criteria", "percent")
                file_object.write(f"\nrel_thresh_resoln = {res / 100:0.4f}\n")
            file_object.write(f"termination_flag = {termination_flag:0.0f} // \n")

            max_iter = self.search(Config.SIM, "protocol", "bounds_search").get("max_steps", 100)
            file_object.write(f"max_iter = {max_iter:0.0f} // \n")

            file_object.write(f"Namp = {1}\n")
            file_object.write("objref stimamp_values\n")
            file_object.write(f"stimamp_values = new Vector(Namp,{0})\n")
            for amp_ind in range(1):
                file_object.write(f"stimamp_values.x[{amp_ind:0.0f}] = {0:0.4f}\n")

        elif protocol_mode == NeuronRunMode.FINITE_AMPLITUDES:
            activation: dict = self.search(Config.SIM, "protocol", "threshold", optional=True)
            if activation is None:
                warnings.warn(
                    'No activation threshold parameters defined for FINITE_AMPLITUDES protocol,'
                    'proceeding with default values',
                    stacklevel=2,
                )
                ap_thresh = -30
                ap_detect_location = 0.9
            else:
                ap_thresh = self.search(Config.SIM, "protocol", "threshold", "value")
                ap_detect_location = self.search(Config.SIM, "protocol", "threshold", "ap_detect_location")
            file_object.write(f"\nap_thresh = {ap_thresh:0.0f}\n")
            file_object.write(f"ap_detect_location  = {ap_detect_location:0.2f}\n")
            find_thresh = 0
            block_thresh_flag = 0
            amps = self.search(Config.SIM, "protocol", "amplitudes")
            num_amps = len(amps)
            file_object.write("\n//***************** Batching Parameters **********\n")
            file_object.write(f"Namp = {num_amps:0.0f}\n")
            file_object.write("objref stimamp_values\n")
            file_object.write(f"stimamp_values = new Vector(Namp,{0})\n")
            for amp_ind in range(num_amps):
                file_object.write(f"stimamp_values.x[{amp_ind:0.0f}] = {amps[amp_ind]:0.4f}\n")
        file_object.write(
            f"\nfind_thresh = {find_thresh} "
            "// find_thresh = 0 if not doing threshold search; "
            "find_thresh = 1 if looking for threshold\n"
        )
        file_object.write(
            f"find_block_thresh = {block_thresh_flag} "
            "// If find_thresh==1, can also set find_block_thresh = 1 "
            "to find block thresholds instead of activation threshold\n"
        )

    def write_saving(self, fiber_model_info, file_object):
        """Write the saving section of the hoc file.

        :param fiber_model_info: Dictionary containing information about the fiber model.
        :param file_object:  File object to write to.
        :raises ValueError: If AP end time locs are invalid
        """
        file_object.write("\n//***************** Recording ********************\n")
        if 'saving' not in self.configs[Config.SIM.value]:
            self.configs[Config.SIM.value]['saving'] = {
                "space": {"vm": False, "gating": False, "times": [0]},
                "time": {"vm": False, "gating": False, "istim": False, "locs": [0]},
                "runtimes": False,
            }
        else:
            pass
        file_object.write(
            f"saveflag_Vm_time      = {int(self.search(Config.SIM, 'saving', 'time', 'vm') is True):0.0f}\n"
        )
        file_object.write(
            f"saveflag_gating_time  = {int(self.search(Config.SIM, 'saving', 'time', 'gating') is True):0.0f}\n"
        )
        file_object.write(
            f"saveflag_Vm_space     = {int(self.search(Config.SIM, 'saving', 'space', 'vm') is True):0.0f}\n"
        )
        file_object.write(
            f"saveflag_gating_space = {int(self.search(Config.SIM, 'saving', 'space', 'gating') is True):0.0f}\n"
        )
        file_object.write(f"saveflag_Ve           = {int(False):0.0f}\n")
        file_object.write(
            f"saveflag_Istim        = {int(self.search(Config.SIM, 'saving', 'time', 'istim') is True):0.0f}\n"
        )
        if 'cap_recording' not in self.configs[Config.SIM.value]['saving']:
            file_object.write(f"saveflag_Imem         = {0}\n")
        else:
            file_object.write(
                f"saveflag_Imem         = "
                f"{int(self.search(Config.SIM, 'saving', 'cap_recording', 'Imembrane_matrix') is True):0.0f}\n"
            )
        if 'runtimes' not in self.configs[Config.SIM.value]['saving']:
            file_object.write(f"saveflag_runtime      = {0}\n")
        else:
            file_object.write(
                f"saveflag_runtime      = {int(self.search(Config.SIM, 'saving', 'runtimes') is True):0.0f}\n"
            )
        if 'aploctime' not in self.configs[Config.SIM.value]['saving']:
            file_object.write(f"saveflag_ap_loctime   = {0}\n")
        else:
            file_object.write(
                f"saveflag_ap_loctime   = {int(self.search(Config.SIM, 'saving', 'aploctime') is True):0.0f}\n"
            )
        if 'end_ap_times' in self.configs[Config.SIM.value]['saving']:
            loc_min = self.search(Config.SIM, "saving", "end_ap_times", "loc_min")
            loc_max = self.search(Config.SIM, "saving", "end_ap_times", "loc_max")

            if loc_min > loc_max:
                raise ValueError(
                    "ap_end_times is defined in Sim, so the system is saving AP times at the ends of the fiber. "
                    "The values defined in Sim violated loc_min > loc_max."
                )
            if not ((1 >= loc_min >= 0) and (1 >= loc_max >= 0)):
                raise ValueError(
                    "ap_end_times is defined in Sim. "
                    "The values for loc_min and loc_max defined in Sim are not in [0,1]."
                )
            if any([loc_min == 0, loc_min == 1, loc_max == 0, loc_max == 1]) and fiber_model_info.get(
                "passive_end_nodes"
            ):
                raise ValueError(
                    "ap_end_times is defined in Sim, so the system is saving AP times at the ends of the fiber. "
                    "The values for loc_min and/or loc_max are the terminal nodes  "
                    "(i.e., 0 or 1), which are also set to passive_end_nodes=1 (i.e., grounded therefore no APs)."
                )

            file_object.write(
                f"saveflag_end_ap_times = {1}\n\n"
            )  # if Sim has "ap_end_times" defined, then we are recording them
            file_object.write(f"loc_min_end_ap        = {loc_min:0.2f}\n")
            file_object.write(f"loc_max_end_ap        = {loc_max:0.2f}\n")
            file_object.write(
                f"ap_end_thresh         = {self.search(Config.SIM, 'saving', 'end_ap_times', 'threshold'):0.0f}\n"
            )

    def write_intracellular_stim(self, file_object):
        """Write the intracellular stimulation section of the hoc file.

        :param file_object: File object to write to.
        """
        file_object.write("\n//***************** Intracellular Stim ***********\n")
        # use for keys only, get params with self.search() for error throwing if missing them
        intracellular_stim: dict = self.search(Config.SIM, "intracellular_stim")
        file_object.write(
            f"IntraStim_PulseTrain_delay    = "
            f"{self.search(Config.SIM, 'intracellular_stim', 'times', 'IntraStim_PulseTrain_delay'):.2f} // [ms]\n"
        )
        file_object.write(
            f"IntraStim_PulseTrain_pw       = "
            f"{self.search(Config.SIM, 'intracellular_stim', 'times', 'pw'):.2f} // [ms]\n"
        )
        if "IntraStim_PulseTrain_dur" in intracellular_stim.get("times").values():
            file_object.write(
                f"IntraStim_PulseTrain_traindur = "
                f"{self.search(Config.SIM, 'intracellular_stim', 'times', 'IntraStim_PulseTrain_dur'):.2f} // [ms]\n"
            )
        else:
            file_object.write("IntraStim_PulseTrain_traindur = tstop - IntraStim_PulseTrain_delay // [ms]\n")
        file_object.write(
            f"IntraStim_PulseTrain_freq     = "
            f"{self.search(Config.SIM, 'intracellular_stim', 'pulse_repetition_freq'):.2f} // [Hz]\n"
        )
        file_object.write(
            f"IntraStim_PulseTrain_amp      = " f"{self.search(Config.SIM, 'intracellular_stim', 'amp'):0.4f} // [nA]\n"
        )
        file_object.write(
            f"IntraStim_PulseTrain_ind      = {self.search(Config.SIM, 'intracellular_stim', 'ind'):0.0f} "
            f"// Index of node where intracellular stim is placed [unitless]\n"
        )
