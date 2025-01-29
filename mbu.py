 # Copyright © 2025 Zayus Baroon <zay@zayusbaroon@blog>

   # This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <https://www.gnu.org/licenses/>

#!/usr/bin/env python3

import sys
import os
from datetime import datetime
import time
from multiprocessing import Process
import base64

import tomllib
import getpass
import hashlib


from watcher.watcher import Watcher, get_files
from packer.packer import Packer


def regen_config():
    default = b''' user_password = ''\r\n
    [storage]
    use_database = false
    database_init_script = """DROP TABLE IF EXISTS file_data; DROP TABLE IF EXISTS dirs; CREATE TABLE files (name TEXT, lm REAL, size INTEGER, id INTEGER PRIMARY KEY); CREATE TABLE dirs (name TEXT);"""
    buffer_size = 2048
    \r\n
    [packer]
    module = 'default_packer'
    package_directory = 'packer/'
    restore_directory = 'packer/contents/'
    pigeon_directory = 'packer/send/'
    pigeon_file = 'packer/send/package'
    \r\n
    [watcher]
    module = 'default_watcher'
    '''

    with open('config.toml', 'wb') as f:
        f.write(default.encode())
        f.close()
    return

def edit_toml(toml, old_field, new_field):
    with open(toml, 'r+') as f:
        data = f.read()
        data = data.replace(old_field, new_field)
        f.seek(0)
        f.write(data)
    return

def parse_args():
    options = {'-p': None, '-o': None, '-w': None, '-d': None}
    switches = {}
    syn = {'--password': '-p', '--watch': '-w', '--package': '-o'}

    for a in range(len(sys.argv)):
        try:
            if sys.argv[a] in options:
                    options[sys.argv[a]] = sys.argv[a+1]
            elif sys.argv[a] in syn:
                options[syn[sys.argv[a]]] = sys.argv[a+1]
        except (KeyError, IndexError):
            pass

    return(options)

def monitor(watcher, packer):
    while True:
        chk = get_files(watcher.watchee)
        if watcher.update(chk) == True:
            ct = datetime.now().strftime('%H:%M:%S')
            print(f'{ct} \u2014 Change detected in {watcher.watchee}. Backing up...')
            packer.make_package()
            print('OK')


# if config['user_password'] == h.hashdigest()

def main():
    if len(sys.argv) < 2:
        print('Invalid usage: no input supplied')
        sys.exit()

    elif (sys.argv[1] == '-h' or sys.argv[1] == '--help') and len(sys.argv) == 2:
        print('''A modular backup utility, v1.0\n\nUsage: [python3] mbu.py [options] <target-directory>|| -h, --help\nOptions:
        -o, --package   : Compress <target-directory>, encrypt the compressed archive, and store result.\n
        -w, --watch     : Continuously watch <target-directory> for changes, compressing and encrypting it if any are detected.\n
        -d              : Decrypts and decompresses previously stored backup of <target-directory>. Can also be executed at the watch loop prompt.\n
        -p, --password  : Allows password to be supplied inline instead of displaying a prompt after program execution. \n''')
        sys.exit()

    if not os.path.exists(config := 'config.toml'):
        regen_config()
    with open(config, 'rb') as t:
        settings = tomllib.load(t)

    options = parse_args()
    h = hashlib.blake2s()

    if options['-p'] != None:
        pwd = options['-p']
    else:
        pwd = getpass.getpass('Enter password: ')

    h.update(pwd.encode())
    digest = h.hexdigest()
    if settings['user_password'] == "":
        cfr = getpass.getpass('Not found; creating new password. Please confirm the selected password: ')
        if pwd != cfr:
            print('Password mismatch. Exiting')
            sys.exit()
        old = r'user_password = ""'
        new = f'user_password = "{digest}"'
        edit_toml(config, old, new)

    elif digest != settings['user_password']:
        print('Password mismatch. Exiting')
        sys.exit()
    print('Password OK')

    if settings['salt'] == "":
        old = r'salt = ""'
        s = os.urandom(16)
        new = f'salt = "{base64.b64encode(s).decode()}"'
        edit_toml(config, old, new)
    else:
        s = base64.b64decode(settings['salt'])
    if options['-o'] != None and os.path.exists(options['-o']):
            packer = Packer(config, options['-o'], pwd.encode(), s)
            print(f'Packaging {packer.watchee} as {packer.outfile}')
            packer.make_package()
    elif options['-w'] != None and os.path.isdir(options['-w']):
        packer = Packer(config, options['-w'], pwd.encode(), s)
        watcher = Watcher(config, options['-w'])
        print(f'Watching {watcher.watchee} for changes...\n')
        loop = Process(target=monitor, args=[watcher, packer])
        loop.start()
        while True:
            cmd = input()
            if cmd.lower() == '-d':
                packer.depackage()
            else:
                print('Invalid command')

    elif options['-d'] != None and os.path.exists(options['-d']):
        packer = Packer(config, options['-d'], pwd.encode(), s)
        print(f'Unpacking {packer.outfile} to {packer.restore_dir}')
        packer.depackage()
    else:
        print('Invalid usage')
        sys.exit()






if __name__ == '__main__':
    main()
