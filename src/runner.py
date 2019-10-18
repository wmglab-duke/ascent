#!/usr/bin/env python3.7

"""
File:       runner.py
Author:     Jake Cariello
Created:    July 21, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""
# builtins
import os
import pickle
import sys
import time

# packages
import subprocess

# access
from src.core import *
from src.utils import *


class Runner(Exceptionable, Configurable):

    def __init__(self, config_file_path: str):

        # initialize Configurable super class
        Configurable.__init__(self, SetupMode.NEW, ConfigKey.MASTER, config_file_path)

        # get config path info from config and set to class vars
        self.exceptions_config_path = self.path(ConfigKey.MASTER, 'config', 'paths', 'exceptions')

        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW, self.exceptions_config_path)

        # init variables for later use
        self.slide_manager = None
        self.fiber_manager = None

    def smart_run(self):

        print('\nStarting smart run.')

        def load(path: str):
            return pickle.load(open(path, 'rb'))

        path_parts = [self.path(ConfigKey.MASTER, 'samples_path'), self.search(ConfigKey.MASTER, 'sample')]

        if not os.path.isfile(os.path.join(*path_parts, 'slide_manager.obj')):
            print('Existing slide manager not found. Performing full run.')
            self.full_run()

        else:
            print('Loading existing slide manager.')
            self.slide_manager = load(os.path.join(*path_parts, 'slide_manager.obj'))

            if os.path.isfile(os.path.join(*path_parts, 'fiber_manager.obj')):
                print('Loading existing fiber manager.')
                self.fiber_manager = load(os.path.join(*path_parts, 'fiber_manager.obj'))

            else:
                print('Existing fiber manager not found. Performing fiber run.')
                self.fiber_run()

        self.save_all()

        if self.fiber_manager is not None:
            self.fiber_manager.save_full_coordinates('TEST_JSON_OUTPUT.json')
        else:
            raise Exception('my dude, something went horribly wrong here')

        self.handoff()

    def full_run(self):
        self.slide_run()
        self.fiber_run()

    def slide_run(self):
        print('\nSTART SLIDE MANAGER')
        self.slide_manager = SlideManager(self.configs[ConfigKey.MASTER.value],
                                          self.configs[ConfigKey.EXCEPTIONS.value],
                                          map_mode=SetupMode.OLD)

        print('BUILD FILE STRUCTURE')
        self.slide_manager.build_file_structure()

        print('POPULATE')
        self.slide_manager.populate()

        print('WRITE')
        self.slide_manager.write(WriteMode.SECTIONWISE2D)

    def fiber_run(self):
        print('\nSTART FIBER MANAGER')
        self.fiber_manager = FiberManager(self.slide_manager,
                                          self.configs[ConfigKey.MASTER.value],
                                          self.configs[ConfigKey.EXCEPTIONS.value])

        print('FIBER XY COORDINATES')
        self.fiber_manager.fiber_xy_coordinates(plot=True, save=True)

        print('FIBER Z COORDINATES')
        self.fiber_manager.fiber_z_coordinates(self.fiber_manager.xy_coordinates, save=True)

    def handoff(self):

        """
        TODO: implement shell commands below
