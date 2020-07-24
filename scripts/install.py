#!/usr/bin/env python3.7

import os
import sys
import subprocess

def run(args):
    sys.argv = args

    proc = None

    if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        proc = subprocess.Popen(['bash', './config/system/installation/install.sh'])
    else:
        proc = subprocess.Popen(['powershell.exe', '.\\config\\system\\installation\\install.ps1'])

    proc.wait()

