#!/usr/bin/env python3

import sys
import os
import shutil, stat
import pyodbc, argparse, re

class OdsClient(object):
    def __init__(self, logger):
        self.logger = logger
        self.server = 'odsdb'
        self.db = 'ods'
        self.username = 'cnsscebot'
        self.passwd = 'Dragonstone20!'

        self.connStr = (r"DRIVER={{FreeTDS}};SERVER={};PORT=1433;DATABASE={};UID=na\{};PWD={};" +
            r"TDS_Version=7.0;Trusted_domain=na.qualcomm.com").format(self.server, self.db, self.username, self.passwd)

        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        if self.conn == None:
            try:
                self.conn = pyodbc.connect(self.connStr)
                if self.conn is None:
                    raise Exception('ODS server connection fails!')
                self.cursor = self.conn.cursor()
            except:
                raise Exception('connect() exception %s' % self.connStr)


    def get_salesforce(self, casenum):
        if not casenum.isdigit():
            # 'casenum' is a absolute path
            self.logger.debug('Not a valid case number: %s' %casenum)
            match = re.search(r'/([0-9]+)\Z', casenum)
            if match:
                casenum = match.group(1)

        case_dic = {}
        _QUERY = 'SELECT c.CaseNumber, c.Account, cp.CustomerProject, cp.SoftwareProduct, \
                    cp.Chipset, c.Status FROM salesforce.Cases as c \
                    LEFT JOIN salesforce.CustomerProjects as cp ON c.CustomerProjectId=cp.CustomerProjectId \
                    WHERE c.CaseNumber={}'.format(casenum)

        try:
            self.cursor.execute(_QUERY)
        except Exception as e:
            self.logger.critical(str(e))
            return None

        for row in self.cursor:
            try:
                case_dic['CaseNumber']      = str(row[0])
                case_dic['Account']         = str(row[1])
                case_dic['CustomerProject'] = str(row[2])
                case_dic['SoftwareProduct'] = str(row[3])
                case_dic['Chipset']         = str(row[4])
                case_dic['Status']          = str(row[5])
            except Exception as e:
                self.logger.critical(str(e))
                return None

            if len(case_dic['Account']) > 20:
                case_dic['Account'] = case_dic['Account'].split()[0]
            if len(case_dic['CustomerProject']) > 20:
                case_dic['CustomerProject'] = case_dic['CustomerProject'].split()[0]
            if len(case_dic['SoftwareProduct']) > 20:
                case_dic['SoftwareProduct'] = case_dic['SoftwareProduct'].split()[0]
            if len(case_dic['Chipset']) > 20:
                case_dic['Chipset'] = case_dic['Chipset'].split()[0]
            if len(case_dic['Status']) > 20:
                status_str = ''
                for i in case_dic['Status'].split():
                    status_str += (i + ' ')
                case_dic['Status'] = status_str[:-1]
        return case_dic



    def find_built(self, build):
        # TODO
        