cd src
/Library/Java/JavaVirtualMachines/jdk1.8.0_221.jdk/Contents/Home/bin/javac -classpath /Users/jakecariello/Box/Documents/Pipeline/access/lib/json-20190722.jar:/Applications/COMSOL54/Multiphysics/plugins/* model/*.java
/Applications/COMSOL54/Multiphysics/java/maci64/jre/Contents/Home/bin/java -cp .:$(echo /Applications/COMSOL54/Multiphysics/plugins/*.jar | tr ' ' ':'):/Users/jakecariello/Box/Documents/Pipeline/access/lib/json-20190722.jar model/FEMBuilder
cd ..

        """

        comsol_path = self.load(os.path.join('.config', 'system.json')).get('comsol_path')
        jdk_path = self.load(os.path.join('.config', 'system.json')).get('jdk_path')
        core_name = 'ModelWrapper'

        # file_name_no_ext = os.path.join('src', 'core', 'FEMBuilder')
        # run commands by system type
        # cwd = os.getcwd()

        if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):  # macOS and linux


            # TODO: RUN ./comsol server IN SEPARATE SHELL
            subprocess.Popen(['{}/bin/comsol'.format(comsol_path), 'server'], close_fds=True)
            os.chdir('src')
            os.system('{}/javac -classpath ../lib/json-20190722.jar:{}/plugins/* model/*.java -d ../bin'.format(jdk_path,
                                                                                                      comsol_path))
            submit = '{}/java/maci64/jre/Contents/Home/bin/java -cp .:$(echo {}/plugins/*.jar | tr \' \' \':\'):../lib/json-20190722.jar:../bin model/{}'.format(comsol_path,
                                                                                                              comsol_path,
                                                                                                              core_name)
            print(submit)

            os.system('{}/java/maci64/jre/Contents/Home/bin/java '
                      '-cp .:$(echo {}/plugins/*.jar | tr \' \' \':\'):../lib/json-20190722.jar:../bin model.{}'.format(comsol_path,
                                                                                                                 comsol_path,
                                                                                                                 core_name))
            os.chdir('..')


            # manifest = 'com/comsol/accessutils/MANIFEST.MF'
            #
            # os.chdir('src')
            # os.system('javac com/comsol/accessutils/*.java -classpath ../lib/json-20190722.jar -source 1.8 -target 1.8')
            # os.system('jar -cvfm {}/plugins/com.comsol.accessutils_1.0.0.jar {} '
            #           'com/comsol/accessutils/*.class'.format(comsol_path, manifest))
            # os.chdir('..')
            #
            # subprocess.call('{}/bin/comsol compile {}/{}.java '
            #           '-classpathadd {}/plugins/com.comsol.accessutils_1.0.0.jar:'
            #           '{}/lib/json-20190722.jar'.format(comsol_path, cwd, file_name_no_ext, comsol_path, cwd),shell=True)
            #
            # subprocess.call('{}/bin/comsol batch -inputfile {}/{}.class '
            #           '-dev {}/plugins/com.comsol.accessutils_1.0.0.jar,'
            #           '{}/lib/json-20190722.jar '
            #           '-plist 10.0'.format(comsol_path, cwd, file_name_no_ext, comsol_path, cwd),shell=True)

        else: # assume to be 'win64'

            # TODO: WINDOWS IMPLEMENTATION OF ABOVE CODE
            # TODO: RUN ./comsol server IN SEPARATE SHELL
            subprocess.Popen(['{}\\bin\\win64\\comsolmphserver.exe'.format(comsol_path)], close_fds=True)
            os.chdir('src')
            os.system('""{}\\javac" -cp "..\\lib\\json-20190722.jar";"{}\\plugins\\*" model\\*.java -d ../bin"'.format(jdk_path,
                                                                                                             comsol_path))
            print('here')
            print('""{}\\java\\win64\\jre\\bin\\java '
                  '-classpath .;"{}\\plugins\\*";..\\lib\\json-20190722.jar "model\\{}"'.format(comsol_path,
                                                                                                         comsol_path,
                                                                                                         core_name))
            os.system('""{}\\java\\win64\\jre\\bin\\java '
                      '-classpath .;$(echo "{}\\plugins\\*" );..\\lib\\json-20190722.jar "model\\{}"'.format(comsol_path,
                                                                                                                 comsol_path,
                                                                                                                 core_name))
            os.chdir('..')

            # manifest = 'com\\comsol\\accessutils\\MANIFEST.MF'
            #
            # os.chdir('src')
            # os.system('javac com\\comsol\\accessutils\\*.java -classpath ..\\lib\\json-20190722.jar -source 1.8 -target 1.8')
            # os.system('jar -cvfm "{}\\plugins\\com.comsol.accessutils_1.0.0.jar" {} '
            #           'com\\comsol\\accessutils\\*.class'.format(comsol_path, manifest))
            # os.chdir('..')
            #
            # subprocess.call('"{}\\bin\\win64\\comsolcompile" "{}\\{}.java" '
            #                 '-classpathadd "{}\\plugins\\com.comsol.accessutils_1.0.0.jar;'
            #                 '{}\\lib\\json-20190722.jar"'.format(comsol_path, cwd, file_name_no_ext, comsol_path, cwd),shell=True)
            #
            # subprocess.call('"{}\\bin\\win64\\comsolbatch" -inputfile "{}\\{}.class" '
            #                 '-dev "{}\\plugins\\com.comsol.accessutils_1.0.0.jar,'
            #                 '{}\\lib\\json-20190722.jar"'.format(comsol_path, cwd, file_name_no_ext, comsol_path, cwd),shell=True)

    def save_all(self):

        print('SAVE ALL')
        path_parts = [self.path(ConfigKey.MASTER, 'samples_path'), self.search(ConfigKey.MASTER, 'sample')]
        self.slide_manager.save(os.path.join(*path_parts, 'slide_manager.obj'))
        self.fiber_manager.save(os.path.join(*path_parts, 'fiber_manager.obj'))






    # def run(self):
    #     self.map = Map(self.configs[ConfigKey.MASTER.value],
    #                         self.configs[ConfigKey.EXCEPTIONS.value],
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
    #     #                     [0,  1, 0]], self.configs[ConfigKey.EXCEPTIONS.value])
    #     # print('output path: {}'.format(self.trace.write(Trace.WriteMode.SECTIONWISE,
    #     #                                                 '/Users/jakecariello/Box/SPARCpy/data/output/test_trace')))
    #
    #     # TEST: exceptions configuration path
    #     # print('exceptions_config_path:\t{}'.format(self.exceptions_config_path))
    #
    #     # TEST: retrieve data from config file
    #     # print(self.search(ConfigKey.MASTER, 'test_array', 0, 'test'))
    #
    #     # TEST: throw error
    #     # self.throw(2)
    #
    #     # self.slide = Slide([Fascicle(self.configs[ConfigKey.EXCEPTIONS.value],
    #     #                              [self.trace],
    #     #                              self.trace)],
    #     #                    self.trace,
    #     #                    self.configs[ConfigKey.MASTER.value],
    #     #                    self.configs[ConfigKey.EXCEPTIONS.value])
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
    #     self.traces = [Trace(cnt[:, 0, :], self.configs[ConfigKey.EXCEPTIONS.value]) for cnt in self.cnts]
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
    #                                             self.configs[ConfigKey.EXCEPTIONS.value],
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
    #     self.nerve = Nerve(Trace(self.nerve_cnts[0][:, 0, :], self.configs[ConfigKey.EXCEPTIONS.value]))
    #
    #     self.fascicles = Fascicle.separate_to_list(os.path.join('data', 'input', 'samples',
    #                                                             'Cadaver54-3', 'EndoneuriumMask.tif'),
    #                                                os.path.join('data', 'input', 'samples',
    #                                                             'Cadaver54-3','PerineuriumMask.tif'),
    #                                                self.configs[ConfigKey.EXCEPTIONS.value],
    #
    #
    #                                                plot=False)
    #     self.slide = Slide(self.fascicles, self.nerve,
    #                        self.configs[ConfigKey.MASTER.value],
    #                        self.configs[ConfigKey.EXCEPTIONS.value])
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
    #     self.nerve = Nerve(Trace(self.nerve_cnts[0][:, 0, :], self.configs[ConfigKey.EXCEPTIONS.value]))
    #
    #     self.fascicles = Fascicle.inner_to_list(os.path.join('data', 'input', 'samples',
    #                                                          'Pig11-3', 'FascMask.tif'),
    #                                             self.configs[ConfigKey.EXCEPTIONS.value],
    #                                             plot=False,
    #                                             scale=1.05)
    #     self.slide = Slide(self.fascicles, self.nerve,
    #                        self.configs[ConfigKey.EXCEPTIONS.value],
    #                        will_reposition=True)
    #
    #     # self.slide.reposition_fascicles(self.slide.reshaped_nerve(ReshapeNerveMode.ELLIPSE))
    #     self.slide.reposition_fascicles(self.slide.reshaped_nerve(ReshapeNerveMode.CIRCLE))
