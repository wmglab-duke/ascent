#!/usr/bin/env python3.7

# for interfacing with os
import os

# for checking the OS type
import sys


class Javable:

    def compile_file(self, path: str):
        # compile target java file
        compile_java_file_prompt = "javac %s.java" % path
        os.system(compile_java_file_prompt)

    def run_file(self, path: str):
        # set working directory for java (choose by system type)
        cwd = os.getcwd()

        if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):  # macOS and linux
            os.system('export JAVA_HOME={}'.format(cwd))
        else:  # sys.platform would be 'win32'
            os.system('set path={}'.format(cwd))

        # run target java file
        run_java_file_prompt = "java %s" % path
        os.system(run_java_file_prompt)  # note absence of ".java"

    def compile_and_run(self, path: str):
        self.compile_file(path)
        self.run_file(path)
