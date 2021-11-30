#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# builtins
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pickle
from typing import List

# packages
import json
import base64
import sys
import numpy as np
import subprocess
from copy import deepcopy
from quantiphy import Quantity
from shapely.geometry import Point
import pymunkoptions

pymunkoptions.options["debug"] = False

# ascent
from src.core import Sample, Simulation, Waveform
from src.utils import Exceptionable, Configurable, SetupMode, Config, NerveMode, DownSampleMode, WriteMode, \
    CuffShiftMode, PerineuriumResistivityMode, TemplateOutput, Env, ReshapeNerveMode


class Runner(Exceptionable, Configurable):

    def __init__(self, number: int):

        # initialize Configurable super class
        Configurable.__init__(self)

        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW)

        # this corresponds to the run index (as file name in config/user/runs/<run_index>.json
        self.number = number

    def load_configs(self) -> dict:
        """
        :return: dictionary of all configs (Sample, Model(s), Sims(s))
        """

        def validate_and_add(config_source: dict, key: str, path: str):
            """
            :param config_source: all configs, to which we add new ones
            :param key: the key of the dict in Configs
            :param path: path to the JSON file of the config
            :return: updated dict of all configs
            """
            self.validate_path(path)
            if os.path.exists(path):
                if key not in config_source.keys():
                    config_source[key] = []
                config_source[key] += [self.load(path)]
            else:
                print('Missing {} config: {}'.format(key, path))
                self.throw(37)

        configs = dict()

        sample = self.search(Config.RUN, 'sample')

        if not isinstance(sample, int):
            self.throw(95)

        models = self.search(Config.RUN, 'models', optional=True)
        sims = self.search(Config.RUN, 'sims', optional=True)

        sample_path = os.path.join(
            os.getcwd(),
            'samples',
            str(sample),
            'sample.json'
        )
        validate_and_add(configs, 'sample', sample_path)

        model_paths = [os.path.join(os.getcwd(),
                                    'samples',
                                    str(sample),
                                    'models',
                                    str(model),
                                    'model.json') for model in models]

        for model_path in model_paths:
            validate_and_add(configs, 'models', model_path)

        sim_paths = [os.path.join(os.getcwd(),
                                  'config',
                                  'user',
                                  'sims',
                                  '{}.json'.format(sim)) for sim in sims]
        for sim_path in sim_paths:
            validate_and_add(configs, 'sims', sim_path)

        return configs

    def run(self, smart: bool = True):
        """
        :param smart: bool telling the program whether to reprocess the sample or not if it already exists as sample.obj
        :return: nothing to memory, spits out all pipeline related data to file
        """
        # NOTE: single sample per Runner, so no looping of samples
        #       possible addition of functionality for looping samples in start.py

        # load all json configs into memory
        all_configs = self.load_configs()

        def load_obj(path: str):
            """
            :param path: path to python obj file
            :return: obj file
            """
            return pickle.load(open(path, 'rb')).add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value])

        # ensure NEURON files exist in export location
        Simulation.export_neuron_files(os.environ[Env.NSIM_EXPORT_PATH.value])
        Simulation.export_system_config_files(os.path.join(os.environ[Env.NSIM_EXPORT_PATH.value], 'config', 'system'))

        if 'break_points' in self.configs[Config.RUN.value].keys() and \
                sum(self.search(Config.RUN, 'break_points').values()) > 1:
            self.throw(76)

        if 'partial_fem' in self.configs[Config.RUN.value].keys() and \
                sum(self.search(Config.RUN, 'partial_fem').values()) > 1:
            self.throw(80)

        potentials_exist: List[bool] = []  # if all of these are true, skip Java
        ss_bases_exist: List[bool] = []  # if all of these are true, skip Java

        sample_num = self.configs[Config.RUN.value]['sample']

        sample_file = os.path.join(
            os.getcwd(),
            'samples',
            str(sample_num),
            'sample.obj'
        )

        print('SAMPLE {}'.format(self.configs[Config.RUN.value]['sample']))

        # instantiate sample
        if smart and os.path.exists(sample_file):
            print('Found existing sample {} ({})'.format(self.configs[Config.RUN.value]['sample'], sample_file))
            sample = load_obj(sample_file)
        else:
            # init slide manager
            sample = Sample(self.configs[Config.EXCEPTIONS.value])
            # run processes with slide manager (see class for details)

            sample \
                .add(SetupMode.OLD, Config.SAMPLE, all_configs[Config.SAMPLE.value][0]) \
                .add(SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]) \
                .add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]) \
                .init_map(SetupMode.OLD) \
                .build_file_structure() \
                .populate(deform_animate=False) \
                .write(WriteMode.SECTIONWISE2D) \
                .output_morphology_data() \
                .save(os.path.join(sample_file))

        # iterate through models
        if 'models' not in all_configs.keys():
            print('NO MODELS TO MAKE IN Config.RUN - killing process')
            pass
        else:
            for model_index, model_config in enumerate(all_configs[Config.MODEL.value]):
                model_num = self.configs[Config.RUN.value]['models'][model_index]
                print('    MODEL {}'.format(model_num))

                # use current model index to computer maximum cuff shift (radius) .. SAVES to file in method
                model_config = self.compute_cuff_shift(model_config, sample, all_configs[Config.SAMPLE.value][0])

                model_config_file_name = os.path.join(
                    os.getcwd(),
                    'samples',
                    str(sample_num),
                    'models',
                    str(model_num),
                    'model.json'
                )

                # write edited model config in place
                TemplateOutput.write(model_config, model_config_file_name)

                # use current model index to compute electrical parameters ... SAVES to file in method
                self.compute_electrical_parameters(all_configs, model_index)

                # iterate through simulations
                if 'sims' in all_configs.keys():
                    for sim_index, sim_config in enumerate(all_configs['sims']):
                        sim_num = self.configs[Config.RUN.value]['sims'][sim_index]
                        print('        SIM {}'.format(self.configs[Config.RUN.value]['sims'][sim_index]))
                        sim_obj_dir = os.path.join(
                            os.getcwd(),
                            'samples',
                            str(sample_num),
                            'models',
                            str(model_num),
                            'sims',
                            str(sim_num)
                        )

                        sim_obj_file = os.path.join(
                            sim_obj_dir,
                            'sim.obj'
                        )

                        # init fiber manager
                        if smart and os.path.exists(sim_obj_file):
                            print('\t    Found existing sim object for sim {} ({})'.format(
                                self.configs[Config.RUN.value]['sims'][sim_index], sim_obj_file))

                            simulation: Simulation = load_obj(sim_obj_file)
                            potentials_exist.append(simulation.potentials_exist(sim_obj_dir))

                            if 'supersampled_bases' in simulation.configs['sims'].keys():
                                if simulation.configs['sims']['supersampled_bases']['use']:
                                    source_sim = simulation.configs['sims']['supersampled_bases']['source_sim']

                                    source_sim_obj_dir = os.path.join(
                                        os.getcwd(),
                                        'samples',
                                        str(sample_num),
                                        'models',
                                        str(model_num),
                                        'sims',
                                        str(source_sim)
                                    )

                                    # do Sim.fibers.xy_parameters match between Sim and source_sim?
                                    source_sim: simulation = load_obj(os.path.join(source_sim_obj_dir, 'sim.obj'))
                                    source_xy_dict: dict = source_sim.configs['sims']['fibers']['xy_parameters']
                                    xy_dict: dict = simulation.configs['sims']['fibers']['xy_parameters']

                                    if not source_xy_dict == xy_dict:
                                        self.throw(82)

                                    ss_bases_exist.append(
                                        simulation.ss_bases_exist(source_sim_obj_dir)
                                    )

                        else:
                            if not os.path.exists(sim_obj_dir):
                                os.makedirs(sim_obj_dir)
                            
                            if not os.path.exists(sim_obj_dir+'/plots'):
                                os.makedirs(sim_obj_dir+'/plots')

                            simulation: Simulation = Simulation(sample, self.configs[Config.EXCEPTIONS.value])
                            simulation \
                                .add(SetupMode.OLD, Config.MODEL, model_config) \
                                .add(SetupMode.OLD, Config.SIM, sim_config) \
                                .add(SetupMode.OLD, Config.CLI_ARGS, self.configs[Config.CLI_ARGS.value]) \
                                .resolve_factors() \
                                .write_waveforms(sim_obj_dir) \
                                .write_fibers(sim_obj_dir) \
                                .validate_srcs(sim_obj_dir) \
                                .save(sim_obj_file)

                            potentials_exist.append(simulation.potentials_exist(sim_obj_dir))

                            if 'supersampled_bases' in simulation.configs['sims'].keys():
                                if simulation.configs['sims']['supersampled_bases']['use']:
                                    source_sim = simulation.configs['sims']['supersampled_bases']['source_sim']

                                    source_sim_obj_dir = os.path.join(
                                        os.getcwd(),
                                        'samples',
                                        str(sample_num),
                                        'models',
                                        str(model_num),
                                        'sims',
                                        str(source_sim)
                                    )

                                    # do Sim.fibers.xy_parameters match between Sim and source_sim?
                                    source_sim: simulation = load_obj(os.path.join(sim_obj_dir, 'sim.obj'))
                                    source_xy_dict: dict = source_sim.configs['sims']['fibers']['xy_parameters']
                                    xy_dict: dict = simulation.configs['sims']['fibers']['xy_parameters']

                                    if not source_xy_dict == xy_dict:
                                        self.throw(82)

                                    ss_bases_exist.append(
                                        simulation.ss_bases_exist(source_sim_obj_dir)
                                    )
            if self.configs[Config.CLI_ARGS.value].get('break_point')=='pre_java' or \
                    (('break_points' in self.configs[Config.RUN.value].keys()) and \
                     self.search(Config.RUN, 'break_points').get('pre_java')==True):
                print('KILLING PRE JAVA')
                sys.exit()

            # handoff (to Java) -  Build/Mesh/Solve/Save bases; Extract/Save potentials if necessary
            if 'models' in all_configs.keys() and 'sims' in all_configs.keys():
                self.model_parameter_checking(all_configs)
                # only transition to java if necessary (there are potentials that do not exist)
                if not all(potentials_exist) or not all(ss_bases_exist):
                    print('\nTO JAVA\n')
                    self.handoff(self.number)
                    print('\nTO PYTHON\n')
                else:
                    print('\nSKIPPING JAVA - all required extracted potentials already exist\n')

                self.remove(Config.RUN)
                run_path = os.path.join('config', 'user', 'runs', '{}.json'.format(self.number))
                self.add(SetupMode.NEW, Config.RUN, run_path)
                                
                #  continue by using simulation objects
                models_exit_status = self.search(Config.RUN, "models_exit_status")

                for model_index, model_config in enumerate(all_configs[Config.MODEL.value]):
                    model_num = self.configs[Config.RUN.value]['models'][model_index]
                    conditions = [models_exit_status is not None, len(models_exit_status) > model_index]
                    if models_exit_status[model_index] if all(conditions) else True:
                        for sim_index, sim_config in enumerate(all_configs['sims']):
                            sim_num = self.configs[Config.RUN.value]['sims'][sim_index]
                            sim_obj_path = os.path.join(
                                os.getcwd(),
                                'samples',
                                str(self.configs[Config.RUN.value]['sample']),
                                'models',
                                str(model_num),
                                'sims',
                                str(sim_num),
                                'sim.obj'
                            )

                            sim_dir = os.path.join(
                                os.getcwd(),
                                'samples',
                                str(self.configs[Config.RUN.value]['sample']),
                                'models',
                                str(model_num),
                                'sims'
                            )

                            # load up correct simulation and build required sims
                            simulation: Simulation = load_obj(sim_obj_path)
                            simulation.build_n_sims(sim_dir, sim_num)

                            # export simulations
                            Simulation.export_n_sims(
                                sample_num,
                                model_num,
                                sim_num,
                                sim_dir,
                                os.environ[Env.NSIM_EXPORT_PATH.value]
                            )

                            # ensure run configuration is present
                            Simulation.export_run(
                                self.number,
                                os.environ[Env.PROJECT_PATH.value],
                                os.environ[Env.NSIM_EXPORT_PATH.value]
                            )

                        print('Model {} data exported to appropriate folders in {}'.format(model_num, os.environ[
                            Env.NSIM_EXPORT_PATH.value]))

                    elif not models_exit_status[model_index]:
                        print('\nDid not create NEURON simulations for Sims associated with: \n'
                              '\t Model Index: {} \n'
                              'since COMSOL failed to create required potentials. \n'.format(model_num))

            elif 'models' in all_configs.keys() and 'sims' not in all_configs.keys():
                # Model Configs Provided, but not Sim Configs
                print('\nTO JAVA\n')
                self.handoff(self.number)
                print('\nNEURON Simulations NOT created since no Sim indices indicated in Config.SIM\n')

    def handoff(self, run_number: int):
        comsol_path = os.environ[Env.COMSOL_PATH.value]
        jdk_path = os.environ[Env.JDK_PATH.value]
        project_path = os.environ[Env.PROJECT_PATH.value]
        run_path = os.path.join(project_path, 'config', 'user', 'runs', '{}.json'.format(run_number))

        core_name = 'ModelWrapper'

        #Encode command line args as jason string, then encode to base64 for passing to java
        argstring = json.dumps(self.configs[Config.CLI_ARGS.value])
        argbytes = argstring.encode('ascii')
        argbase = base64.b64encode(argbytes)
        argfinal = argbase.decode('ascii')
        
        if sys.platform.startswith('darwin'):  # macOS

            subprocess.Popen(['{}/bin/comsol'.format(comsol_path), 'server'], close_fds=True)
            os.chdir('src')
            os.system(
                '{}/javac -classpath ../bin/json-20190722.jar:{}/plugins/* model/*.java -d ../bin'.format(jdk_path,
                                                                                                          comsol_path))
            # https://stackoverflow.com/questions/219585/including-all-the-jars-in-a-directory-within-the-java-classpath
            os.system('{}/java/maci64/jre/Contents/Home/bin/java '
                      '-cp .:$(echo {}/plugins/*.jar | '
                      'tr \' \' \':\'):../bin/json-20190722.jar:../bin model.{} "{}" "{}" "{}"'.format(comsol_path,
                                                                                                  comsol_path,
                                                                                                  core_name,
                                                                                                  project_path,
                                                                                                  run_path,
                                                                                                  argfinal))
            os.chdir('..')

        elif sys.platform.startswith('linux'):  # linux

            subprocess.Popen(['{}/bin/comsol'.format(comsol_path), 'server'], close_fds=True)
            os.chdir('src')
            os.system(
                '{}/javac -classpath ../bin/json-20190722.jar:{}/plugins/* model/*.java -d ../bin'.format(jdk_path,
                                                                                                          comsol_path))
            # https://stackoverflow.com/questions/219585/including-all-the-jars-in-a-directory-within-the-java-classpath
            os.system('{}/java/glnxa64/jre/bin/java '
                      '-cp .:$(echo {}/plugins/*.jar | '
                      'tr \' \' \':\'):../bin/json-20190722.jar:../bin model.{} "{}" "{}" "{}"'.format(comsol_path,
                                                                                                  comsol_path,
                                                                                                  core_name,
                                                                                                  project_path,
                                                                                                  run_path,
                                                                                                  argfinal))
            os.chdir('..')

        else:  # assume to be 'win64'
            subprocess.Popen(['{}\\bin\\win64\\comsolmphserver.exe'.format(comsol_path)], close_fds=True)
            os.chdir('src')
            os.system('""{}\\javac" '
                      '-cp "..\\bin\\json-20190722.jar";"{}\\plugins\\*" '
                      'model\\*.java -d ..\\bin"'.format(jdk_path,
                                                         comsol_path))
            os.system('""{}\\java\\win64\\jre\\bin\\java" '
                      '-cp "{}\\plugins\\*";"..\\bin\\json-20190722.jar";"..\\bin" '
                      'model.{} "{}" "{}" "{}""'.format(comsol_path,
                                                   comsol_path,
                                                   core_name,
                                                   project_path,
                                                   run_path,
                                                   argfinal))
            os.chdir('..')

    def compute_cuff_shift(self, model_config: dict, sample: Sample, sample_config: dict):
        # NOTE: ASSUMES SINGLE SLIDE

        # add temporary model configuration
        self.add(SetupMode.OLD, Config.MODEL, model_config)
        self.add(SetupMode.OLD, Config.SAMPLE, sample_config)

        # fetch slide
        slide = sample.slides[0]

        # fetch nerve mode
        nerve_mode: NerveMode = self.search_mode(NerveMode, Config.SAMPLE)

        if nerve_mode == NerveMode.PRESENT:
            if 'deform_ratio' not in self.configs[Config.SAMPLE.value].keys():
                deform_ratio = 1
            else:
                deform_ratio = self.search(Config.SAMPLE, 'deform_ratio')
            if deform_ratio > 1:
                self.throw(109)
        else:
            deform_ratio = None

        # fetch cuff config
        cuff_config: dict = self.load(
            os.path.join(os.getcwd(), "config", "system", "cuffs", model_config['cuff']['preset'])
        )

        # fetch 1-2 letter code for cuff (ex: 'CT')
        cuff_code: str = cuff_config['code']

        # fetch radius buffer string (ex: '0.003 [in]')
        cuff_r_buffer_str: str = [item["expression"] for item in cuff_config["params"]
                                  if item["name"] == '_'.join(['thk_medium_gap_internal', cuff_code])][0]

        # calculate value of radius buffer in micrometers (ex: 76.2)
        cuff_r_buffer: float = Quantity(
            Quantity(
                cuff_r_buffer_str.translate(cuff_r_buffer_str.maketrans('', '', ' []')),
                scale='m'
            ),
            scale='um'
        ).real  # [um] (scaled from any arbitrary length unit)

        # get center and radius of nerve's min_bound circle
        nerve_copy = deepcopy(slide.nerve if nerve_mode == NerveMode.PRESENT else slide.fascicles[0].outer)

        # Get the boundary and center information for computing cuff shift
        if self.search_mode(ReshapeNerveMode, Config.SAMPLE) and not slide.monofasc() and deform_ratio == 1:
            x, y = 0, 0
            r_bound = np.sqrt(sample_config['Morphology']['Nerve']['area'] / np.pi)
        else:
            x, y, r_bound = nerve_copy.make_circle()

        # next calculate the angle of the "centroid" to the center of min bound circle
        # if mono fasc, just use 0, 0 as centroid (i.e., centroid of nerve same as centroid of all fasc)
        # if poly fasc, use centroid of all fascicle as reference, not 0, 0
        # angle of centroid of nerve to center of minimum bounding circle
        reference_x = reference_y = 0.0
        if not slide.monofasc() and not (round(slide.nerve.centroid()[0])==round(slide.nerve.centroid()[1])==0):
            self.throw(123) #if the slide has nerve and is not centered at the nerve throw error
        if not slide.monofasc():
            reference_x, reference_y = slide.fascicle_centroid()
        theta_c = (np.arctan2(reference_y - y, reference_x - x) * (360 / (2 * np.pi))) % 360

        # calculate final necessary radius by adding buffer
        r_f = r_bound + cuff_r_buffer

        # fetch initial cuff rotation (convert to rads)
        theta_i = cuff_config.get('angle_to_contacts_deg') % 360

        # fetch boolean for cuff expandability
        expandable: bool = cuff_config['expandable']

        # check radius iff not expandable
        if not expandable:
            r_i_str: str = [item["expression"] for item in cuff_config["params"]
                            if item["name"] == '_'.join(['R_in', cuff_code])][0]
            r_i: float = Quantity(
                Quantity(
                    r_i_str.translate(r_i_str.maketrans('', '', ' []')),
                    scale='m'
                ),
                scale='um'
            ).real  # [um] (scaled from any arbitrary length unit)

            if not r_f <= r_i:
                self.throw(51)

            theta_f = theta_i
        else:
            # get initial cuff radius
            r_i_str: str = [item["expression"] for item in cuff_config["params"]
                            if item["name"] == '_'.join(['r_cuff_in_pre', cuff_code])][0]
            r_i: float = Quantity(
                Quantity(
                    r_i_str.translate(r_i_str.maketrans('', '', ' []')),
                    scale='m'
                ),
                scale='um'
            ).real  # [um] (scaled from any arbitrary length unit)

            if r_i < r_f:
                fixed_point = cuff_config.get('fixed_point')
                if fixed_point is None:
                    self.throw(126)
                if fixed_point == 'clockwise_end':
                    theta_f = theta_i*(r_i/r_f)
                elif fixed_point == 'center':
                    theta_f = theta_i
            else:
                theta_f = theta_i

        offset = 0
        for key, coef in cuff_config["offset"].items():
            value_str = [item["expression"] for item in cuff_config["params"] if item['name'] == key][0]
            value: float = Quantity(
                Quantity(
                    value_str.translate(value_str.maketrans('', '', ' []')),
                    scale='m'
                ),
                scale='um'
            ).real  # [um] (scaled from any arbitrary length unit)
            offset += coef * value

        # remove sample config
        self.remove(Config.SAMPLE)

        cuff_shift_mode: CuffShiftMode = self.search_mode(CuffShiftMode, Config.MODEL)

        # remove (pop) temporary model configuration
        model_config = self.remove(Config.MODEL)
        model_config['min_radius_enclosing_circle'] = r_bound

        if slide.orientation_angle is not None:
            theta_c = (slide.orientation_angle) * (360 / (2 * np.pi)) % 360  # overwrite theta_c, use our own orientation

        if cuff_shift_mode == CuffShiftMode.AUTO_ROTATION_MIN_CIRCLE_BOUNDARY \
                or cuff_shift_mode == CuffShiftMode.MIN_CIRCLE_BOUNDARY:  # for backwards compatibility
            if r_i > r_f:
                model_config['cuff']['rotate']['pos_ang'] = theta_c-theta_f
                model_config['cuff']['shift']['x'] = x - (r_i - offset - cuff_r_buffer - r_bound) * np.cos(
                    theta_c * ((2 * np.pi) / 360))
                model_config['cuff']['shift']['y'] = y - (r_i - offset - cuff_r_buffer - r_bound) * np.sin(
                    theta_c * ((2 * np.pi) / 360))

            else:
                model_config['cuff']['rotate']['pos_ang'] = theta_c-theta_f

                # if nerve is present, use 0,0
                if slide.nerve is not None and deform_ratio==1:  # has nerve
                    model_config['cuff']['shift']['x'] = 0
                    model_config['cuff']['shift']['y'] = 0
                else:
                    # else, use
                    model_config['cuff']['shift']['x'] = x
                    model_config['cuff']['shift']['y'] = y

        elif cuff_shift_mode == CuffShiftMode.AUTO_ROTATION_TRACE_BOUNDARY \
                or cuff_shift_mode == CuffShiftMode.TRACE_BOUNDARY:  # for backwards compatibility
            if r_i < r_f:
                model_config['cuff']['rotate']['pos_ang'] = theta_c-theta_f
                model_config['cuff']['shift']['x'] = x
                model_config['cuff']['shift']['y'] = y
            else:
                id_boundary = Point(0, 0).buffer(r_i - offset)
                n_boundary = Point(x, y).buffer(r_f)

                if id_boundary.boundary.distance(n_boundary.boundary) < cuff_r_buffer:
                    nerve_copy.shift([x, y, 0])
                    print("WARNING: NERVE CENTERED ABOUT MIN CIRCLE CENTER (BEFORE PLACEMENT) BECAUSE "
                          "CENTROID PLACEMENT VIOLATED REQUIRED CUFF BUFFER DISTANCE\n")

                center_x = 0
                center_y = 0
                step = 1  # [um] STEP SIZE
                x_step = step * np.cos(-theta_c + np.pi)  # STEP VECTOR X-COMPONENT
                y_step = step * np.sin(-theta_c + np.pi)  # STEP VECTOR X-COMPONENT

                # shift nerve within cuff until one step within the minimum separation from cuff
                while nerve_copy.polygon().boundary.distance(id_boundary.boundary) >= cuff_r_buffer:
                    nerve_copy.shift([x_step, y_step, 0])
                    center_x -= x_step
                    center_y -= y_step

                # to maintain minimum separation from cuff, reverse last step
                center_x += x_step
                center_y += y_step

                model_config['cuff']['rotate']['pos_ang'] = (theta_c-theta_f)
                model_config['cuff']['shift']['x'] = center_x
                model_config['cuff']['shift']['y'] = center_y

        elif cuff_shift_mode == CuffShiftMode.NAIVE_ROTATION_TRACE_BOUNDARY:
            if slide.orientation_point is not None:
                print('Warning: orientation tif image will be ignored because a NAIVE cuff shift mode was chosen.')
            if r_i < r_f:
                model_config['cuff']['rotate']['pos_ang'] = 0
                model_config['cuff']['shift']['x'] = x
                model_config['cuff']['shift']['y'] = y
            else:
                id_boundary = Point(0, 0).buffer(r_i - offset)
                n_boundary = Point(x, y).buffer(r_f)

                if id_boundary.boundary.distance(n_boundary.boundary) < cuff_r_buffer:
                    nerve_copy.shift([x, y, 0])
                    print("WARNING: NERVE CENTERED ABOUT MIN CIRCLE CENTER (BEFORE PLACEMENT) BECAUSE "
                          "CENTROID PLACEMENT VIOLATED REQUIRED CUFF BUFFER DISTANCE\n")

                center_x = 0
                center_y = 0
                step = 1  # [um] STEP SIZE
                x_step = step * np.cos(-theta_c + np.pi)  # STEP VECTOR X-COMPONENT
                y_step = step * np.sin(-theta_c + np.pi)  # STEP VECTOR X-COMPONENT

                # shift nerve within cuff until one step within the minimum separation from cuff
                while nerve_copy.polygon().boundary.distance(id_boundary.boundary) >= cuff_r_buffer:
                    nerve_copy.shift([x_step, y_step, 0])
                    center_x -= x_step
                    center_y -= y_step

                # to maintain minimum separation from cuff, reverse last step
                center_x += x_step
                center_y += y_step

                model_config['cuff']['rotate']['pos_ang'] = 0
                model_config['cuff']['shift']['x'] = center_x
                model_config['cuff']['shift']['y'] = center_y

        elif cuff_shift_mode == CuffShiftMode.NONE:
            model_config['cuff']['rotate']['pos_ang'] = 0
            model_config['cuff']['shift']['x'] = 0
            model_config['cuff']['shift']['y'] = 0

        elif cuff_shift_mode == CuffShiftMode.NAIVE_ROTATION_MIN_CIRCLE_BOUNDARY \
                or cuff_shift_mode == CuffShiftMode.PURPLE:
            if slide.orientation_point is not None:
                print('Warning: orientation tif image will be ignored because a NAIVE cuff shift mode was chosen.')
            if r_i > r_f:
                model_config['cuff']['rotate']['pos_ang'] = 0

                model_config['cuff']['shift']['x'] = x - (r_i - offset - cuff_r_buffer - r_bound) * np.cos(
                    theta_i * ((2 * np.pi) / 360))
                model_config['cuff']['shift']['y'] = y - (r_i - offset - cuff_r_buffer - r_bound) * np.sin(
                    theta_i * ((2 * np.pi) / 360))

            else:
                model_config['cuff']['rotate']['pos_ang'] = 0

                # if nerve is present, use 0,0
                if slide.nerve is not None and deform_ratio==1:  # has nerve
                    model_config['cuff']['shift']['x'] = 0
                    model_config['cuff']['shift']['y'] = 0
                else:
                    # else, use
                    model_config['cuff']['shift']['x'] = x
                    model_config['cuff']['shift']['y'] = y
                    
        return model_config

    def compute_electrical_parameters(self, all_configs, model_index):

        # fetch current model config using the index
        model_config = all_configs[Config.MODEL.value][model_index]
        model_num = self.configs[Config.RUN.value]['models'][model_index]

        # initialize Waveform object
        waveform = Waveform(self.configs[Config.EXCEPTIONS.value])

        # add model config to Waveform object, enabling it to generate waveforms
        waveform.add(SetupMode.OLD, Config.MODEL, model_config)

        # compute rho and sigma from waveform instance
        if model_config.get('modes').get(PerineuriumResistivityMode.config.value) == \
                PerineuriumResistivityMode.RHO_WEERASURIYA.value:
            freq_double = model_config.get('frequency')
            rho_double = waveform.rho_weerasuriya(freq_double)
            sigma_double = 1 / rho_double
            tmp = {'value': str(sigma_double), 'label': 'RHO_WEERASURIYA @ %d Hz' % freq_double, 'unit': '[S/m]'}
            model_config['conductivities']['perineurium'] = tmp

        elif model_config.get('modes').get(PerineuriumResistivityMode.config.value) == \
                PerineuriumResistivityMode.MANUAL.value:
            pass
        else:
            self.throw(48)

        dest_path: str = os.path.join(*all_configs[Config.SAMPLE.value][0]['samples_path'],
                                      str(self.configs[Config.RUN.value]['sample']),
                                      'models',
                                      str(model_num),
                                      'model.json')

        TemplateOutput.write(model_config, dest_path)

    def populate_env_vars(self):
        if Config.ENV.value not in self.configs.keys():
            self.throw(75)

        for key in Env.vals.value:
            value = self.search(Config.ENV, key)
            assert type(value) is str
            os.environ[key] = value

    def model_parameter_checking(self, all_configs):
        for _, model_config in enumerate(all_configs[Config.MODEL.value]):
            distal_exists = model_config['medium']['distal']['exist']
            if distal_exists and model_config['medium']['proximal']['distant_ground'] == True:
                self.throw(107)
