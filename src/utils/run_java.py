# for interfacing with os
import os

# for checking the OS type
import sys

# compile target java file
os.system('javac TARGET_FILE.java')

# set working directory for java (choose by system type)
cwd = os.getcwd()
if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):  # macOS and linux
    os.system('export JAVA_HOME={}'.format(cwd))
else:  # sys.pltaform would be 'win32'
    os.system('set path={}'.format(cwd))

# run target java file
os.system('java TARGET_FILE')  # note absence of ".java"