#!/usr/bin/env python3.7

import os
import sys
import subprocess

def run(args):
    sys.argv = args
    
    if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        subprocess.Popen(['bash ./config/system/installation/install.sh'])
    else:
        subprocess.Popen(['.\config\system\installation\install.ps1'])

