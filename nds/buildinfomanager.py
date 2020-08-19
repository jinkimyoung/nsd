#!/usr/bin/env python3

import os
import re

import FileListManager

class BuildInfoManager():
    def __init__(self):
        self.BuildIDs = {}
        self.flm = FileListManager()

    def read_buildids(self, file_dst):
        self._reset_buildids()
        ftype = self.flm.get_ftype(file_dst)

        try:
            if ftype == 'FULLR':
                self.string_boot(file_dst)
                self.string_wlan(file_dst)
                self.string_mpss(file_dst)
                self.string_btfm(file_dst)
                self.string_tz(file_dst)
                self.string_apss(file_dst)
                self.string_aop(file_dst)
                self.is_dist_wlan()
            elif ftype in ['BTR']:
                self.string_btfm(file_dst)
            elif ftype in ['SSR', 'PDR']:
                self.string_wlan(file_dst)
                if self.is_dist_wlan():
                    self.string_mpss(file_dst)
            elif ftype in ['ELF_MPSS_ROOTPD']:
                self.string_mpss(file_dst)
            elif ftype in ['ELF_WLAN_FW_DIST', 'ELF_WLAN_FW_INT']:            
                self.string_wlan(file_dst)
                if ftype == 'ELF_WLAN_FW_INT' and self.string_mpss(file_dst) == False:
                    raise Exception('Unexpected')
            elif ftype == 'ELF_APSS':
                self.string_apss(file_dst)
            elif ftype == 'ELF_TZ':
                self.string_tz(file_dst)
            elif ftype == 'ELF_AOP':
                self.string_aop(file_dst)
        except Exception as e:
            print('[CRITICAL] '+str(e))
            raise Exception(str(e))

    ##################################################################
    def string_btfm(self, file_dst):
        self.BuildIDs['BTFM'] = {}

        sgroup = ['BTFM.CHE.*-QCACHROMZ-(.*)', 'BTFM.CHE.*-QCACHROM-(.*)', \
                    'BTFM.HST.*-QCACHROMZ-(.*)', 'BTFM.HST.*-QCACHROM-(.*)', \
                    'BTFM.HSP.*-QCAHSPROMZ-(.*)', 'BTFM.HST.*-QCAHSPROM-(.*)' ]

        v = None
        with open(file_dst) as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip('\r\n')
                v = None
                for skeyword in sgroup:
                    v = re.search(skeyword, line)
                    if v is None:
                        continue
                    else:
                        break

                if v is None:
                    # Find the next line
                    continue
                else:
                    version = v.groups()
                    print(f'string_btfm() : {version} : {line}')
                    self.BuildIDs['BTFM']['VERSION_STRING'] = v.group(0)
                    return True
        return False

    def string_tz(self, file_dst):
        self.BuildIDs['TZ'] = {}
        self.BuildIDs['TZ']['QC_IMAGE_VERSION_STRING'] = None
        self.BuildIDs['TZ']['QC_IMAGE_VARIANT_STRING'] = None
        
        # Need to check
        step = 0
        with open(file_dst) as f:
            lines = f.readlines()
            for line in lines:
                if step == 0:
                    v = re.search('QC_IMAGE_VERSION_STRING=TZ', line)
                    if v is None:
                        continue
                    else:
                        line = line.rstrip('\r\n')
                        version = line[v.start()+len('QC_IMAGE_VERSION_STRING='):]
                        print(f'string_tz() : TZ_QC_IMAGE_VERSION_STRING : {version}')
                        self.BuildIDs['TZ']['QC_IMAGE_VERSION_STRING'] = version
                        step = 1
                elif step == 1:
                    v = re.search('IMAGE_VARIANT_STRING=', line)
                    if v is None:
                        continue
                    else:
                        line = line.rstrip('\r\n')
                        version = line[v.start()+len('IMAGE_VARIANT_STRING='):]
                        print(f'string_tz() : TZ_IMAGE_VARIANT_STRING : {version}')
                        self.BuildIDs['TZ']['QC_IMAGE_VARIANT_STRING'] = version
                        return True

        return False

    def string_apss(self, file_dst):
        self.BuildIDs['AOP'] = {}
        self.BuildIDs['AOP']['QC_IMAGE_VERSION_STRING'] = None
        with open(file_dst) as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip('\r\n')
                v = re.search('^Linux version (\d{0,2}\.\d{0,2}\.\d{0,2})', line)
                if v is None:
                    continue
                else:
                    version = v.groups()
                    self.logger.info('string_apss() : {} : {}'.format(version, line))
                    self.BuildIDs['AOP']['QC_IMAGE_VERSION_STRING'] = line
                    return True
        return False

    def get_image_info_by_reserve(self, lines, keyword):
        print(f'get_image_info_by_reserve() : keyword({keyword})')

        info = { }
        info['QC_IMAGE_VERSION_STRING']     = None
        info['OEM_IMAGE_UUID_STRING']       = None

        state = 0
        count = 0 
        # for PDR mini case
        max_line    = 6

        for line in reversed(lines):
            line = line.rstrip('\r\n')

            if state == 0:
                # A. find QC_IMAGE_VERSION_STRING
                v = re.search(keyword, line)
                if v is not None:
                    # handle the exception 
                    if 'IMAGE_VARIANT_STRING' in line:
                        continue
                    info['QC_IMAGE_VERSION_STRING'] = line[v.start()+len('QC_IMAGE_VERSION_STRING='):]
                    info['QC_IMAGE_VERSION_STRING'] = info['QC_IMAGE_VERSION_STRING'].split()[0]
                    # validatte 
                    if re.search('(.*)-(.*)-(.*)-([0-9]$)', info['QC_IMAGE_VERSION_STRING']):
                        state = 1
                        count = 0
                    else:
                        info['QC_IMAGE_VERSION_STRING'] = None

            elif state == 1:
                if count >= max_line:
                    print(f'count({count}) : it is possible to get the wrong info, try from the beginning')
                    state = 0
                    count = 0
                    continue 
                else:
                    count = count + 1

                # B. find QC_IMAGE_VERSION_STRING
                v = re.search('OEM_IMAGE_UUID_STRING=', line)
                if v is not None:
                    info['OEM_IMAGE_UUID_STRING'] = line[v.start()+len('OEM_IMAGE_UUID_STRING='):]
                    info['OEM_IMAGE_UUID_STRING'] = info['OEM_IMAGE_UUID_STRING'].split()[0]
                    print('found')
                    return info
                else:
                    count = count + 1

        print('Failed to find the information')
        info['QC_IMAGE_VERSION_STRING']     = None
        info['OEM_IMAGE_UUID_STRING']       = None
        return info

    def get_image_info(self, lines, keyword):
        print(f'get_image_info() : keyword(keyword)')

        info = { }
        info['QC_IMAGE_VERSION_STRING'] = None
        info['OEM_IMAGE_UUID_STRING'] = None
        state = 0
        count = 0 
        max_line    = 10

        for line in lines:
            line = line.rstrip('\r\n')

            if state == 0:
                # A. find QC_IMAGE_VERSION_STRING
                v = re.search(keyword, line)
                if v is not None:
                    # handle the exception 
                    if 'IMAGE_VARIANT_STRING' in line:
                        continue
                    info['QC_IMAGE_VERSION_STRING'] = line[v.start()+len('QC_IMAGE_VERSION_STRING='):]
                    info['QC_IMAGE_VERSION_STRING'] = info['QC_IMAGE_VERSION_STRING'].split()[0]
                    state = 1
                    count = 0
            elif state == 1:
                # B. find QC_IMAGE_VERSION_STRING
                v = re.search('OEM_IMAGE_UUID_STRING=', line)
                if v is not None:
                    if count < max_line:
                        info['OEM_IMAGE_UUID_STRING'] = line[v.start()+len('OEM_IMAGE_UUID_STRING='):]
                        info['OEM_IMAGE_UUID_STRING'] = info['OEM_IMAGE_UUID_STRING'].split()[0]
                        return info
                    else:
                        print(f'count({count}) : it is possible to get the wrong info, try from the beginning')
                        state = 0
                else:
                    count = count + 1
                    if count >= max_line:
                        print(f'count({count}) : it is possible to get the wrong info, try from the beginning')
                        state = 0
                    else:
                        # for PDR mini case
                        v = re.search(keyword, line)
                        if v is not None:
                            # handle the exception 
                            if 'IMAGE_VARIANT_STRING' in line:
                                continue
                            info['QC_IMAGE_VERSION_STRING'] = line[v.start()+len('QC_IMAGE_VERSION_STRING='):]
                            info['QC_IMAGE_VERSION_STRING'] = info['QC_IMAGE_VERSION_STRING'].split()[0]
                            state = 1
                            count = 0

        print('Failed to find the information')
        return info

    def string_aop(self, file_dst):
        self.BuildIDs['AOP'] = {}
        self.BuildIDs['AOP']['QC_IMAGE_VERSION_STRING'] = None
        self.BuildIDs['AOP']['OEM_IMAGE_UUID_STRING'] = None

        skeywords = [ 'QC_IMAGE_VERSION_STRING=AOP' ]

        if self.flm.get_ftype(file_dst) == 'FULLR':
            dir_path = os.path.dirname(file_dst)
            dst_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and ('dataram' in f.lower() or 'aop_data' in f.lower()) ]
        else:
            dst_files = [ file_dst ]
        dst_files.sort()
     
        for dst_file in dst_files:
            with open(dst_file) as f:
                lines = f.readlines()

                for keyword in skeywords:
                    info = self.get_image_info(lines, keyword)
                    if info['QC_IMAGE_VERSION_STRING'] != None and info['OEM_IMAGE_UUID_STRING'] != None:
                        self.BuildIDs['AOP'] = info
                        return True

        return False

    def string_wlan(self, file_dst):
        self.BuildIDs['WLAN'] = {}
        self.BuildIDs['WLAN']['OEM_IMAGE_UUID_STRING'] = None
        self.BuildIDs['WLAN']['QC_IMAGE_VERSION_STRING'] = None

        skeywords = [ 'QC_IMAGE_VERSION_STRING=WLAN', 'QC_IMAGE_VERSION_STRING=CI_WLAN' ]

        if self.flm.get_ftype(file_dst) == 'FULLR':
            dir_path = os.path.dirname(file_dst)
            dst_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and ('ddrcs' in f.lower() or 'dram_cs' in f.lower()) ]
        else:
            dst_files = [ file_dst ]
        dst_files.sort()

        for dst_file in dst_files:
            with open(dst_file) as f:
                lines = f.readlines()

                for keyword in skeywords:
                    info = self.get_image_info_by_reserve(lines, keyword)
                    if info['QC_IMAGE_VERSION_STRING'] != None and info['OEM_IMAGE_UUID_STRING'] != None:
                        self.BuildIDs['WLAN'] = info
                        print(f'{info}')
                        return True

                for keyword in skeywords:
                    info = self.get_image_info(lines, keyword)
                    if info['QC_IMAGE_VERSION_STRING'] != None and info['OEM_IMAGE_UUID_STRING'] != None:
                        self.BuildIDs['WLAN'] = info
                        print(f'{info}')
                        return True

        return False

    def string_mpss(self, file_dst):
        self.BuildIDs['MPSS'] = {}
        self.BuildIDs['MPSS']['QC_IMAGE_VERSION_STRING'] = None
        self.BuildIDs['MPSS']['OEM_IMAGE_UUID_STRING'] = None

        skeywords = [ 'QC_IMAGE_VERSION_STRING=MPSS' ]

        if self.flm.get_ftype(file_dst) == 'FULLR':
            dir_path = os.path.dirname(file_dst)
            dst_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and ('ddrcs' in f.lower() or 'dram_cs' in f.lower()) ]
        else:
            dst_files = [ file_dst ]
        dst_files.sort()

        for dst_file in dst_files:
            with open(dst_file) as f:
                lines = f.readlines()

                for keyword in skeywords:
                    info = self.get_image_info_by_reserve(lines, keyword)
                    if info['QC_IMAGE_VERSION_STRING'] != None and info['OEM_IMAGE_UUID_STRING'] != None:
                        self.BuildIDs['MPSS'] = info
                        print(f'{info}')
                        return True

                for keyword in skeywords:
                    info = self.get_image_info(lines, keyword)
                    if info['QC_IMAGE_VERSION_STRING'] != None and info['OEM_IMAGE_UUID_STRING'] != None:
                        self.BuildIDs['MPSS'] = info
                        print(f'{info}')
                        return True

        return False

  def string_boot(self, file_dst):
        print('BuildInfo:string_boot()')
        self.BuildIDs['BOOT'] = {}
        self.BuildIDs['BOOT']['QC_IMAGE_VERSION_STRING'] = None
        self.BuildIDs['BOOT']['OEM_IMAGE_UUID_STRING'] = None

        with open(file_dst) as f:
            lines = f.readlines()

            info = self.get_image_info(lines, 'QC_IMAGE_VERSION_STRING=BOOT')
            if info['QC_IMAGE_VERSION_STRING'] != None and info['OEM_IMAGE_UUID_STRING'] != None:
                self.BuildIDs['BOOT'] = info
                return True

        return False

    def is_dist_wlan(self, str_input = None):
        keywords = [ 'HST', 'HSP' ] 

        if str_input == None:
            if self.BuildIDs.get('WLAN') == None:
                raise Exception('There is no QC_IMAGE_VERSION_STRING for WLAN')
            if self.BuildIDs['WLAN'].get('QC_IMAGE_VERSION_STRING') == None:
                raise Exception('There is no QC_IMAGE_VERSION_STRING for WLAN')
            str_input = self.BuildIDs['WLAN']['QC_IMAGE_VERSION_STRING']

        for keyword in keywords:
            if keyword in str_input:
                return True

        return False

    def is_dist_wlan2(self, file_dst):
        # Search in all DDR if  loading WLAN failed
        dir_path = os.path.dirname(file_dst)
        dst_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and ('ddrcs' in f.lower() or 'dram_cs' in f.lower()) ]

        dst_files.sort()
  
        for dst_file in dst_files:
            path_dst = os.path.join(dir_path, dst_file)
            if not os.path.exists(path_dst):
                continue

            with open(dst_file) as f:
                lines = f.readlines()
                for line in lines:
                    line = line.rstrip('\r\n')
                    if re.search('.*cnss_get_fw_files_for_target.*', line):
                        # For Ext - HST
                        return True
                    elif re.search('.*__icnss_register_driver.*', line):
                        # For Int - Hellium
                        return False
 
        return False

    def _reset_buildids(self):
		if hasattr(self, 'BuildIDs'):
            del(self.BuildIDs)
            self.BuildIDs = {}

    def get_buildids(self):
        return self.BuildIDs

