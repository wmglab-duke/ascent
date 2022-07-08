#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os
import subprocess
import sys


def run(args):

    def ensure_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    sys.argv = args

    if sys.version_info[0] < 3:
        raise Exception('Installation must be run using Python 3.\nTry \'./run install\' or \'python3 run install\'.\n')

    reply = input('Have you navigated to the root of the ASCENT repository? [y/N] ').lower().strip()
    if reply[0] != 'y':
        print('Please do so and re-run.\n')
        sys.exit()
    else:
        print('Great, proceeding with installation.\n')

    # define and generate user directories
    binpath = 'bin'
    defdirs = [
        binpath,
        'samples',
        'input',
        'config/user',
        'config/user/runs',
        'config/user/sims']

    for path in defdirs:
        ensure_dir(path)

    # download required JAR(s)
    jars = ['https://repo1.maven.org/maven2/org/json/json/20190722/json-20190722.jar']
    for jar in jars:
        retrieve = True
        target = os.path.join(binpath, jar.split('/')[-1])
        if os.path.exists(target):
            reply = input('{} already found! download again and overwrite? [y/N] '.format(target)).lower().strip()
            if reply[0] != 'y':
                print('Not overwriting.\n')
                retrieve = False
            else:
                print('Overwriting.\n')

        if retrieve:
            print('Downloading {} to {}'.format(jar, target))
            if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
                subprocess.Popen(['wget', '-q', '-O', target, jar]).wait()
            else:
                p = subprocess.Popen("powershell.exe", stdin=subprocess.PIPE)
                p.stdin.write(
                    '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12\n'.encode())
                p.stdin.write('$source = \'{}\'\n'.format(jar).encode())
                p.stdin.write('$destination = \'{}\'\n'.format(os.path.abspath(target)).encode())
                p.stdin.write('curl $source -OutFile $destination'.encode())
                p.stdin.close()

    # run system-specific installation
    if args.no_conda:
        print('Skipping conda portion of installation\n')
    else:
        proc = None

        if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
            proc = subprocess.Popen("source config/system/installation/install.sh -i", shell=True, executable="/bin/bash")
        else:
            proc = subprocess.Popen(['powershell.exe', '.\\config\\system\\installation\\install.ps1'])

        proc.wait()
    print('Installation complete!\n')
