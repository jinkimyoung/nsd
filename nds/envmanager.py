#!/usr/bin/env python3

import os
import yaml

# Ref : https://stackabuse.com/reading-and-writing-yaml-to-a-file-in-python/

class EnvManager():
    def __init__(self):
        self._top =  os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        self._fyml = os.path.join(self._top, 'configure', 'envs.yml')
        self._envs = { 'CRASHSCOPE' : r'C:\\ProgramData\\QUALCOMM\\Crashscope\\1.5.40.33', 'QXDM4' : r'C:\Program Files (x86)\Qualcomm\QXDM4' }
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
                    print(f'os.environ[\'CRASHSCOPE\'] is updated : {latest}')
            else:
                pass

    def save_genvs(self):
        try:
            with open(self._fyml, 'w') as file:
                documents = yaml.dump(self._envs, file)
        except Exception as ERR:
            print('[CRITICAL]In save_genvs() : '+str(ERR))

        if not os.path.exists(self._fyml):
            raise Exception(f'{self._fyml} is not present')

    def read_genvs(self):
        if not os.path.exists(self._fyml):
            raise Exception(f'{self._fyml} is not present')

        try:
            with open(self._fyml, "r") as ymlfile:
                _genv = yaml.load(ymlfile)

            gitlist = [ _genv[section]['git'] for section in _genv if 'git' in _genv[section].keys() ]
            print(gitlist)
            return gitlist
        except Exception as ERR:
            print('[CRITICAL]In _get_gits() : '+str(ERR))

    def TestUnit(self):
        self.find_latest_in_local()
        self.save_genvs()




e = EnvManager()
e.find_latest_in_local()
e.save_genvs()
