#!/usr/bin/env python3.7

# for interfacing with os
import os

# for checking the OS type
import sys

def compile(self, path: str):
        # compile target java file
        os.system('javac TARGET_FILE.java')

        # set working directory for java (choose by system type)
        cwd = os.getcwd()

        if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):  # macOS and linux
            os.system('export JAVA_HOME={}'.format(cwd))
        else:  # sys.platform would be 'win32'
            os.system('set path={}'.format(cwd))

        # run target java file
        os.system('java TARGET_FILE')  # note absence of ".java"

def run(self, path: str):

#    from src.utils import java
 #   java.compile()
  #  java.run()



