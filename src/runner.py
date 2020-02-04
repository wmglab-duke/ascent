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

import sys

# packages
import subprocess

# access
from copy import deepcopy

import numpy as np
from descartes import PolygonPatch

from src.core import Sample, Simulation, Waveform
from src.utils import *
from shapely.geometry import Point, MultiLineString, Polygon
from matplotlib import pyplot as plt


class Runner(Exceptionable, Configurable):

    def __init__(self):

        # initialize Configurable super class
        Configurable.__init__(self)

        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW)

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
        stupid = False

        # NOTE: single sample per Runner, so no looping of samples
        #       possible addition of functionality for looping samples in start.py

        # load all json configs into memory
        all_configs = self.load_configs()

        def load(path: str):
            return pickle.load(open(path, 'rb'))

        sample_file = os.path.join(
            'samples',
            str(self.configs[Config.RUN.value]['sample']),
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
            print('    MODEL {}'.format(self.configs[Config.RUN.value]['models'][model_index]))

            # use current model index to computer maximum cuff shift (radius) .. SAVES to file in method
            self.compute_cuff_shift(all_configs, model_index, sample)

            # use current model index to compute electrical parameters ... SAVES to file in method
            self.compute_electrical_parameters(all_configs, model_index)

            # iterate through simulations
            for sim_index, sim_config in enumerate(all_configs['sims']):
                print('        SIM {}'.format(self.configs[Config.RUN.value]['sims'][sim_index]))
                sim_obj_dir = os.path.join(
                    'samples',
                    str(self.configs[Config.RUN.value]['sample']),
                    'models',
                    str(model_index),
                    'sims',
                    str(self.configs[Config.RUN.value]['sims'][sim_index])
                )

                sim_obj_file = os.path.join(
                    sim_obj_dir,
                    'sim.obj'
                )

                # init fiber manager
                # fiber_manager = None
                if smart and (not stupid) and os.path.exists(sim_obj_file):
                    print('Found existing sim object for sim: {}'.format(sim_index))
                    pass
                    # fiber_manager = load(fiber_manager_file)
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

        # handoff (to Java) -  Build/Mesh/Solve/Save bases; Extract/Save potentials
        print('\nTO JAVA\n')
        self.handoff()
        print('\nTO PYTHON\n')

        #  continue by using simulation objects
        for model_index, model_config in enumerate(all_configs[Config.MODEL.value]):
            for sim_index, sim_conifig in enumerate(all_configs['sims']):
                sim_obj_path = os.path.join(
                    'samples',
                    str(self.configs[Config.RUN.value]['sample']),
                    'models',
                    str(model_index),
                    'sims',
                    str(self.configs[Config.RUN.value]['sims'][sim_index]),
                    'sim.obj'
                )

                sim_dir = os.path.join(
                    'samples',
                    str(self.configs[Config.RUN.value]['sample']),
                    'models',
                    str(model_index),
                    'sims',
                    str(self.configs[Config.RUN.value]['sims'][sim_index])
                )

                load(sim_obj_path).build_sims(sim_dir)

    def handoff(self):
        comsol_path = self.search(Config.ENV, 'comsol_path')
        jdk_path = self.search(Config.ENV, 'jdk_path')
        project_path = self.search(Config.ENV, 'project_path')
        run_path = os.path.join(project_path, 'config', 'user', 'runs', '{}.json'.format(sys.argv[1]))

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

    def compute_cuff_shift(self, all_configs, model_index, sample):

        # fetch current model config using the index
        model_config = all_configs[Config.MODEL.value][model_index]

        # fetch cuff config
        cuff = self.load(os.path.join("config", "system", "cuffs", model_config['cuff']['preset']))

        # Data conventions: A point is a pair of floats (x, y).
        # A circle is a triple of floats (center x, center y, radius).

        # Returns the smallest circle that encloses all the given points. Runs in expected O(n) time, randomized.
        # Input: A sequence of pairs of floats or ints, e.g. [(0,5), (3.1,-2.7)].
        # Output: A triple of floats representing a circle.
        # Note: If 0 points are given, None is returned. If 1 point is given, a circle of radius 0 is returned.
        #
        # Initially: No boundary points known
        def make_circle(points):
            # Convert to float and randomize order
            shuffled = [(float(x), float(y)) for (x, y) in points]
            random.shuffle(shuffled)

            # Progressively add points to circle or recompute circle
            c = None
            for (i, p) in enumerate(shuffled):
                if c is None or not is_in_circle(c, p):
                    c = _make_circle_one_point(shuffled[: i + 1], p)
            return c

        # One boundary point known
        def _make_circle_one_point(points, p):
            c = (p[0], p[1], 0.0)
            for (i, q) in enumerate(points):
                if not is_in_circle(c, q):
                    if c[2] == 0.0:
                        c = make_diameter(p, q)
                    else:
                        c = _make_circle_two_points(points[: i + 1], p, q)
            return c

        # Two boundary points known
        def _make_circle_two_points(points, p, q):
            circ = make_diameter(p, q)
            left = None
            right = None
            px, py = p
            qx, qy = q

            # For each point not in the two-point circle
            for r in points:
                if is_in_circle(circ, r):
                    continue

                # Form a circumcircle and classify it on left or right side
                cross = _cross_product(px, py, qx, qy, r[0], r[1])
                c = make_circumcircle(p, q, r)
                if c is None:
                    continue
                elif cross > 0.0 and (
                        left is None or _cross_product(px, py, qx, qy, c[0], c[1]) > _cross_product(px, py, qx, qy,
                                                                                                    left[0], left[1])):
                    left = c
                elif cross < 0.0 and (
                        right is None or _cross_product(px, py, qx, qy, c[0], c[1]) < _cross_product(px, py, qx, qy,
                                                                                                     right[0],
                                                                                                     right[1])):
                    right = c

            # Select which circle to return
            if left is None and right is None:
                return circ
            elif left is None:
                return right
            elif right is None:
                return left
            else:
                return left if (left[2] <= right[2]) else right

        def make_diameter(a, b):
            cx = (a[0] + b[0]) / 2.0
            cy = (a[1] + b[1]) / 2.0
            r0 = np.math.hypot(cx - a[0], cy - a[1])
            r1 = np.math.hypot(cx - b[0], cy - b[1])
            return cx, cy, max(r0, r1)

        def make_circumcircle(a, b, c):
            # Mathematical algorithm from Wikipedia: Circumscribed circle
            ox = (min(a[0], b[0], c[0]) + max(a[0], b[0], c[0])) / 2.0
            oy = (min(a[1], b[1], c[1]) + max(a[1], b[1], c[1])) / 2.0
            ax = a[0] - ox
            ay = a[1] - oy
            bx = b[0] - ox
            by = b[1] - oy
            cx = c[0] - ox
            cy = c[1] - oy
            d = (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) * 2.0
            if d == 0.0:
                return None
            x = ox + ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (
                        ay - by)) / d
            y = oy + ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (
                        bx - ax)) / d
            ra = np.math.hypot(x - a[0], y - a[1])
            rb = np.math.hypot(x - b[0], y - b[1])
            rc = np.math.hypot(x - c[0], y - c[1])
            return x, y, max(ra, rb, rc)

        _MULTIPLICATIVE_EPSILON = 1 + 1e-14

        def is_in_circle(c, p):
            return c is not None and np.math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] * _MULTIPLICATIVE_EPSILON

        # Returns twice the signed area of the triangle defined by (x0, y0), (x1, y1), (x2, y2).
        def _cross_product(x0, y0, x1, y1, x2, y2):
            return (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)

        def smallest_enclosing_circle_naive(points):
            # Returns the smallest enclosing circle in O(n^4) time using the naive algorithm.
            # https://www.nayuki.io/res/smallest-enclosing-circle/smallestenclosingcircle-test.py

            # Degenerate cases
            if len(points) == 0:
                return None
            elif len(points) == 1:
                return points[0][0], points[0][1], 0

            # Try all unique pairs
            result = None
            for i in range(len(points)):
                p = points[i]
                for j in range(i + 1, len(points)):
                    q = points[j]
                    c = make_diameter(p, q)
                    if (result is None or c[2] < result[2]) and \
                            all(is_in_circle(c, r) for r in points):
                        result = c
            if result is not None:
                return result  # This optimization is not mathematically proven

            # Try all unique triples
            for i in range(len(points)):
                p = points[i]
                for j in range(i + 1, len(points)):
                    q = points[j]
                    for k in range(j + 1, len(points)):
                        r = points[k]
                        c = make_circumcircle(p, q, r)
                        if c is not None and (result is None or c[2] < result[2]) and \
                                all(is_in_circle(c, s) for s in points):
                            result = c

            if result is None:
                raise AssertionError()

            return result

        # if nervemode is present, use r_nerve from nerve -> r_nerve
        # else if nervemode is not present, find minimum bounding circle of the nerve and center it at (0,0) -> r_nerve

        # CorTec: r_nerve, thk_medium_gap_internal_CT, r_cuff_in_pre_CT
        # Enteromedics: r_nerve, thk_medium_gap_internal_EM, r_cuff_in_pre_EM
        # ImThera: r_nerve, thk_medium_gap_internal_IT, r_cuff_in_pre_ITI
        # LivaNova: r_nerve, thk_medium_gap_internal_LN, r_cuff_in_pre_LN
        # Madison: r_nerve, thk_medium_gap_internal_M, r_cuff_in_pre_M
        # MicroLeads: R_in_U (constant), L_U, Tangent_U
        # Pitt: R_in_Pitt (constant)
        # Purdue: r_nerve, thk_medium_gap_internal_P, r_conductor_P,
        #   sep_conductor_P, r_cuff_in_pre_P (this is not like the others)

        r_in = 100  # get inner cuff boundary from cuff configuration
        angle_deg = 45  # parameter in cuff configuration file
        id_boundary = Point(0, 0).buffer(r_in)  # TODO use this for Enteromedics, Cortec. ImThera, LN, Madison, Pitt, Purdue

        r_microleads_in = 100
        l_microleads = 300
        w_microleads = 200

        p1 = Point(0, -w_microleads / 2)
        p2 = Point(l_microleads, -w_microleads / 2)
        p3 = Point(l_microleads, w_microleads / 2)
        p4 = Point(0, w_microleads / 2)
        point_list = [p1, p2, p3, p4, p1]
        poly = Polygon([[p.x, p.y] for p in point_list])

        mergedpoly = poly.union(id_boundary)  # TODO use this for MicroLeads

        if NerveMode.NOT_PRESENT:
            nerve_copy = deepcopy(sample.slides[0].fascicles[0].outer)
        elif NerveMode.PRESENT:
            nerve_copy = deepcopy(sample.slides[0].nerve)  # get nerve from slide

        nerve_copy.down_sample(DownSampleMode.KEEP, 20)
        circle = smallest_enclosing_circle_naive(nerve_copy.points)

        outer_circle = Point(circle[0], circle[1]).buffer(circle[2])

        sep = 10  # parameter in model config file
        step = 1  # hard coded step size [um]

        angle = angle_deg * np.pi / 180
        x_shift = 0  # initialize cuff shift values
        y_shift = 0
        x_step = step * np.cos(angle)
        y_step = step * np.sin(angle)

        while nerve_copy.polygon().boundary.distance(mergedpoly.boundary) >= sep:
            nerve_copy.shift([x_step, y_step, 0])

            x_shift += x_step
            y_shift += y_step

            x_shift -= x_step
            y_shift -= y_step

        # x, y = mergedpoly.exterior.xy
        x2, y2 = outer_circle.boundary.xy
        # union with id_boundary
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # ax.plot(x, y)
        ax.plot(x2, y2, 'k-')
        ax.plot(nerve_copy.points[:,0], nerve_copy.points[:,1], 'k-')
        # ax.plot(nerve_copy.points)
        # nerve.plot()

        plt.show()
        print("here")

    def compute_electrical_parameters(self, all_configs, model_index):

        # fetch current model config using the index
        model_config = all_configs[Config.MODEL.value][model_index]

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
                                      str(self.configs[Config.RUN.value]['models'][model_index]),
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
