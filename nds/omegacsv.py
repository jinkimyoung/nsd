#!/usr/bin/env python3

import os
import csv
import re
import panda as pd
from datetime import datetime

class OmegaCSV:
    def __init__(self, file_csv):
        self._mandatory = [ 'CaseNumber', 'AccountName', 'CustomerProjectName', \
                            'OwnerName', 'OwnerEmail', 'OwnerLocation1', 'CreatedDate', \
                            'ProblemCode1', 'ProblemCode2', 'ProblemCode3', \
                            'CcChipset', 'TaxmanProductLine', 'Subject' ]

        self.chips_supported = config().chips_supported

        if len(file_csv) == 1:
            self.file_csv = file_csv if os.path.exists(file_csv) else None
            if self.file_csv is None:
                raise Exception(f'{file_csv} is not present')
        else:
            self.file_csv = file_csv 
            for f in self.file_csv:
                if not os.path.exists(f):
                    raise Exception(f'{f} is not present')
        self.read()

    def __del__(self):
        pass

    def read(self):
        try:
            if len(file_csv) == 1:
                self._rows = csv.DictReader(open(self.csv_file))
            else:
                # Use PD
                df_merged = pd.concat([pd.read_csv(f, sep=',') for f in self.csv_file], ignore_index=True, sort=False)
                self._rows = df_merged 

        except Exception as ERR:
            print('[CRITICAL] '+str(ERR))

    def _convert_date(self, date_in):
        #date_in = 'Mon Jun 22 23:52:43 PDT 2020'

        g = re.search('(.*) (.*) (.*) (.*)\:(.*)\:(.*) (.*) (.*)', date_in)
        if g is None: 
            raise Exception('input is wrong')
        date = datetime.strptime(g.group(8)+'-'+g.group(2)+'-'+g.group(3), '%Y-%b-%d').strftime('%Y-%m-%d')
        print(date)
        return date

    def _trim(self, input):
        trimed = { _key : input[_key] for _key in self._mandatory }
        trimed['CreatedDate'] = self._convert_date(trimed['CreatedDate'])
        return trimed 

    def _filter(self, subtech, row):
        if row['ProblemCode1'] != 'Wireless Connectivity Software':
            return True

        if not row['CcChipset'] in self.chips_supported:
            return True
        elif row['OwnerName'] in ['Kimyoung Jin']:
            return False

        return False

    def get_active_cases(self, run_mode, reflash = False):
        cases = [] 

        if reflash == True:
            self.read()

        for _row in self._rows:
            trimed_record = self._trim(_row)
            if self._filter(trimed_record):
                continue
            cases.append(trimed_record)

        return cases



    

