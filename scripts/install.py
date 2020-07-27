#!/usr/bin/env python3

import os
import sys
import subprocess

def run(args):
    sys.argv = args

 
    if sys.version_info[0] < 3:
        raise Exception('Installation must be run using Python 3.\nTry \'./run install\' or \'python3 run install\'.\n')

    reply = input('Have you navigated to the root of the ASCENT repository? [y/N] ').lower().strip()
    if reply[0] is not 'y':
        print('Please do so and re-run.\n')
        sys.exit()
    else:
        print('Great, proceeding with installation.\n')

    # download required JAR(s)
    bin = 'bin'
    if not os.path.exists(bin):
        os.mkdir(bin)

    jars = ['https://repo1.maven.org/maven2/org/json/json/20190722/json-20190722.jar']
    for jar in jars:
        retrieve = True
        target = os.path.join(bin, jar.split('/')[-1])
        if os.path.exists(target):
            reply = input('{} already found! download again and overwrite? [y/N] '.format(target)).lower().strip()
            if reply[0] is not 'y':
                print('Not overwriting.\n')
                retrieve = False
            else:
                print('Overwriting.\n')

        if retrieve:
            print('Downloading {} to {}'.format(jar, target))
            if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
                subprocess.Popen(['wget', '-q', '-O', target, jar]).wait()
            else:
                subprocess.Popen([
                    'powershell.exe -Command \"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest {} -OutFile {}\"'.format(jar, target),
                ], shell=True).wait()

    # run system-specific installation
    proc = None

    if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        proc = subprocess.Popen(['bash', './config/system/installation/install.sh'])
    else:
        proc = subprocess.Popen(['powershell.exe', '.\\config\\system\\installation\\install.ps1'])
    
    proc.wait()

