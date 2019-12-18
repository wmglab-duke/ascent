import math

from src.utils import *


class SimulationBuilder(Exceptionable, Configurable, Saveable):
    def __init__(self, exception_config):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

    def build_hoc(self):
        """
        Write file LaunchSim###.hoc
        :return:
        """
        file_object = open("Launch.hoc", "w")
        file_object.write("<HEADER> \n")

        # ENVIRONMENT
        file_object.write("//***************** Environment *****************\n")
        file_object.write("celsius = %0.0f // [degC]\n\n" % self.search(Config.MODEL, "temperature", "value"))

        # TIME PARAMETERS
        file_object.write("//***************** Time ************************\n")
        dt = self.search(Config.SIM, "extracellular_stim", "global", "dt")
        file_object.write("dt = %0.3f // [ms]\n" % dt)

        tstop = self.search(Config.SIM, "extracellular_stim", "global", "stop")
        file_object.write("tstop = %0.0f // [ms]\n" % tstop)

        n_tsteps = math.floor(tstop / dt) + 1
        file_object.write("n_tsteps = %0.0f // [unitless]\n" % n_tsteps)

        file_object.write("t_initSS = %0.0f // [ms]\n" % self.search(Config.SIM, "extracellular_stim", "global", "initSS"))

        file_object.write("dt_initSS = %0.0f // [ms]\n\n" % self.search(Config.SIM, "extracellular_stim", "global", "dt_initSS"))

        # FIBER PARAMETERS
        file_object.write("//***************** Fiber Parameters *************\n")

        myel_modes = self.search(Config.SIM, "modes", "myel")
        myel_fiber_modes = self.search(Config.SIM, "modes", "myel_fiber")
        print(myel_modes[0])
        print(myel_fiber_modes[0])
        print(MyelinationMode.UNMYELINATED)
        print(MyelinationMode.MYELINATED)

        if myel_modes[0] == MyelinationMode.UNMYELINATED:  # TODO
            print("here1")
            fiber_type = 3
            fiber_type_str = "CFiber"
        elif myel_modes[0] == MyelinationMode.MYELINATED:
            print("here2")
            fiber_type = 2
            if myel_fiber_modes[0] == MyelinatedFiberType.MRG_DISCRETE:
                fiber_type_str = "MRG_DISCRETE"
            elif myel_fiber_modes[0] == MyelinatedFiberType.MRG_INTERPOLATION:
                fiber_type_str = "MRGInterp"
            elif myel_fiber_modes[0] == MyelinatedFiberType.B_FIBER:
                fiber_type_str = "B"

        print(fiber_type)
        print("here")
        file_object.write("fiber_type = %0.0f "
                          "// fiber_type = 1 for unmyelinated; fiber_type = 2 for myelinated; "
                          "fiber_type = 3 for c fiber built from cFiberBuilder.hoc\n"
                          % fiber_type)

        file_object.write("strdef fiber_type_str\n")
        file_object.write("fiber_type_str = %s\n" % fiber_type_str)

        file_object.close()

    def build_slurm(self):
        """
        Write file StartSim###.slurm
        :return:
        """
        pass
