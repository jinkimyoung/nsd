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
    list_dirs.append(configs.local_top)
    list_dirs.append(configs.local_cases)
    list_dirs.append(configs.local_gits)

    _check_directories(list_dirs)

    # B. _check_mysql_connection
    cnssbot = _check_mysql_connection()

    # C. _check_jira_connection()
    _check_jira_connection(configs.rest_options, cnssbot)

    # D. Update GITs
    _gits_pull(configs.local_gits)

    # E. Update LOCAL packages like QXDM / Crashscope
    _update_tools()

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

def _gits_pull(dst_top):
    g = GitManager(dst_top)
    g.update_latests()
    return

def _update_tools():
    env = EnvManager()
    env.update()
    return

if __name__ == "__main__":
    print('aa)')