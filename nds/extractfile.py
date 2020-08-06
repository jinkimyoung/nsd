#!/usr/bin/env python3

import os
import sqlite3
import subprocess
import shutil

class ExtractFile():
    def __init__(self, top):
        # https://www.7-zip.org/
        ## Packing / unpacking: 7z, XZ, BZIP2, GZIP, TAR, ZIP and WIM
        ## Unpacking only: AR, ARJ, CAB, CHM, CPIO, CramFS, DMG, EXT, FAT, GPT, HFS, IHEX, ISO, LZH, LZMA, MBR, MSI, NSIS, NTFS, QCOW2, RAR, RPM, SquashFS, UDF, UEFI, VDI, VHD, VMDK, WIM, XAR and Z
        self._ext_7z = ('.ZIP', '.zip', '.7z', '.rar', '.tar', '.tz', '.tgz', '.bz2', '.gz')
        self._ext_alzip = ('.egg', '.EGG')
        self._archive_list = set(self._ext_7z + self._ext_alzip)
        # Note : Set deletes the duplicated item -> Use this for list

        self._top = top if os.path.exists(top) else Exception(f"Path is wrong - src({self._top})")

        # DB
        self._db = os.path.join(self._top, 'archives.db')
        self._connect()

    def __del__(self):
        self._disconnect()
            
    def _connect(self):
        self._conn = sqlite3.connect(self._db)
        self._cursor = self._conn.cursor()
        self._create_archeive()

    def _disconnect(self):
        if hasattr(self, '_conn') and self._conn != None:
            self._conn.close()
            del(self._conn)

    def _removes(self, dst):
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
        except Exception as ERR:
            print(str(ERR))
        return

    def _mkdir(self, dst):
        try:
            os.mkdir(dst, mode=0o777)
        except Exception as ERR:
            print(str(ERR))
        return

    def _create_archeive(self):
        self._cursor.execute('CREATE TABLE IF NOT EXISTS archives(path TEXT UNIQUE, size INT)')
        print('done : _create_archeive()')

    def is_candidate(self, fpath, size):
        print(f'get_archeive({fpath}, {size})')
        try:
            self._cursor.execute(f"SELECT path, size FROM archives WHERE path=\'{fpath}\'")
            res = self._cursor.fetchall()
            if len(res) == 0:
                print(f'len(res) is zero')
                return True
            elif len(res) == 1:
                print(f'len(res) is 1 : {res[0][0]}, {res[0][1]}')

                if res[0][1] < size:
                    # Delete previous folder if the previous size is smaller than now
                    self._removes(self._get_dst(fpath))

                return False if res[0][1] == size else True
            else:
                raise Exception('unexpected')
        except Exception as ERR:
            print('SQLITE3 - ERR : '+str(ERR))
            return False

    def insert_or_update_archeive(self, fpath):
        size = os.path.getsize(fpath)
        print(f'insert_or_update_archeive({fpath} : {size})')
        try:
            self._cursor.execute(f'INSERT OR REPLACE INTO archives(path, size)  VALUES (\'{fpath}\', {size})')
            self._conn.commit()
        except Exception as ERR:
            print('SQLITE3 - ERR : '+str(ERR))
        return

    def _permission_recursive(self, tpath):
        if os.path.exists(tpath):
            os.chmod(tpath, 0o777)
        
        for base, dirs, files in os.walk(tpath, topdown=False):
            for _dir in [os.path.join(base, d) for d in dirs]:
                os.chmod(_dir, 0o777)
            for _file in [os.path.join(base, f) for f in files]:
                os.chmod(_file, 0o777)

    def _get_dst(self, fpath):
        return os.path.join(os.path.dirname(fpath), os.path.splitext(os.path.basename(fpath))[0])

    def _7z(self, fpath):
        dpath = self._get_dst(fpath)
        print(f'_7z() : ({fpath}), ({dpath})')
        self._mkdir(dpath)

        cmd = [r'C:\Program Files\7-Zip\7z.exe', 'x', fpath, '-aoa', '-o' + dpath]
        _7z = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in _7z.stdout.readlines():
            print(line)

        ret = _7z.wait()
        print('_7z() done : {ret}')
        if ret == 0:
            self._permission_recursive(dpath) 
        return dpath

    def _alzip(self, fpath):
        dpath = self._get_dst(fpath)
        print(f'_alzip() : ({fpath}), ({dpath})')

         # "" -x "\\mbann-linux\workspace2\CNSSStability\04696600\kernel panci_0706.egg" "\\mbann-linux\workspace2\CNSSStability\04696600\"
        cmd = [r'C:\Program Files (x86)\ESTsoft\ALZip\alzipcon.exe',  fpath, os.path.dirname(dpath)]
        _alzip = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in _alzip.stdout.readlines():
            print(line)

        ret = _alzip.wait()
        print('_alzip() done : {ret}')
        if ret == 0:
            self._permission_recursive(dpath) 
        return dpath

    def _tar(self, fpath):
        # In Windows, 7Z can replace. Let's test
        dpath = self._get_dst(fpath)
        print(f'_tar : ({fpath}), ({dpath}))')
        self._mkdir(dpath)

        #cmd = ['tar', 'xvzf', fpath, '-C', dpath, '--strip-components=1'] 
        cmd = ['tar', 'xvzf', fpath, '-C', dpath]
        _tar = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in _tar.stdout.readlines():
            print(line)

        ret = _tar.wait()
        if ret == 0:
            self._permission_recursive(dpath) 
        print(f"_tar() is done : {ret}")

        return dpath

    def _decompress(self, fpath):
        fext = os.path.splitext(fpath)[1]

        if fext in self._ext_7z:
            ret = self._7z(fpath)
        elif fext in self._ext_alzip:
            ret = self._alzip(fpath)
        else:
            raise Exception('Unexpected')

        self.insert_or_update_archeive(fpath)
        return ret

    def get_list(self, path_top):
        print(f'running from {path_top}')
        alist = []

        for _base, _dirs, _files in os.walk(path_top):
            for fpath in [os.path.join(_base, f) for f in _files]:
                if os.path.splitext(fpath)[1] in self._archive_list:
                    if self.is_candidate(fpath, os.path.getsize(fpath)):
                        alist.append(fpath)
                    else:
                        print('{fpath} is not a candidate')
        return alist

    def decompress_from_top(self):
        alist = self.get_list(self._top)

        for afile in alist:
            dsub = self._decompress(afile)
            if dsub != '':
                asublist = self.get_list(dsub)
                alist.extend(x for x in asublist if x not in alist)

        print('decompress_from_top() is done')
        print(alist)

    def UnitTest(self):
        self._top = r'C:\Temp'
        print(self.is_candidate(r'C:\Temp\abcde\2222.txt', 100))
        self.insert_or_update_archeive(r'C:\Temp\abcde\2222.txt')
        print(self.is_candidate(r'C:\Temp\abcde\2222.txt', os.path.getsize(r'C:\Temp\abcde\2222.txt')))
        self.decompress_from_top()


