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
import os

from src.core import *
from src.utils import *
import cv2
import matplotlib.pyplot as plt
import numpy as np


class Runner(Exceptionable, Configurable):

    def __init__(self, config_file_path: str):

        # initialize Configurable super class
        Configurable.__init__(self, SetupMode.NEW, ConfigKey.MASTER, config_file_path)

        # get config path info from config and set to class vars
        self.exceptions_config_path = self.path(ConfigKey.MASTER, 'config', 'paths', 'exceptions')

        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW, self.exceptions_config_path)

    def run(self):
        # self.map = SlideMap(self.configs[ConfigKey.MASTER.value],
        #                     self.configs[ConfigKey.EXCEPTIONS.value],
        #                     mode=SetupMode.NEW)

        # TEST: Trace functionality
        # self.trace = Trace([[0,  0, 0],
        #                     [2,  0, 0],
        #                     [4,  0, 0],
        #                     [4,  1, 0],
        #                     [4,  2, 0],
        #                     [2,  2, 0],
        #                     [0,  2, 0],
        #                     [0,  1, 0]], self.configs[ConfigKey.EXCEPTIONS.value])
        # print('output path: {}'.format(self.trace.write(Trace.WriteMode.SECTIONWISE,
        #                                                 '/Users/jakecariello/Box/SPARCpy/data/output/test_trace')))

        # TEST: exceptions configuration path
        # print('exceptions_config_path:\t{}'.format(self.exceptions_config_path))

        # TEST: retrieve data from config file
        # print(self.search(ConfigKey.MASTER, 'test_array', 0, 'test'))

        # TEST: throw error
        # self.throw(2)

        # self.slide = Slide([Fascicle(self.configs[ConfigKey.EXCEPTIONS.value],
        #                              [self.trace],
        #                              self.trace)],
        #                    self.trace,
        #                    self.configs[ConfigKey.MASTER.value],
        #                    self.configs[ConfigKey.EXCEPTIONS.value])
        pass

    def trace_test(self):

        # build path and read image
        path = os.path.join('data', 'tracefile2.tif');
        img = cv2.imread(path, -1)

        # get contours and build corresponding traces
        # these are intentionally instance attributes so they can be inspected in the Python Console
        self.cnts, self.hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.traces = [Trace(cnt[:, 0, :], self.configs[ConfigKey.EXCEPTIONS.value]) for cnt in self.cnts]

        # plot formats
        formats = ['r', 'g', 'b']

        # original points and centroids
        title = 'Figure 0: original traces with calculated centroids'
        print(title)
        plt.figure(0)
        plt.axes().set_aspect('equal', 'datalim')
        for i, trace in enumerate(self.traces):
            trace.plot(formats[i] + '-')
            trace.plot_centroid(formats[i] + '*')
        plt.legend([str(i) for i in range(len(self.traces)) for _ in (0, 1)]) # end of this line is to duplicate items
        plt.title(title)
        plt.show()

        # ellipse/circle/original comparison (trace 0)
        title = 'Figure 1: fit comparisons (trace 0)'
        print(title)
        plt.figure(1)
        plt.axes().set_aspect('equal', 'datalim')
        self.traces[0].plot(formats[0])
        self.traces[0].to_circle().plot(formats[1])
        self.traces[0].to_ellipse().plot(formats[2])
        plt.legend(['original', 'circle', 'ellipse'])
        plt.title(title)
        plt.show()

        # example stats
        pairs = [(0, 1), (1, 2), (2, 0)]
        print('\nEXAMPLE STATS')
        for pair in pairs:
            print('PAIR: ({}, {})'.format(*pair))
            print('\tcent dist:\t{}'.format(self.traces[pair[0]].centroid_distance(self.traces[pair[1]])))
            print('\tmin dist:\t{}'.format(self.traces[pair[0]].min_distance(self.traces[pair[1]])))
            print('\tmax dist:\t{}'.format(self.traces[pair[0]].max_distance(self.traces[pair[1]])))
            print('\twithin:\t\t{}'.format(self.traces[pair[0]].within(self.traces[pair[1]])))

        title = 'Figure 2: Scaled trace'
        print(title)
        plt.figure(2)
        plt.axes().set_aspect('equal', 'datalim')
        self.traces[0].plot(formats[0])
        self.traces[0].scale(1.2)
        self.traces[0].plot(formats[1])
        plt.legend(['original', 'scaled'])
        plt.title(title)
        plt.show()

    def fascicle_test(self):
        # build path and read image
        path = os.path.join('data', 'tracefile3.tif');

        self.img = np.flipud(cv2.imread(path, -1))

        # get contours and build corresponding traces
        # these are intentionally instance attributes so they can be inspected in the Python Console
        self.cnts, self.hierarchy = cv2.findContours(self.img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.fascicles = Fascicle.list_from_contours(self.cnts, self.hierarchy[0],
                                                     self.configs[ConfigKey.EXCEPTIONS.value],
                                                     plot=True,
                                                     scale=1.03)


    def reposition_test(self):
        # build path and read image
        path = os.path.join('data', 'Cadaver54-3_NerveMask.tif');
        path2 = os.path.join('data', 'Cadaver54-3_PerineuriumMask.tif');

        self.img = np.flipud(cv2.imread(path, -1))
        self.img2 = np.flipud(cv2.imread(path2, -1))

        # get contours and build corresponding traces
        # these are intentionally instance attributes so they can be inspected in the Python Console
        self.cnts, self.hierarchy = cv2.findContours(self.img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Nerve = Nerve.list_from_contours(self.cnts, self.hierarchy[0],
                                                     self.configs[ConfigKey.EXCEPTIONS.value],
                                                     plot=True)
        self.slide = Slide(self.fascicles,)

        self.cnts2, self.hierarchy2 = cv2.findContours(self.img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.fascicles = Fascicle.list_from_contours(self.cnts, self.hierarchy[0],
                                                     self.configs[ConfigKey.EXCEPTIONS.value],
                                                     plot=True)
