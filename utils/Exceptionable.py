#!/usr/bin/env python3.7

"""
File:       Exceptionable.py
Author:     Jake Cariello
Created:    July 19, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""

from utils.ExceptionManager import ExceptionManager


class Exceptionable:
    def __init__(self, exception_manager: ExceptionManager):
        self.exception_manager = exception_manager

    def throw(self, code):
        raise Exception(self.exception_manager.message(code))