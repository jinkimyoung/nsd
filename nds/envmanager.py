#!/usr/bin/env python3

import os
import yaml

# Ref : https://stackabuse.com/reading-and-writing-yaml-to-a-file-in-python/

class EnvManager():
    def __init__(self):
        self._top =  os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        self._fyml = os.path.join(self._top, 'configure', 'envs.yml')
        self._envs = { 'CRASHSCOPE' : r'C:\\ProgramData\\QUALCOMM\\Crashscope\\1.5.40.33', 'QXDM4' : r'C:\Program Files (x86)\Qualcomm\QXDM4' }

    def update(self):
        self.read_genvs()
        self.find_latest_in_local()

    def find_latest_in_local(self):
        for env in self._envs.keys():
            if env == 'CRASHSCOPE':
                topdir = os.path.dirname(self._envs['CRASHSCOPE'])
                
                dirs = [ d for d in os.listdir(topdir) if os.path.isdir(os.path.join(topdir, d)) ]
                dirs.sort()
                latest = os.path.join(os.path.dirname(self._envs['CRASHSCOPE']), dirs[-1])

                if os.environ.get('CRASHSCOPE') != latest:
                    os.environ['CRASHSCOPE'] = latest
                    self._envs['CRASHSCOPE'] = latest
                    self.save_genvs()
                    print(f'os.environ[\'CRASHSCOPE\'] is updated : {latest}')
            else:
                pass

    def save_genvs(self):
        print('In save_genvs()')
        try:
            with open(self._fyml, 'w') as file:
                yaml.dump(self._envs, file)
        except Exception as ERR:
            print('[CRITICAL]In save_genvs() : '+str(ERR))

        if not os.path.exists(self._fyml):
            raise Exception(f'{self._fyml} is not present')

    def read_genvs(self):
        print('In read_genvs()')
        if not os.path.exists(self._fyml):
            raise Exception(f'{self._fyml} is not present')

        try:
            with open(self._fyml, "r") as ymlfile:
                _genv = yaml.load(ymlfile, Loader=yaml.FullLoader)
                self._envs = _genv
                print(_genv)
        except Exception as ERR:
            print('[CRITICAL]In _get_gits() : '+str(ERR))

    def TestUnit(self):
        self.read_genvs()
        self.find_latest_in_local()


#e = EnvManager()
#e.TestUnit()
#e.find_latest_in_local()
#e.save_genvs()
