import subprocess
import sys, time


# https://stackoverflow.com/questions/39432305/python-how-to-find-uuid-of-computer-and-set-as-variable

def run(args):
    my_OS = 'UNIX-LIKE' if any([s in sys.platform for s in ['darwin', 'linux']]) else 'WINDOWS'
    my_uuid = None
    if my_OS == 'UNIX-LIKE':
        dmidecode = subprocess.Popen(['dmidecode'],
                                     stdout=subprocess.PIPE,
                                     bufsize=1,
                                     universal_newlines=True
                                     )

        while True:
            line = dmidecode.stdout.readline()
            if "UUID:" in str(line):
                my_uuid = str(line).split("UUID:", 1)[1].split()[0]
            if not line:
                break
    elif my_OS == 'WINDOWS':
        my_uuid = subprocess.check_output('wmic csproduct get UUID')
        print('here')

    print("My ID:", my_uuid)
    return my_uuid
