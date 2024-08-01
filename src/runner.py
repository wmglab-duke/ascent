#!/usr/bin/env python3.7

"""Defines the runner module.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import base64
import json
import os
import pickle
import subprocess
import sys
import time
import warnings

import numpy as np

from src.core import Model, Sample, Simulation
from src.utils import (
    Config,
    Configurable,
    Env,
    ExportMode,
    IncompatibleParametersError,
    JavaError,
    SetupMode,
    WriteMode,
)


class Runner(Configurable):
    """Control flow of the pipeline."""

    def __init__(self, number: int):
        """Initialize Runner class.

        :param number: number of this run
        """
        # initialize Configurable super class
        Configurable.__init__(self)

        # this corresponds to the run index (as file name in config/user/runs/<run_index>.json
        self.ss_bases_exist = None
        self.bases_potentials_exist = None
        self.number = number

    def load_configs(self) -> dict:
        """Load all configuration files into class.

        :raises TypeError: if sample is not int
        :return: dictionary of all configs (Sample, Model(s), Sims(s))
        """

        def validate_and_add(config_source: dict, key: str, path: str):
            """Validate and add config to class.

            :param config_source: all configs, to which we add new ones
            :param key: the key of the dict in Configs
            :param path: path to the JSON file of the config
            :raises FileNotFoundError: if config file not found
            """
            self.validate_path(path)
            if os.path.exists(path):
                if key not in config_source:
                    config_source[key] = []
                config_source[key] += [self.load(path)]
            else:
                raise FileNotFoundError(f"Missing {key} config required by run configuration! ({path})")

        configs = {}

        sample = self.search(Config.RUN, 'sample')

        if not isinstance(sample, int):
            raise TypeError(
                "Sample parameter in run must be an integer. Each Run must be associated with a single Sample."
            )

        models = self.search(Config.RUN, 'models', optional=True)
        sims = self.search(Config.RUN, 'sims', optional=True)

        sample_path = os.path.join(os.getcwd(), 'samples', str(sample), 'sample.json')
        validate_and_add(configs, 'sample', sample_path)

        model_paths = [
            os.path.join(os.getcwd(), 'samples', str(sample), 'models', str(model), 'model.json') for model in models
        ]

        for model_path in model_paths:
            validate_and_add(configs, 'models', model_path)

        sim_paths = [os.path.join(os.getcwd(), 'config', 'user', 'sims', f'{sim}.json') for sim in sims]
        for sim_path in sim_paths:
            validate_and_add(configs, 'sims', sim_path)

        return configs

    def load_obj(self, path: str):
        """Load object from file.

        :param path: path to python obj file
        :return: obj file
        """
        with open(path, 'rb') as o:
            obj = pickle.load(o)
        obj.add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value])
        return obj

    def setup_run(self):
        """Perform all setup steps for a run.

        :return: Dictionary of all configs
        """
        run_pseudonym = self.configs[Config.RUN.value].get('pseudonym')
        if run_pseudonym is not None:
            print('Run pseudonym:', run_pseudonym)

        # ensure NEURON files exist in export location
        Simulation.export_neuron_files(os.environ[Env.NSIM_EXPORT_PATH.value])
        Simulation.export_system_config_files(os.path.join(os.environ[Env.NSIM_EXPORT_PATH.value], 'config', 'system'))

        for deprecated_key in ['break_points', 'local_avail_cpus', 'submission_context', 'partial_fem']:
            if deprecated_key in self.configs[Config.RUN.value]:
                warnings.warn(
                    f"Specifying {deprecated_key} in run.json is deprecated, and has no effect.", stacklevel=2
                )

        # load all json configs into memory
        return self.load_configs()

    def generate_sample(self, all_configs, smart=True):
        """Generate the sample object for this run.

        :param all_configs: all configs for this run
        :param smart: if True, reuse objects from previous runs
        :return: (sample object, sample number)
        """
        sample_num = self.configs[Config.RUN.value]['sample']

        sample_file = os.path.join(os.getcwd(), 'samples', str(sample_num), 'sample.obj')

        sample_pseudonym = all_configs[Config.SAMPLE.value][0].get('pseudonym')

        print(
            f"SAMPLE {self.configs[Config.RUN.value]['sample']}",
            f'- {sample_pseudonym}' if sample_pseudonym is not None else '',
        )

        # instantiate sample
        if smart and os.path.exists(sample_file):
            print(f"Found existing sample {self.configs[Config.RUN.value]['sample']} ({sample_file})")
            sample = self.load_obj(sample_file)
        else:
            # init slide manager
            sample = Sample()
            # run processes with slide manager (see class for details)

            sample.add(SetupMode.OLD, Config.SAMPLE, all_configs[Config.SAMPLE.value][0]).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]).init_map(
                SetupMode.OLD
            ).build_file_structure().populate().write(
                WriteMode.SECTIONWISE2D
            ).output_morphology_data().save(
                sample_file
            )

        return sample, sample_num

    def prep_model(self, all_configs, model_index, model_config, sample, sample_num, smart=True):
        """Prepare model prior to handoff to Java.

        :param all_configs: all configs for this run
        :param model_index: index of model
        :param model_config: config for this model
        :param sample: sample object
        :param sample_num: sample number
        :param smart: if True, reuse objects from previous runs
        :return: model number
        """
        model_num = self.configs[Config.RUN.value]['models'][model_index]
        model_pseudonym = model_config.get('pseudonym')
        model_file = os.path.join(os.getcwd(), 'samples', str(sample_num), 'models', str(model_num), 'model.obj')
        model_config_file = os.path.join(
            os.getcwd(), 'samples', str(sample_num), 'models', str(model_num), 'model.json'
        )
        print(f'\tMODEL {model_num}', f'- {model_pseudonym}' if model_pseudonym is not None else '')
        if smart and os.path.exists(model_file):
            print(f"\tFound existing model {model_num} ({model_file})")
            model: Model = self.load_obj(model_file)
            if isinstance(
                model.configs['models']['cuff'], dict
            ):  # Indicates that model.obj was built before ascent had multi-cuff functionality
                if "index" not in model.configs['models']['cuff']:  # If no cuff index is provided
                    warnings.warn(
                        'No "cuff" -> "index" provided in model.json. Assigning cuff index to 0.', stacklevel=2
                    )
                    model.configs['models']['cuff']['index'] = 0
                # Update model cuffs with new list structure
                model.configs['models']['cuff'] = [model.configs['models']['cuff']]  # cast to list

                # Save to files for future runs
                model.write(model_config_file)
                model.save(model_file)

        else:
            model = Model()
            # use current model index to computer maximum cuff shift (radius) .. SAVES to file in method
            model.add(SetupMode.OLD, Config.MODEL, model_config).add(SetupMode.OLD, Config.SAMPLE, sample).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]).compute_cuff_shift(
                sample, all_configs[Config.SAMPLE.value][0]
            ).compute_electrical_parameters().validate().write(
                model_config_file
            ).save(
                model_file
            )

        return model_num

    def sim_setup(self, sim_index, sim_config, sample_num, model_num, smart, sample, model_config):
        """Create simulation object and prepare for generation of NEURON sims.

        :param sim_index: index of sim
        :param sim_config: config for this sim
        :param sample_num: sample number
        :param model_num: model number
        :param smart: if True, use existing objects
        :param sample: sample object
        :param model_config: config for this model
        :return: simulation object, directory of sim
        """
        sim_num = self.configs[Config.RUN.value]['sims'][sim_index]
        sim_pseudonym = sim_config.get('pseudonym')
        print(
            f"\t\tSIM {self.configs[Config.RUN.value]['sims'][sim_index]}",
            f'- {sim_pseudonym}' if sim_pseudonym is not None else '',
        )

        sim_obj_dir = os.path.join(
            os.getcwd(), 'samples', str(sample_num), 'models', str(model_num), 'sims', str(sim_num)
        )

        sim_obj_file = os.path.join(sim_obj_dir, 'sim.obj')

        # init fiber manager
        if smart and os.path.exists(sim_obj_file):
            print(f'\t\tFound existing sim object for sim {sim_num} ({sim_obj_file})')

            simulation: Simulation = self.load_obj(sim_obj_file)

        else:
            os.makedirs(sim_obj_dir + '/plots', exist_ok=True)
            simulation: Simulation = Simulation(sample)
            simulation.add(SetupMode.OLD, Config.MODEL, model_config).add(SetupMode.OLD, Config.SIM, sim_config).add(
                SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]
            ).add(
                SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]
            ).resolve_factors().write_waveforms(
                sim_obj_dir
            ).write_fibers(
                sim_obj_dir
            ).validate_srcs(
                sim_obj_dir
            ).save(
                sim_obj_file
            )
        return simulation, sim_obj_dir

    def validate_supersample(self, simulation, sample_num, model_num):
        """Validate supersampling parameters.

        :param simulation: simulation object
        :param sample_num: sample number
        :param model_num: model number
        :raises FileNotFoundError: if source_sim object is not found
        :raises IncompatibleParametersError: If supersampled xy does not match source xy
        :return: directory of source simulation
        """
        source_sim_index = simulation.configs['sims']['supersampled_bases']['source_sim']

        source_sim_obj_dir = os.path.join(
            os.getcwd(), 'samples', str(sample_num), 'models', str(model_num), 'sims', str(source_sim_index)
        )

        # do Sim.fibers.xy_parameters match between Sim and source_sim?
        try:
            source_sim: simulation = self.load_obj(os.path.join(source_sim_obj_dir, 'sim.obj'))
            print(f'\t    Found existing source sim {source_sim_index} for supersampled bases ({source_sim_obj_dir})')
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Could not load indicated super-sampled sim object (source sim: {source_sim_index})."
                f"Original error: {e}"
            )

        source_xy_dict: dict = source_sim.configs['sims']['fibers']['xy_parameters']
        xy_dict: dict = simulation.configs['sims']['fibers']['xy_parameters']

        if source_xy_dict != xy_dict:
            raise IncompatibleParametersError(
                "Trying to use super-sampled potentials that do not match your Sim's xy_parameters perfectly"
            )
        return source_sim_obj_dir

    def generate_nsims(self, sim_index, model_num, sample_num):
        """Generate NEURON simulations.

        :param sim_index: index of sim
        :param model_num: model number
        :param sample_num: sample number
        :raises ValueError: if export behavior is not supported
        """
        sim_num = self.configs[Config.RUN.value]['sims'][sim_index]
        sim_obj_path = os.path.join(
            os.getcwd(),
            'samples',
            str(self.configs[Config.RUN.value]['sample']),
            'models',
            str(model_num),
            'sims',
            str(sim_num),
            'sim.obj',
        )

        sim_dir = os.path.join(
            os.getcwd(), 'samples', str(self.configs[Config.RUN.value]['sample']), 'models', str(model_num), 'sims'
        )

        # load up correct simulation and build required sims
        simulation: Simulation = self.load_obj(sim_obj_path)
        simulation.build_n_sims(sim_dir, sim_num)

        # get export behavior
        if self.configs[Config.CLI_ARGS.value].get('export_behavior') is not None:
            export_behavior = self.configs[Config.CLI_ARGS.value]['export_behavior']
        elif self.configs[Config.RUN.value].get('export_behavior') is not None:
            export_behavior = self.configs[Config.RUN.value]['export_behavior']
        else:
            export_behavior = 'selective'
        # check to make sure we have a valid behavior
        if not np.any([export_behavior == x.value for x in ExportMode]):
            raise ValueError("Invalid export behavior defined in run.json")

        # export simulations
        Simulation.export_n_sims(
            sample_num,
            model_num,
            sim_num,
            sim_dir,
            os.environ[Env.NSIM_EXPORT_PATH.value],
            export_behavior=export_behavior,
        )

        # ensure run configuration is present
        Simulation.export_run(self.number, os.environ[Env.PROJECT_PATH.value], os.environ[Env.NSIM_EXPORT_PATH.value])

    def run(self, smart: bool = True):
        """Run the pipeline.

        :param smart: bool telling the program whether to reprocess the sample or not if it already exists as sample.obj
        :return: nothing to memory, spits out all pipeline related data to file
        """
        # NOTE: single sample per Runner, so no looping of samples
        #       possible addition of functionality for looping samples in start.py

        all_configs = self.setup_run()

        self.bases_potentials_exist: list[bool] = []  # if all of these are true, skip Java
        self.ss_bases_exist: list[bool] = []  # if all of these are true, skip Java

        sample, sample_num = self.generate_sample(all_configs, smart=smart)

        # iterate through models
        if 'models' not in all_configs:
            print('NO MODELS TO MAKE IN Config.RUN - killing process')
        else:
            for model_index, model_config in enumerate(all_configs[Config.MODEL.value]):
                # loop through each model
                model_num = self.prep_model(all_configs, model_index, model_config, sample, sample_num, smart=smart)
                if 'sims' in all_configs:
                    # iterate through simulations
                    for sim_index, sim_config in enumerate(all_configs['sims']):
                        # generate simulation object
                        simulation, sim_obj_dir = self.sim_setup(
                            sim_index, sim_config, sample_num, model_num, smart, sample, model_config
                        )

                        # CHECK IF POTENTIALS EXIST FOR EACH FIBERSET X BASIS
                        # DON'T NEED POTENTIALS TO EXIST IF WE ARE USING SUPER SAMPLED ONES
                        if (
                            'supersampled_bases' not in simulation.configs['sims']
                            or not simulation.configs['sims']['supersampled_bases']['use']
                        ):
                            self.bases_potentials_exist.append(simulation.bases_potentials_exist(sim_obj_dir))

                        # CHECK IF THE SUPERSAMPLED BASES EXIST FOR EACH BASIS
                        # check if supersampled bases exist and if so, validate supersampling parameters
                        if 'supersampled_bases' in simulation.configs['sims']:
                            if simulation.configs['sims']['supersampled_bases']['generate']:
                                self.ss_bases_exist.append(simulation.ss_bases_exist(sim_obj_dir))
                            if simulation.configs['sims']['supersampled_bases']['use']:
                                source_sim_obj_dir = self.validate_supersample(simulation, sample_num, model_num)
                                self.ss_bases_exist.append(simulation.ss_bases_exist(source_sim_obj_dir))

            if self.configs[Config.CLI_ARGS.value].get('break_point') == 'pre_java' or (
                ('break_points' in self.configs[Config.RUN.value])
                and self.search(Config.RUN, 'break_points').get('pre_java') is True
            ):
                print('KILLING PRE JAVA')
                return

            # handoff (to Java) -  Build/Mesh/Solve/Save bases; Extract/Save potentials if necessary
            if 'models' in all_configs and 'sims' in all_configs:
                # only transition to java if necessary (there are potentials that do not exist)
                if not all(self.bases_potentials_exist) or not all(self.ss_bases_exist):
                    print('\nTO JAVA\n')
                    self.handoff(self.number)
                    print('\nTO PYTHON\n')
                else:
                    print('\nSKIPPING JAVA - all required extracted potentials already exist\n')

                self.remove(Config.RUN)
                run_path = os.path.join('config', 'user', 'runs', f'{self.number}.json')
                self.add(SetupMode.NEW, Config.RUN, run_path)

                #  continue by using simulation objects
                models_exit_status = self.search(Config.RUN, "models_exit_status")

                for model_index, _model_config in enumerate(all_configs[Config.MODEL.value]):
                    model_num = self.configs[Config.RUN.value]['models'][model_index]
                    conditions = [
                        models_exit_status is not None,
                        len(models_exit_status) > model_index,
                    ]
                    model_ran = models_exit_status[model_index] if all(conditions) else True
                    ss_use_notgen = [
                        (
                            'supersampled_bases' in sim_config
                            and sim_config['supersampled_bases']['use']
                            and not sim_config['supersampled_bases']['generate']
                        )
                        for sim_config in all_configs['sims']
                    ]

                    if model_ran or np.all(ss_use_notgen):
                        for sim_index, _sim_config in enumerate(all_configs['sims']):
                            # generate output neuron sims
                            self.generate_nsims(sim_index, model_num, sample_num)
                        print(
                            f'Model {model_num} data exported to appropriate '
                            f'folders in {os.environ[Env.NSIM_EXPORT_PATH.value]}'
                        )

                    elif not models_exit_status[model_index]:
                        print(
                            f'\nDid not create NEURON simulations for Sims associated with: \n'
                            f'\t Model Index: {model_num} \n'
                            f'since COMSOL failed to create required potentials. \n'
                        )

            elif 'models' in all_configs and 'sims' not in all_configs:
                # Model Configs Provided, but not Sim Configs
                print('\nTO JAVA\n')
                self.handoff(self.number)
                print('\nNEURON Simulations NOT created since no Sim indices indicated in Config.SIM\n')

    def handoff(self, run_number: int, class_name='ModelWrapper'):
        """Handoff to Java.

        :param run_number: int, run number
        :param class_name: str, class name of Java class to run
        :raises JavaError: if Java fails to run
        """
        comsol_path = os.environ[Env.COMSOL_PATH.value]
        jdk_path = os.environ[Env.JDK_PATH.value]
        project_path = os.environ[Env.PROJECT_PATH.value]
        run_path = os.path.join(project_path, 'config', 'user', 'runs', f'{run_number}.json')

        # Encode command line args as jason string, then encode to base64 for passing to java
        argstring = json.dumps(self.configs[Config.CLI_ARGS.value])
        argbytes = argstring.encode('ascii')
        argbase = base64.b64encode(argbytes)
        argfinal = argbase.decode('ascii')

        if sys.platform.startswith('win'):  # windows
            server_command = [f'{comsol_path}\\bin\\win64\\comsolmphserver.exe', '-login', 'auto']
            compile_command = (
                f'""{jdk_path}\\javac" '
                f'-cp "..\\bin\\json-20190722.jar";"{comsol_path}\\plugins\\*" '
                f'model\\*.java -d ..\\bin"'
            )
            java_command = (
                f'""{comsol_path}\\java\\win64\\jre\\bin\\java" '
                f'-cp "{comsol_path}\\plugins\\*";"..\\bin\\json-20190722.jar";"..\\bin" '
                f'model.{class_name} "{project_path}" "{run_path}" "{argfinal}""'
            )
        else:
            server_command = [f'{comsol_path}/bin/comsol', 'mphserver', '-login', 'auto']

            compile_command = (
                f'{jdk_path}/javac -classpath ../bin/json-20190722.jar:'
                f'{comsol_path}/plugins/* model/*.java -d ../bin'
            )
            if sys.platform.startswith('linux'):  # linux
                java_comsol_path = comsol_path + '/java/glnxa64/jre/bin/java'
            else:  # mac
                java_comsol_path = comsol_path + '/java/maci64/jre/Contents/Home/bin/java'

            java_command = (
                f'{java_comsol_path} '
                f'-cp .:$(echo {comsol_path}/plugins/*.jar | '
                f'tr \' \' \':\'):../bin/json-20190722.jar:'
                f'../bin model.{class_name} "{project_path}" "{run_path}" "{argfinal}"'
            )

        # start comsol server
        subprocess.Popen(server_command, close_fds=True)
        # wait for server to start
        time.sleep(10)
        os.chdir('src')
        # compile java code
        exit_code = os.system(compile_command)
        if exit_code != 0:
            raise JavaError("Java compiler (javac) encountered an error during compilation operations.")
        # run java code
        exit_code = os.system(java_command)
        if exit_code != 0:
            raise JavaError("Encountered an error during handoff to java.")
        os.chdir('..')

    def populate_env_vars(self):
        """Get environment variables from config file.

        :raises FileNotFoundError: if environment variable file not found
        """
        if Config.ENV.value not in self.configs:
            raise FileNotFoundError("Missing environment variables configuration file")

        for key in Env.vals.value:
            value = self.search(Config.ENV, key)
            assert type(value) is str
            os.environ[key] = value
