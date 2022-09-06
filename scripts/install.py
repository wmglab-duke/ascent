#!/usr/bin/env python3.7

"""Installs ASCENT.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import subprocess
import sys


def run(args):
    """Install ASCENT."""

    def ensure_dir(directory):
        """Ensure a directory exists."""
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
        'config/user/sims',
    ]

    for path in defdirs:
        ensure_dir(path)

    # download required JAR(s)
    jars = ['https://repo1.maven.org/maven2/org/json/json/20190722/json-20190722.jar']
    for jar in jars:
        retrieve = True
        target = os.path.join(binpath, jar.split('/')[-1])
        if os.path.exists(target):
            reply = input(f'{target} already found! download again and overwrite? [y/N] ').lower().strip()
            if reply[0] != 'y':
                print('Not overwriting.\n')
                retrieve = False
            else:
                print('Overwriting.\n')

        if retrieve:
            print(f'Downloading {jar} to {target}')
            if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
                subprocess.run(['curl', '-o', target, jar])
            else:
                with subprocess.Popen("powershell.exe", stdin=subprocess.PIPE) as p:
                    p.stdin.write(
                        '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12\n'.encode()
                    )
                    p.stdin.write(f'$source = \'{jar}\'\n'.encode())
                    p.stdin.write(f'$destination = \'{os.path.abspath(target)}\'\n'.encode())
                    p.stdin.write('curl $source -OutFile $destination'.encode())

    # run system-specific installation
    if args.no_conda:
        print('Skipping conda portion of installation\n')
    else:
        if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
            subprocess.check_call(["source", "config/system/installation/install.sh", "-i"], executable="/bin/bash")
        else:
            subprocess.check_call(['powershell.exe', '.\\config\\system\\installation\\install.ps1'])
    print('Installation complete!\n')
