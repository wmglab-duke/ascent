import math

from src.utils import *


class SimulationBuilder(Exceptionable, Configurable, Saveable):
    def __init__(self, exception_config):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.add(SetupMode.NEW, Config.FIBER_Z, os.path.join('config', 'system', 'fiber_z.json'))

    def build_hoc(self):
        """
        Write file LaunchSim###.hoc
        :return:
        """

        fiber_types = self.search(Config.SIM, "fibers")
        for fiber_type_index, fiber_type in enumerate(fiber_types):
            # if myelinated - loop diameters

            # if CFiber - loop diameters and dx

            # search SIM config for parameters and assign to variables
            # see fiber manager 318 for template -- todo
            # search FIBER config for parameters and assign to variables

            file_object = open("Launch%0.0f.hoc" % fiber_type_index, "w")
            file_object.write("<HEADER> \n")

            # ENVIRONMENT
            file_object.write("\n//***************** Environment *****************\n")
            file_object.write("celsius = %0.0f // [degC]\n" % self.search(Config.MODEL, "temperature", "value"))

            # TIME PARAMETERS
            file_object.write("\n//***************** Time ************************\n")
            dt = self.search(Config.SIM, "extracellular_stim", "global", "dt")
            file_object.write("dt = %0.3f // [ms]\n" % dt)
            tstop = self.search(Config.SIM, "extracellular_stim", "global", "stop")
            file_object.write("tstop = %0.0f // [ms]\n" % tstop)
            n_tsteps = math.floor(tstop / dt) + 1
            file_object.write("n_tsteps = %0.0f // [unitless]\n" % n_tsteps)
            file_object.write("t_initSS = %0.0f // [ms]\n" % self.search(Config.SIM, "extracellular_stim", "global", "initSS"))
            file_object.write("dt_initSS = %0.0f // [ms]\n" % self.search(Config.SIM, "extracellular_stim", "global", "dt_initSS"))

            # FIBER PARAMETERS
            file_object.write("\n//***************** Fiber Parameters *************\n")
            fiber_model = fiber_type["type"]

            file_object.write("fiber_type = %0.0f "
                              "// fiber_type = 1 for unmyelinated; fiber_type = 2 for myelinated; "
                              "fiber_type = 3 for c fiber built from cFiberBuilder.hoc\n"
                              % self.search(Config.FIBER_Z,
                                            MyelinationMode.parameters.value,
                                            fiber_model,
                                            "fiber_type"))

            file_object.write("strdef fiber_type_str\n")
            file_object.write("fiber_type_str = \"%s\"\n" %
                              self.search(Config.FIBER_Z,
                                          MyelinationMode.parameters.value,
                                          fiber_model,
                                          "fiber_type_str"))

            file_object.write("node_channels = %0.0f "
                              "// node_channels = 0 for MRG; node_channels = 1 for Schild 1994\n" %
                              self.search(Config.FIBER_Z,
                                          MyelinationMode.parameters.value,
                                          fiber_model,
                                          "node_channels"))

            #  axonnodes - TODO, what is the dimension in fiber manager
            file_object.write("axonnodes = %0.0f "
                              "// must match up with ExtractPotentials\n" % 99999)

            file_object.write("passive_end_nodes = %0.0f "
                              "// passive_end_nodes = 1 to make both end nodes passive; 0 otherwise\n" %
                              self.search(Config.FIBER_Z,
                                          MyelinationMode.parameters.value,
                                          fiber_model,
                                          "passive_end_nodes"))

            #  fiberD - TODO, what is the diameter
            file_object.write("fiberD = %0.0f "
                              "// fiber diameter\n" % 99999)

            file_object.write("strdef fiberD_str\n")

            file_object.write("fiberD_str = \"%s\" // fiber diameter\n" % "TBD")

            file_object.write("\n//***************** Intracellular Stim ***********\n")
            file_object.write("IntraStim_PulseTrain_delay = %0.0f // [ms]\n" % self.search(Config.SIM, "intracellular_stim", "times", "IntraStim_PulseTrain_delay"))
            file_object.write("IntraStim_PulseTrain_pw = %0.0f // [ms]\n" % self.search(Config.SIM, "intracellular_stim", "times", "pw"))
            file_object.write("IntraStim_PulseTrain_traindur = tstop - IntraStim_PulseTrain_delay // [ms]\n")
            file_object.write("IntraStim_PulseTrain_freq = %0.0f // [ms]\n" % self.search(Config.SIM, "intracellular_stim", "freq", "value"))  # TODO unit?
            file_object.write("IntraStim_PulseTrain_amp = %0.4f // [nA]\n" % self.search(Config.SIM, "intracellular_stim", "amp", "value"))  # TODO unit?
            file_object.write("IntraStim_PulseTrain_ind = %0.0f "
                              "// Index of node where intracellular stim is placed [unitless]\n" %
                              self.search(Config.SIM, "intracellular_stim", "ind"))

            file_object.write("\n//***************** Extracellular Stim ***********\n")
            file_object.write("strdef VeTime_fname\n")
            file_object.write("VeTime_fname = \"%s\"\n" % "TBD")
            file_object.write("flag_extracellular_stim = %0.0f\n" % 1)

            file_object.write("\n//***************** Recording ********************\n")
            file_object.write("saveflag_Vm_time = %0.0f\n" % self.search(Config.SIM, "save_flags", "vm_time"))
            file_object.write("saveflag_gating_time = %0.0f\n" % self.search(Config.SIM, "save_flags", "gating_time"))
            file_object.write("saveflag_Vm_space = %0.0f\n" % self.search(Config.SIM, "save_flags", "vm_space"))
            file_object.write("saveflag_gating_space = %0.0f\n" % self.search(Config.SIM, "save_flags", "gating_space"))
            file_object.write("saveflag_Ve = %0.0f\n" % self.search(Config.SIM, "save_flags", "ve"))
            file_object.write("saveflag_Istim = %0.0f\n" % self.search(Config.SIM, "save_flags", "istim"))

            file_object.write("\n//***************** Classification Checkpoints ***\n")
            file_object.write("Nchecknodes = %0.0f\n" % self.search(Config.SIM, "check_points", "n_checknodes"))
            file_object.write("Nchecktimes = %0.0f\n" % self.search(Config.SIM, "check_points", "n_checktimes"))

            file_object.write("\n//***************** Threshold Parameters *********\n")
            file_object.write("find_thresh = %0.0f "
                              "// find_thresh = 0 if not doing threshold search; "
                              "find_thresh = 1 if looking for threshold\n"
                              % self.search(Config.SIM,
                                            "threshold",
                                            "thresh"))
            file_object.write("find_block_thresh = %0.0f "
                              "// If find_thresh==1, can also set find_block_thresh = 1 "
                              "to find block thresholds instead of activation threshold\n"
                              % self.search(Config.SIM,
                                            "threshold",
                                            "block_thresh"))

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

            file_object.write("\nap_thresh = %0.0f\n" % self.search(Config.SIM, "threshold", "thresh"))
            file_object.write("N_minAPs  = %0.0f\n" % self.search(Config.SIM, "threshold", "n_min_aps"))
            file_object.write("\nflag_whichstim  = %0.0f\n" % 0)

            file_object.write("\n//***************** Batching Parameters **********\n")
            amps = [0, 1]  # todo
            Namp = len(amps)
            freqs = [20]  # todo
            Nfreq = len(freqs)

            file_object.write("Nmodels = %0.0f\n" % 1)
            file_object.write("ModelNum = %0.0f\n" % 0)  # todo
            file_object.write("Nfasc = %0.0f\n" % 0)  # todo
            file_object.write("Namp = %0.0f\n" % len(amps))
            file_object.write("Nfreq  = %0.0f\n" % len(freqs))
            file_object.write("\nobjref stimamp_values\n")
            file_object.write("stimamp_values = new Vector(Namp,%0.0f)\n" % 0)
            for amp in range(len(amps)):
                file_object.write("stimamp_values.x[%0.0f] = %0.0f\n" % (amp, 0))

            file_object.write("\nobjref Vefreq_values\n")
            file_object.write("Vefreq_values = new Vector(Nfreq,%0.0f)\n" % 0)
            for freq in range(len(freqs)):
                file_object.write("Vefreq_values.x[%0.0f] = %0.0f\n" % (freq, 0))

            file_object.write("\nload_file(\"Wrapper_block.hoc\")\n")  # todo

                # fiberD
            # fiberD_str
            # if C Fiber then dz and len too

            file_object.close()

    def build_slurm(self):
        """
        Write file StartSim###.slurm
        :return:
        """
        pass
