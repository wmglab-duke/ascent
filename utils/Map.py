#!/usr/bin/env python3.7

"""
File:       Map.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""
from utils.ExceptionManager import ExceptionManager
import os
import re
import datetime
import numpy as np

class Map:

    def __init__(self, new: bool, path: str, exception_manager: ExceptionManager):
        """
        :param new: indicate whether or not to build new Map
        :param path: MUST exist (to find path to save/load)
        """

        self.exception_manager = exception_manager

        #%% assign file name
        if path[-1] in ['/', '\\']:  # path is a directory (only makes sense if new map)
            self.file = os.path.join(path[:-1], self.__path())

            if not new:
                raise Exception(exception_manager.message(1))

        else:  # path given is a file
            self.file = path

        #%% choose
        if new:  # new slide map must be generated
            pass


        else:  # old slide map will be used
            pass


    @staticmethod
    def build_new(path = ''):
        pass

    def __path(self):
        """
        :return: newly generated path name with date stamp
        """
        return 'map_{}.csv'.format(datetime.datetime.now().strftime('%m%d%Y'))