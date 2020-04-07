#!/usr/bin/env python3.7

"""
Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""
# builtins
import pickle
import random
from typing import List

import sys

# packages
import subprocess

# access
from copy import deepcopy

import numpy as np
from quantiphy import Quantity

from src.core import Trace
from src.core import Sample, Simulation, Waveform
from src.utils import *
from shapely.geometry import Point, Polygon
from matplotlib import pyplot as plt


class Runner(Exceptionable, Configurable):

    def __init__(self, number: int):

        # initialize Configurable super class
        Configurable.__init__(self)

        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW)

        self.number = number

    def load_configs(self) -> dict:

        def validate_and_add(config_source: dict, key: str, path: str):
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
        models = self.search(Config.RUN, 'models')
        sims = self.search(Config.RUN, 'sims')

        sample_path = os.path.join(
            'samples',
            str(sample),
            'sample.json'
        )
        validate_and_add(configs, 'sample', sample_path)

        model_paths = [os.path.join('samples',
                                    str(sample),
                                    'models',
                                    str(model),
                                    'model.json') for model in models]
        for model_path in model_paths:
            validate_and_add(configs, 'models', model_path)

        sim_paths = [os.path.join('config',
                                  'user',
                                  'sims',
                                  '{}.json'.format(sim)) for sim in sims]
        for sim_path in sim_paths:
            validate_and_add(configs, 'sims', sim_path)

        return configs

    def run(self, smart: bool = True):
        """

        :param smart:
        :return:
        """
        # NOTE: single sample per Runner, so no looping of samples
        #       possible addition of functionality for looping samples in start.py

        # load all json configs into memory
        all_configs = self.load_configs()

        def load(path: str):
            return pickle.load(open(path, 'rb'))

        potentials_exist: List[bool] = []  # if all of these are true, skip Java

        sample_num = self.configs[Config.RUN.value]['sample']

        sample_file = os.path.join(
            'samples',
            str(sample_num),
            'sample.obj'
        )

        print('SAMPLE {}'.format(self.configs[Config.RUN.value]['sample']))

        # instantiate sample
        if smart and os.path.exists(sample_file):
            print('Found existing sample: {}'.format(self.configs[Config.RUN.value]['sample']))
            sample = load(sample_file)
        else:
            # init slide manager
            sample = Sample(self.configs[Config.EXCEPTIONS.value])
            # run processes with slide manager (see class for details)
            sample \
                .add(SetupMode.OLD, Config.SAMPLE, all_configs[Config.SAMPLE.value][0]) \
                .add(SetupMode.OLD, Config.RUN, self.configs[Config.RUN.value]) \
                .init_map(SetupMode.OLD) \
                .build_file_structure() \
                .populate() \
                .write(WriteMode.SECTIONWISE2D) \
                .output_morphology_data() \
                .save(os.path.join(sample_file))

        # iterate through models
        for model_index, model_config in enumerate(all_configs[Config.MODEL.value]):
            model_num = self.configs[Config.RUN.value]['models'][model_index]
            print('    MODEL {}'.format(model_num))

            # use current model index to computer maximum cuff shift (radius) .. SAVES to file in method
            model_config = self.compute_cuff_shift(model_config, sample, all_configs[Config.SAMPLE.value][0])

            model_config_file_name = os.path.join(
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
            for sim_index, sim_config in enumerate(all_configs['sims']):
                sim_num = self.configs[Config.RUN.value]['sims'][sim_index]
                print('        SIM {}'.format(self.configs[Config.RUN.value]['sims'][sim_index]))
                sim_obj_dir = os.path.join(
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
                    print('Found existing sim object for sim: {}'.format(sim_index))

                    simulation: Simulation = load(sim_obj_file)
                    potentials_exist.append(simulation.potentials_exist(sim_obj_dir))

                else:
                    if not os.path.exists(sim_obj_dir):
                        os.makedirs(sim_obj_dir)

                    simulation: Simulation = Simulation(sample, self.configs[Config.EXCEPTIONS.value])
                    simulation \
                        .add(SetupMode.OLD, Config.MODEL, model_config) \
                        .add(SetupMode.OLD, Config.SIM, sim_config) \
                        .resolve_factors() \
                        .write_waveforms(sim_obj_dir) \
                        .write_fibers(sim_obj_dir) \
                        .validate_srcs(sim_obj_dir) \
                        .save(sim_obj_file)

                    potentials_exist.append(simulation.potentials_exist(sim_obj_dir))

        # handoff (to Java) -  Build/Mesh/Solve/Save bases; Extract/Save potentials
        if not all(potentials_exist):  # only transition to java if necessary (there are potentials that do not exist)
            print('\nTO JAVA\n')
            self.handoff(self.number)
            print('\nTO PYTHON\n')
        else:
            print('\nSKIPPING JAVA - all required extracted potentials already exist\n')

        #  continue by using simulation objects
        for model_index, model_config in enumerate(all_configs[Config.MODEL.value]):
            model_num = self.configs[Config.RUN.value]['models'][model_index]
            for sim_index, sim_config in enumerate(all_configs['sims']):
                sim_num = self.configs[Config.RUN.value]['sims'][sim_index]
                sim_obj_path = os.path.join(
                    'samples',
                    str(self.configs[Config.RUN.value]['sample']),
                    'models',
                    str(model_num),
                    'sims',
                    str(sim_num),
                    'sim.obj'
                )

                sim_dir = os.path.join(
                    'samples',
                    str(self.configs[Config.RUN.value]['sample']),
                    'models',
                    str(model_num),
                    'sims',
                    str(sim_num)
                )

                # load up correct simulation and build required sims
                simulation: Simulation = load(sim_obj_path)
                simulation.build_n_sims(sim_dir)

                # export simulations
                Simulation.export_n_sims(
                    sample_num,
                    model_num,
                    sim_num,
                    sim_dir,
                    self.search(Config.ENV, 'nsim_export')
                )

                # ensure run configuration is present
                Simulation.export_run(
                    self.number,
                    self.search(Config.ENV, 'project_path'),
                    self.search(Config.ENV, 'nsim_export')
                )

    def handoff(self, run_number: int):
        comsol_path = self.search(Config.ENV, 'comsol_path')
        jdk_path = self.search(Config.ENV, 'jdk_path')
        project_path = self.search(Config.ENV, 'project_path')
        run_path = os.path.join(project_path, 'config', 'user', 'runs', '{}.json'.format(run_number))

        core_name = 'ModelWrapper'

        if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):  # macOS and linux

            subprocess.Popen(['{}/bin/comsol'.format(comsol_path), 'server'], close_fds=True)
            os.chdir('src')
            os.system(
                '{}/javac -classpath ../lib/json-20190722.jar:{}/plugins/* model/*.java -d ../bin'.format(jdk_path,
                                                                                                          comsol_path))
            # https://stackoverflow.com/questions/219585/including-all-the-jars-in-a-directory-within-the-java-classpath
            os.system('{}/java/maci64/jre/Contents/Home/bin/java '
                      '-cp .:$(echo {}/plugins/*.jar | '
                      'tr \' \' \':\'):../lib/json-20190722.jar:../bin model.{} {} {}'.format(comsol_path,
                                                                                              comsol_path,
                                                                                              core_name,
                                                                                              project_path,
                                                                                              run_path))
            os.chdir('..')

        else:  # assume to be 'win64'
            subprocess.Popen(['{}\\bin\\win64\\comsolmphserver.exe'.format(comsol_path)], close_fds=True)
            os.chdir('src')
            # TODO:
            os.system('""{}\\javac" '
                      '-cp "..\\lib\\json-20190722.jar";"{}\\plugins\\*" '
                      'model\\*.java -d ..\\bin"'.format(jdk_path,
                                                         comsol_path))
            os.system('""{}\\java\\win64\\jre\\bin\\java" '
                      '-cp "{}\\plugins\\*";"..\\lib\\json-20190722.jar";"..\\bin" '
                      'model.{} {} {}"'.format(comsol_path,
                                               comsol_path,
                                               core_name,
                                               project_path,
                                               run_path))
            os.chdir('..')

    def compute_cuff_shift(self, model_config: dict, sample: Sample, sample_config: dict):

        # add temporary model configuration
        self.add(SetupMode.OLD, Config.MODEL, model_config)
        self.add(SetupMode.OLD, Config.SAMPLE, sample_config)

        # fetch nerve mode
        nerve_present: NerveMode = self.search_mode(NerveMode, Config.SAMPLE)

        # fetch cuff config
        cuff_config: dict = self.load(os.path.join("config", "system", "cuffs", model_config['cuff']['preset']))

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
        nerve_copy = deepcopy(
            sample.slides[0].nerve
            if nerve_present == NerveMode.PRESENT
            else sample.slides[0].fascicles[0].outer
        )

        # for speed, downsample nerves to n_points_nerve (100) points
        n_points_nerve = 100
        nerve_copy.down_sample(DownSampleMode.KEEP, int(np.floor(nerve_copy.points.size / n_points_nerve)))
        x, y, r_bound = nerve_copy.smallest_enclosing_circle_naive()

        theta_c = np.arctan2(y, x)

        # calculate final necessary radius by adding buffer
        r_f = r_bound + cuff_r_buffer

        # fetch initial cuff rotation (convert to rads)
        theta_i = cuff_config.get('angle_to_contacts_deg') * 2 * np.pi / 360

        # fetch cuff rotation mode
        cuff_rotation_mode: CuffRotationMode = self.search_mode(CuffRotationMode, Config.MODEL)

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

            theta_f = 0
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

            if cuff_rotation_mode == CuffRotationMode.MANUAL:
                theta_f = theta_i
            else:  # cuff_rotation_mode == CuffRotationMode.AUTOMATIC
                if r_i < r_f:
                    theta_f = (r_f / r_i - 1) * theta_i
                else:
                    theta_f = 0

        #
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

        if cuff_shift_mode == CuffShiftMode.MIN_CIRCLE_BOUNDARY:
            if r_i < r_f:
                model_config['cuff']['rotate']['pos_ang'] = (theta_f - theta_i + theta_c + np.pi) * 360 / (2 * np.pi)
                model_config['cuff']['shift']['x'] = 0  # - cuff_r_buffer * np.cos(theta_c)
                model_config['cuff']['shift']['y'] = 0  # - cuff_r_buffer * np.sin(theta_c)
            else:
                model_config['cuff']['rotate']['pos_ang'] = (theta_f - theta_i + theta_c + np.pi) * 360 / (2 * np.pi)
                model_config['cuff']['shift']['x'] = x + (r_i - offset - r_f - cuff_r_buffer) * np.cos(theta_c)
                model_config['cuff']['shift']['y'] = y + (r_i - offset - r_f - cuff_r_buffer) * np.sin(theta_c)

        elif cuff_shift_mode == CuffShiftMode.TRACE_BOUNDARY:
            if r_i < r_f:
                model_config['cuff']['rotate']['pos_ang'] = theta_f * 360 / (2 * np.pi)
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
                x_step = step * np.cos(theta_f + theta_i)  # STEP VECTOR X-COMPONENT
                y_step = step * np.sin(theta_f + theta_i)  # STEP VECTOR X-COMPONENT

                # shift nerve within cuff until one step within the minimum separation from cuff
                while nerve_copy.polygon().boundary.distance(id_boundary.boundary) >= cuff_r_buffer:
                    nerve_copy.shift([x_step, y_step, 0])
                    center_x -= x_step
                    center_y -= y_step

                # to maintain minimum separation from cuff, reverse last step
                center_x += x_step
                center_y += y_step

                model_config['cuff']['rotate']['pos_ang'] = theta_f * 360 / (2 * np.pi)
                model_config['cuff']['shift']['x'] = center_x
                model_config['cuff']['shift']['y'] = center_y

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
            freq_double = model_config.get('frequency').get('value')
            freq_unit = model_config.get('frequency').get('unit')
            rho_double = waveform.rho_weerasuriya(freq_double)
            sigma_double = 1 / rho_double
            model_config['conductivities']['perineurium']['value'] = str(sigma_double)
            model_config['conductivities']['perineurium']['label'] = "RHO_WEERASURIYA @ %d %s" % (freq_double,
                                                                                                  freq_unit)
        else:
            self.throw(48)

        dest_path: str = os.path.join(*all_configs[Config.SAMPLE.value][0]['samples_path'],
                                      str(self.configs[Config.RUN.value]['sample']),
                                      'models',
                                      str(model_num),
                                      'model.json')

        TemplateOutput.write(model_config, dest_path)

    # def smart_run(self):
    #
    #     print('\nStarting smart run.')
    #
    #     def load(path: str):
    #         return pickle.load(open(path, 'rb'))
    #
    #     path_parts = [self.path(Config.MASTER, 'samples_path'), self.search(Config.MASTER, 'sample')]
    #
    #     if not os.path.isfile(os.path.join(*path_parts, 'sample.obj')):
    #         print('Existing slide manager not found. Performing full run.')
    #         self.full_run()
    #
    #     else:
    #         print('Loading existing slide manager.')
    #         self.sample = load(os.path.join(*path_parts, 'sample.obj'))
    #
    #         if os.path.isfile(os.path.join(*path_parts, 'fiber_manager.obj')):
    #             print('Loading existing fiber manager.')
    #             self.fiber_manager = load(os.path.join(*path_parts, 'fiber_manager.obj'))
    #
    #         else:
    #             print('Existing fiber manager not found. Performing fiber run.')
    #             self.fiber_run()
    #
    #     self.save_all()
    #
    #     if self.fiber_manager is not None:
    #         self.fiber_manager.save_full_coordinates('TEST_JSON_OUTPUT.json')
    #     else:
    #         raise Exception('my dude, something went horribly wrong here')
    #
    #     self.handoff()
    #
    # def full_run(self):
    #     self.slide_run()
    #     self.fiber_run()
    #
    # def slide_run(self):
    #     print('\nSTART SLIDE MANAGER')
    #     self.sample = Sample(self.configs[Config.MASTER.value],
    #                                       self.configs[Config.EXCEPTIONS.value],
    #                                       map_mode=SetupMode.NEW)
    #
    #     print('BUILD FILE STRUCTURE')
    #     self.sample.build_file_structure()
    #
    #     print('POPULATE')
    #     self.sample.populate()
    #
    #     print('WRITE')
    #     self.sample.write(WriteMode.SECTIONWISE2D)
    #
    # def fiber_run(self):
    #     print('\nSTART FIBER MANAGER')
    #     self.fiber_manager = FiberManager(self.sample,
    #                                       self.configs[Config.MASTER.value],
    #                                       self.configs[Config.EXCEPTIONS.value])
    #
    #     print('FIBER XY COORDINATES')
    #     self.fiber_manager.fiber_xy_coordinates(plot=True, save=True)
    #
    #     print('FIBER Z COORDINATES')
    #     self.fiber_manager.fiber_z_coordinates(self.fiber_manager.xy_coordinates, save=True)
    #
    # def save_all(self):
    #
    #     print('SAVE ALL')
    #     path_parts = [self.path(Config.MASTER, 'samples_path'), self.search(Config.MASTER, 'sample')]
    #     self.sample.save(os.path.join(*path_parts, 'sample.obj'))
    #     self.sample.output_morphology_data()
    #     self.fiber_manager.save(os.path.join(*path_parts, 'fiber_manager.obj'))

    # def run(self):
    #     self.map = Map(self.configs[Config.MASTER.value],
    #                         self.configs[Config.EXCEPTIONS.value],
    #                         mode=SetupMode.NEW)
    #
    #     # TEST: Trace functionality
    #     # self.trace = Trace([[0,  0, 0],
    #     #                     [2,  0, 0],
    #     #                     [4,  0, 0],
    #     #                     [4,  1, 0],
    #     #                     [4,  2, 0],
    #     #                     [2,  2, 0],
    #     #                     [0,  2, 0],
    #     #                     [0,  1, 0]], self.configs[Config.EXCEPTIONS.value])
    #     # print('output path: {}'.format(self.trace.write(Trace.WriteMode.SECTIONWISE,
    #     #                                                 '/Users/jakecariello/Box/SPARCpy/data/output/test_trace')))
    #
    #     # TEST: exceptions configuration path
    #     # print('exceptions_config_path:\t{}'.format(self.exceptions_config_path))
    #
    #     # TEST: retrieve data from config file
    #     # print(self.search(Config.MASTER, 'test_array', 0, 'test'))
    #
    #     # TEST: throw error
    #     # self.throw(2)
    #
    #     # self.slide = Slide([Fascicle(self.configs[Config.EXCEPTIONS.value],
    #     #                              [self.trace],
    #     #                              self.trace)],
    #     #                    self.trace,
    #     #                    self.configs[Config.MASTER.value],
    #     #                    self.configs[Config.EXCEPTIONS.value])
    #     pass
    #
    # def trace_test(self):
    #
    #     # build path and read image
    #     path = os.path.join('data', 'input', 'misc_traces', 'tracefile2.tif');
    #     img = cv2.imread(path, -1)
    #
    #     # get contours and build corresponding traces
    #     # these are intentionally instance attributes so they can be inspected in the Python Console
    #     self.cnts, self.hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     self.traces = [Trace(cnt[:, 0, :], self.configs[Config.EXCEPTIONS.value]) for cnt in self.cnts]
    #
    #     # plot formats
    #     formats = ['r', 'g', 'b']
    #
    #     # original points and centroids
    #     title = 'Figure 0: original traces with calculated centroids'
    #     print(title)
    #     plt.figure(0)
    #     plt.axes().set_aspect('equal', 'datalim')
    #     for i, trace in enumerate(self.traces):
    #         trace.plot(formats[i] + '-')
    #         trace.plot_centroid(formats[i] + '*')
    #     plt.legend([str(i) for i in range(len(self.traces)) for _ in (0, 1)]) # end of this line is to duplicate items
    #     plt.title(title)
    #     plt.show()
    #
    #     # ellipse/circle/original comparison (trace 0)
    #     title = 'Figure 1: fit comparisons (trace 0)'
    #     print(title)
    #     plt.figure(1)
    #     plt.axes().set_aspect('equal', 'datalim')
    #     self.traces[0].plot(formats[0])
    #     self.traces[0].to_circle().plot(formats[1])
    #     self.traces[0].to_ellipse().plot(formats[2])
    #     plt.legend(['original', 'circle', 'ellipse'])
    #     plt.title(title)
    #     plt.show()
    #
    #     # example stats
    #     pairs = [(0, 1), (1, 2), (2, 0)]
    #     print('\nEXAMPLE STATS')
    #     for pair in pairs:
    #         print('PAIR: ({}, {})'.format(*pair))
    #         print('\tcent dist:\t{}'.format(self.traces[pair[0]].centroid_distance(self.traces[pair[1]])))
    #         print('\tmin dist:\t{}'.format(self.traces[pair[0]].min_distance(self.traces[pair[1]])))
    #         print('\tmax dist:\t{}'.format(self.traces[pair[0]].max_distance(self.traces[pair[1]])))
    #         print('\twithin:\t\t{}'.format(self.traces[pair[0]].within(self.traces[pair[1]])))
    #
    #     title = 'Figure 2: Scaled trace'
    #     print(title)
    #     plt.figure(2)
    #     plt.axes().set_aspect('equal', 'datalim')
    #     self.traces[0].plot(formats[0])
    #     self.traces[0].scale(1.2)
    #     self.traces[0].plot(formats[1])
    #     plt.legend(['original', 'scaled'])
    #     plt.title(title)
    #     plt.show()
    #
    # def fascicle_test(self):
    #     # build path and read image
    #     path = os.path.join('data', 'input', 'misc_traces', 'tracefile5.tif')
    #
    #     self.fascicles = Fascicle.inner_to_list(path,
    #                                             self.configs[Config.EXCEPTIONS.value],
    #                                             plot=True,
    #                                             scale=1.06)
    #
    # def reposition_test(self):
    #     # build path and read image
    #     path = os.path.join('data', 'input', 'samples', 'Cadaver54-3', 'NerveMask.tif')
    #
    #     self.img = np.flipud(cv2.imread(path, -1))
    #
    #     # get contours and build corresponding traces
    #     # these are intentionally instance attributes so they can be inspected in the Python Console
    #     self.nerve_cnts, _ = cv2.findContours(self.img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     self.nerve = Nerve(Trace(self.nerve_cnts[0][:, 0, :], self.configs[Config.EXCEPTIONS.value]))
    #
    #     self.fascicles = Fascicle.separate_to_list(os.path.join('data', 'input', 'samples',
    #                                                             'Cadaver54-3', 'EndoneuriumMask.tif'),
    #                                                os.path.join('data', 'input', 'samples',
    #                                                             'Cadaver54-3','PerineuriumMask.tif'),
    #                                                self.configs[Config.EXCEPTIONS.value],
    #
    #
    #                                                plot=False)
    #     self.slide = Slide(self.fascicles, self.nerve,
    #                        self.configs[Config.MASTER.value],
    #                        self.configs[Config.EXCEPTIONS.value])
    #
    #     self.slide.reposition_fascicles(self.slide.reshaped_nerve(ReshapeNerveMode.CIRCLE))
    #
    # def reposition_test2(self):
    #     # build path and read image
    #     path = os.path.join('data', 'input', 'samples', 'Pig11-3', 'NerveMask.tif')
    #     self.img = np.flipud(cv2.imread(path, -1))
    #
    #     # get contours and build corresponding traces
    #     # these are intentionally instance attributes so they can be inspected in the Python Console
    #     self.nerve_cnts, _ = cv2.findContours(self.img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     self.nerve = Nerve(Trace(self.nerve_cnts[0][:, 0, :], self.configs[Config.EXCEPTIONS.value]))
    #
    #     self.fascicles = Fascicle.inner_to_list(os.path.join('data', 'input', 'samples',
    #                                                          'Pig11-3', 'FascMask.tif'),
    #                                             self.configs[Config.EXCEPTIONS.value],
    #                                             plot=False,
    #                                             scale=1.05)
    #     self.slide = Slide(self.fascicles, self.nerve,
    #                        self.configs[Config.EXCEPTIONS.value],
    #                        will_reposition=True)
    #
    #     # self.slide.reposition_fascicles(self.slide.reshaped_nerve(ReshapeNerveMode.ELLIPSE))
    #     self.slide.reposition_fascicles(self.slide.reshaped_nerve(ReshapeNerveMode.CIRCLE))
