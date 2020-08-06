#!/usr/bin/env python3

import os
import json

class OmegaJson:
    def __init__(self):
        self.omega_data = None
        self._mandatories = ( 'caseNumber', 'accountName', 'customerProjectName', \
                                'ownerName' , 'ownerEmail', 'ownerLocation1', 'createdDate', \
                                'problemCode1', 'problemCode2', 'problemCode3', \
                                'ccChipset', 'taxmanProductLine', \
                                'subject', 'description',\
                                'latestQualcommComment')

        # JSON to SF
        self._match_key = { 'caseNumber' : 'caseNumber', \
                        'accountName' : 'AccountName', \
                        'customerProjectName' : 'CustomerProjectName', \
                        'ownerName' : 'OwnerName', \
                        'ownerEmail' : 'OwnerEmail', \
                        'ownerLocation1' : 'OwnerLocation1', \
                        'createdDate' : 'CreatedDate', \
                        'problemCode1' : 'ProblemCode1', \
                        'problemCode2' : 'ProblemCode2', \
                        'problemCode3' : 'ProblemCode3', \
                        'ccChipset' : 'CcChipset', \
                        'taxmanProductLine' : 'TaxmanProductLine', \
                        'subject' : 'Subject', \
                        'description' : 'Description', \
                        'latestQualcommComment' : 'LatestQualcommComment'
                    }

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
        print('In get_data()')
        out = { self._match_key[_key] : _value for (_key, _value) in self.omega_data.items() if _key in self._mandatories }
        print(out)
        return out 

    def UnitTest(self):
        self.read_from_file(r'C:\Temp\case.json')
        self.print_data()
        self.get_data()     

#o = OmegaJson()
#o.UnitTest()
