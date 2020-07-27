#!/usr/bin/env python3

import os
import sqlite3
import subprocess

class NetworkSync:
    def __init__(self, src, dst):
        self._src = src if os.path.exists(src) else None
        self._dst = dst if os.path.exists(dst) else None

        if self._src is None or self._dst is None:
            raise Exception(f"Path is wrong - src({self._src}), dst({self._dst})")

        print(self._src, self._dst)

        # DB
        self._db = os.path.join(self._dst, 'syncs.db')
        self._connect()

    def __del__(self):
        self._disconnect()
            
    def _connect(self):
        self._conn = sqlite3.connect(self._db)
        self._cursor = self._conn.cursor()
        self._create_syncdb()

    def _disconnect(self):
        if self._conn != None:
            self._conn.close()
            del(self._conn)

    def _create_syncdb(self):
        self._cursor.execute('CREATE TABLE IF NOT EXISTS flist(path text UNIQUE, size int)')

    def exist_in_syncdb(self, fname):
        print(f' exist_in_syncdb({fname})')
        try:
            self._conn.execute(f"SELECT COUNT(*) FROM flist WHERE path=\'{fname}\'")
            ret = True if self._conn.fetchall()[0][0] == 1 else False
            print(ret)
            return ret
        except Exception as ERR:
            print('SQLITE3 - ERR : '+str(ERR))
            return False

    def insert_or_update_syncdb(self, fpath):
        size = os.path.getsize(fpath)
        print(f'insert_or_update_syncdb({fpath} : {size})')
        try:
            self._cursor.execute(f'INSERT OR REPLACE INTO flist(path, size)  VALUES (\'{fpath}\', {size})')
            self._conn.commit()
        except Exception as ERR:
            print('SQLITE3 - ERR : '+str(ERR))
        return

    def list_in_dst(self):
        try:
            self._cursor.execute('SELECT path, size FROM flist')
            dlist = { r[0]:r[1] for r in self._cursor.fetchall() }
            print(dlist)
        except Exception as ERR:
            print('SQLITE3 - ERR : '+str(ERR))
        return dlist

    def list_in_src(self):
        d = { f:os.path.getsize(os.path.join(self._src,f)) for f in os.listdir(self._src) if os.path.isfile(os.path.join(self._src,f)) }
        print(d)
        return d

    def determine_list_for_sync(self):
        print('In determine_list_for_sync()')
        slist = self.list_in_src()
        dlist = self.list_in_dst()

        nlist = []
        for fname in slist.keys():
            if dlist.get(fname) == None:
                nlist.append(fname)
            elif slist[fname] != dlist[fname]:
                nlist.append(fname)             

        print(nlist)
        return nlist

    def file_sync(self, sdir, ddir, fname):
        # "robocopy \\localhost\abcde c:\temp 2222.txt"
        cmd = ['robocopy', sdir, ddir, fname ]
        _robocode = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = _robocode.wait()
        return ret

    def fsyncs(self):
        slist = self.determine_list_for_sync()

        for fname in slist:
            self.file_sync(self._src, self._dst, fname)
            #self.update_syncdb(fname, slist[fname]) if self.exist_in_syncdb(fname) else self.insert_syncdb(fname, slist[fname])
            self.insert_or_update_syncdb(fname)

        return

    def UnitTest(self):
        self._src = r'\\localhost\abcde'
        self._dst = r'C:\Temp\abcde'

        list_src = self.list_in_src()
        for fname in list_src.keys():
            self.insert_or_update_syncdb(fname)
            self.exist_in_syncdb(fname+'aa')
            self.exist_in_syncdb(fname)
        self.determine_list_for_sync()


#pwd = r'\\localhost\abcde'
#os.listdir(r'\\localhost\abcde')

#for f in os.listdir(r'\\localhost\abcde'):
#    sf = os.path.join(r'\\localhost\abcde', f)
#    print(f, sf)
#    print(os.path.getsize(sf))

#>>> age = 15
#>>> # Conditions are evaluated from left to right
#>>> print('kid' if age < 18 else 'adult')
#kid

# [x for x in range(1, 10) if x % 2 else x * 100]