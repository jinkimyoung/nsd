#!/usr/bin/env python3

# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook

import os
import logging


import Configs
import GitManager
import EnvManager

from jira.client import JIRA


logging.basicConfig(format='%(asctime)s %(message)s')
logging.warning('is when this event was logged.')


def check_all_dependency():
    # check & create directory

    configs = Configs()

    # A. _check_directories
    list_dirs = [] 
    list_dirs.append(self.top_local)
    _check_directories(list_dirs)

    # B. _check_mysql_connection
    cnssbot = _check_mysql_connection()

    # C. _check_jira_connection()
    _check_jira_connection(configs.rest_options, cnssbot)

    return

def _check_directories(dsts):
    try:
        for dst in dsts:
            if not os.path.exists(dst):
                os.mkdir(dst, mode=0o777)
    except Exception as ERR:
        print('[CIRITICAL] '+str(ERR))
        raise Exception(str(ERR))
    return

def _check_mysql_connection():

    # A. connect MYSQL
    # B. Get CNSSJIRA

#   DB = MysqlManager(logger = logger, db_host=c.db_host, \
#                    db_user=c.db_user, db_pwd=c.db_pwd, \
#                    db_name=c.db_name, db_charset=c.db_charset)
#    DB.connect()
#    logger.info('c.db_opmode : %s' % (c.db_opmode))
#    if c.db_opmode == 'RESET':
#        DB.drop_tables()
#    DB.create_tables()

#    account = DB.pwd_cnsscebot()
#    jira_id = account['ID']
#    jira_pwd = account['PWD']
#    DB.disconnect()
    pass

def _check_jira_connection(rest_options, account):
    try:
        # check JIRA PWD
        print('f{account[\'id\']}, {account[\'pwd\']}')

        client = JIRA(basic_auth=(account['id'], account['pwd']))
    except JIRAError as e:
        status_code = e.status_code

        if status_code == AUTH_ERROR_CODE:
            raise Exception('JIRA Connection Error(%d)' % status_code)

    except Exception as ERR:
        print('[CIRITICAL] '+str(ERR))
        raise Exception(str(ERR))
    return


def _pull_gits():
    g = GitManager(r'c:\temp')
    g.TestUnit()






env = EnvManager()
env.update()


if __name__ == "__main__":
    print('aa)')