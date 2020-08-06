#!/usr/bin/env python3

import os
import re
import sqlite3
import subprocess

class FileListManager:
	def __init__(self, dsrc):
		self._dsrc = dsrc if os.path.exists(dsrc) else None

		if self._dsrc is None:
			raise Exception(f'Path is wrong - dsrc({dsrc})')

		# DB
		self._db = os.path.join(self._dsrc, 'FileListManager.db')
		self._connect()

		##  extentions of files
		self.subtechs	= ( 'GPS' , 'BT' , 'WLAN' )
		self.set_image	= ( '.jpg', '.png', '.wmv' )
		self.set_code	= ( '.patch', '.java', '.c', '.cpp', '.mk', '.h', '.py' )
		self.set_etc	= ( '.pptx', '.xlsx', '.csv', '.html', '.txt', '.pdf', '.dmc', '.exe', '.bat', '.log', '.xqcn', '.ini', '.xls', '.apk', '.cfg', '.gitignore', '.md' )
		self.set_skip = set(self.set_image + self.set_code + self.set_etc)

		# NEED to pair in categorize()
		self.set_elf	= ( 'ELF_APSS', 'ELF_WLAN_FW', 'ELF_WLAN_HOST', 'ELF_MPSS_ROOTPD', 'ELF_MPSS_ELFLOADER', 'ELF_MPSS_CORE', 'ELF_AOP' )
		self.set_dump	= ('SSR', 'FULLR', 'PDR', 'BTR')
		self.set_qxdm	= ('ISF')
		self.set_tomb	= ('BUGREPORT', 'TOMBSTONE')

		self._list_elf	= []
		self._list_dump	= []
		self._list_qxdm = []
		self._list_tomb = []

	def __del__(self):
		self._disconnect()

	def _reset_flist(self):
		self._list_elf	= []
		self._list_dump	= []
		self._list_qxdm = []
		self._list_tomb = []

	def get_ftype(self, fname):
		type = 'OTHER'

		if re.match(r'.*\.isf$', fname): #isf
			type = 'ISF'
		elif re.match(r'ramdump.*\.elf$', fname):
			if re.match(r'.*memshare.*', fname):
				type = 'OTHER'
			elif re.match(r'.*rtel.*', fname):
				type = 'OTHER'
			elif re.match(r'.*smem.*', fname):
				type = 'OTHER'
			elif re.match(r'.*msa.*', fname):
				type = 'OTHER'
			else:
				type = 'SSR'
		elif re.match(r'ramdump_modem.*', fname):
			type = 'SSR'
		elif re.match(r'.*vmlinux.*', fname):
			type = 'ELF_APSS'
		elif re.match(r'WLAN_MERGED.*\.elf', fname):
			type = 'ELF_WLAN_FW'
		elif re.match(r'qca_cld3_wlan\.ko.*\.unstripped', fname):
			type = 'ELF_WLAN_HOST'
		elif re.match(r'orig_MODEM_PROC_IMG_.*\.prodQ.*\.elf', fname):
			type = 'ELF_MPSS_ROOTPD'
		elif re.match(r'.*ELF_LOADER.*\.elf', fname):
			type = 'ELF_MPSS_ELFLOADER'
		elif re.match(r'ELF_LOADER_IMG_.*\.prodQ\.elf', fname):
			type = 'ELF_MPSS_ELFLOADER'
		elif re.match(r'CORE_USER.*\.so', fname):
			type = 'ELF_MPSS_CORE'
		elif re.match(r'EBICS0\.BIN', fname):
			type = 'FULLR'
		elif re.match(r'DDRCS0\.BIN', fname):
			type = 'FULLR'
		elif re.match(r'DDRCS0_0\.BIN', fname):
			type = 'FULLR'
		elif re.match(r'dram_cs0_.*', fname):   # Samsung
			type = 'FULLR'
		elif re.match(r'.*\.qsr4', fname):
			type = 'HASH'
		elif re.match(r'.*bt_fw_crashdump.*\.bin', fname):
			type = 'BTR'
		elif re.match(r'pd_dump_wlan_process.*\.elf', fname):
			type = 'PDR'
		elif re.match(r'bugreport.*', fname):
			type = 'BUGREPORT'
		elif re.match(r'tombstone.*', fname):
			type = 'TOMBSTONE'
		elif re.match(r'hyp.*\.elf', fname):
			type = 'ELF_TZ_HYP'
		elif re.match(r'qsee.*\.elf', fname):
			type = 'ELF_TZ_QSEE'
		elif re.match(r'AOP.*\.elf', fname):
			type = 'ELF_AOP'
		return type

	def _check_subtech(self, subtech):
		if subtech not in self.subtechs:
			raise Exception(f'subtech is not supported : ({subtech})')

	def determinte_files_to_analyze(self):
		self._reset_flist()

		for bases, dirs, files in os.walk(self._dsrc):
			for f in files:
				fpath = os.path.abspath(os.path.join(bases, f))
				fext = os.path.splitext(f)[1]
				if fext in self.set_skip:
					print(f'skip : {fpath}')
					continue
    
				ftype = self.get_ftype(f)
				print(f'{ftype} : {f}')

				if ftype in self.set_elf:
					self._list_elf.append(fpath)
				elif ftype in self.set_dump:
					self._list_dump.append(fpath)
				elif ftype in self.set_qxdm:
					self._list_qxdm.append(fpath)
				elif ftype in self.set_tomb:
					self._list_tomb.append(fpath)
				else:
					print(f'{fpath} is not cagetorized')
		return 

	def get_elfs(self):
		return self._list_elf

	def get_dumps(self):
		return self._list_dump

	def get_qxdms(self):
		return self._list_qxdm
		
	def get_tombs(self):
		return self._list_tomb

	def _connect(self):
		self._conn = sqlite3.connect(self._db)
		self._cursor = self._conn.cursor()
		self._create_syncdb()

	def _disconnect(self):
		if hasattr(self, '_conn') and self._conn != None:
			self._conn.close()
			del(self._conn)

	def _create_syncdb(self):
		self._cursor.execute('CREATE TABLE IF NOT EXISTS flist(path text UNIQUE, size int)')

	def TestCase(self):
		top = r'C:\Temp\nsd'
		category = os.path.join(top, 'category')
		if not os.path.exists(category):
			os.mkdir(category)

		dlist = [ '123', 'abc' ]
		flist = [ 'ramdump.elf', '1.2.elf', 'abcd.isf', 'elf.abc']
		for d1 in dlist:
			subd1 = os.path.join(category, d1)
			if not os.path.exists(subd1):
				os.mkdir(subd1)

			for f1 in flist:
				subf1 = os.path.join(subd1, f1)
				if not os.path.exists(subf1):
					with open(subf1, 'w') as fsub:
						pass

		self.__init__(top)
		self.determinte_files_to_analyze()


f = FileListManager(r'C:\Temp\nsd')
f.TestCase()
