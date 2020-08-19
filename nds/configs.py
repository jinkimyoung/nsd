#!/usr/bin/env python3

import os
import yaml
import platform

class Configs():
    def __init__(self):
        _top = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._fyml = os.path.join(_top, 'configure', 'configs.yml') 
        if not os.path.exists(self._fyml):
            raise Exception(f'Check Path : {self._fyml}')
        self._read()
        self._processing()

    def _read(self):
        try:
            with open(self._fyml, "r") as ymlfile:
                self._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
            print(self._cfg)
        except Exception as ERR:
            print('[CRITICAL] '+str(ERR))

    def _processing(self):
        if not hasattr(self, '_cfg'):
            raise Exception('Do _read() first')

        print(self._cfg['SERVERLIST'])

        # Server & Region
        self.server = platform.uname()[1]
        self.region = 'SD'
        for _key in self._cfg['SERVERLIST'].keys():
            if _key == self.server:
                self.region = self._cfg['SERVERLIST'][_key]['region']
                break
        print(f'{self.server} in {self.region}')

        # OMETA
        if self._cfg.get('OMEGA') != None:
            self.omega_src = self._cfg['OMEGA']
            print(f'{len(self.omega_src)}')
            for fxlx in self.omega_src:
                print(f'{fxlx}')
        else:
            raise Exception('Key[OMEGA] is not present')

        # PATH
        if self._cfg.get('WORKSPACE') != None:
            self.local_top = self._cfg['WORKSPACE']['LOCAL']
            self.network_top = os.path.join(r'\\', self.server, self._cfg['WORKSPACE']['NETWORK'])
            self.local_cases = os.path.join(self.local_top, self._cfg['WORKSPACE']['CASES'])
            self.local_gits = os.path.join(self.local_top, self._cfg['WORKSPACE']['GITS'])

            print(f'{self.local_top}, {self.network_top}, {self.local_cases}, {self.local_gits}')
        else:
            raise Exception('Key[WORKSPACE] is not present')

        #for _key in self._cfg['SERVERLIST'].keys():

        if self._cfg.get('CHIPSETS') != None:
            self.chipsets = []
            print(len(self._cfg.get('CHIPSETS')))
            for chipset in self._cfg['CHIPSETS']:
                self.chipsets += set(self._cfg['CHIPSETS'][chipset])
            print(self.chipsets)
        else:  
            raise Exception('Key[CHIPSETS] is not present')

        if self._cfg.get('JIRA_RESTOPT') != None:
            self.rest_options = self._cfg['JIRA_RESTOPT']
            print(self.rest_options)
        else:
            raise Exception('Key[JIRA_RESTOPT] is not present')

    def get_mysql(self):
        if self._cfg.get('DB') != None:
            return self._cfg['DB']
        else:  
            raise Exception('Key[DB] is not present')

    def _print(self):
        print(self.genv)       

c = Configs()
print(c.get_mysql())
