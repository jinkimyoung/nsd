#!/usr/bin/env python3

import os
import json

class OmegaJson:
    def __init__(self):
        self.omega_data = None
        self._mandatories = ( 'accountName', 'ownerLocation1', 'subject', 'description',\
                            'taxmanProductLine', 'problemCode1', 'problemCode2', 'problemCode3', \
                            'caseNumber' , 'ccChipset', 'ownerEmail', 'customerProjectName', \
                            'latestQualcommComment', 'softwareImageBuildInformation')

    def read_from_file(self, fpath):
        try:
            if not os.path.exists(fpath):
                return False
            with open(fpath) as f:
                self.omega_data = json.load(f)
        except Exception as ERR:
            print('Exception in read_from_file() : '+str(ERR))
            return False

        return self._sanity()

    def _sanity(self):
        for _key in self._mandatories:
            if not _key in self.omega_data.keys():
                raise Exception('some Key are not present')
        return True

    def print_data(self):
        for key in self.omega_data.keys():
            value = self.omega_data[key]
            print(f'[{key}] : [{value}]')

    def get_data(self):
        return self.omega_data

    def UnitTest(self):
        self.read_from_file(r'C:\Temp\case.json')
        self.print_data()
        self.get_data()     



