#!/usr/bin/env python3

import os
import Configs
import ExtractFile
import BuildInfoManager

class DSTN():
    def __init__(self):
        self.dir_dst = None
        self.configs = Configs()

        self.list_elf   = None
        self.list_dump  = None
        self.list_qxdm  = None
        self.list_tomb  = None
        self.dic_buildids = {}

    def __del__(self):
        del(self.list_elf)
        del(self.list_dump)
        del(self.list_qxdm)
        del(self.list_tomb)

    #############################################
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

    def _sync(self):
        retval = os.system('sync')
        retval = os.system('sync')
        return

    def _local_to_networkdrive(self, src):
        print(f'before : [{src}]')
        src.replace(self.top_local, self.nwd_local, 1)
        print(f'after : [{src}]')
        return src

    #############################################
    def set_workdir(self, dir_dst):
        if os.path.exists(dir_dst):
            raise Exception(f'{dir_dst} is not present')

        self.dir_dst = os.path.abspath(dir_dst)

    #############################################
    def _extracts(self):
        ef = ExtractFile(self.dir_dst)
        ef.decompress_from_top()

    def _get_file_lists(self):
        flm = FileListManager(self.dir_dst)
		flm.determinte_files_to_analyze()
        flm.shuffle_ramdumps()

        self.list_elf   = flm.get_elfs()
        self.list_dump  = flm.get_dumps()
        self.list_qxdm  = flm.get_qxdms()
        self.list_tomb  = flm.get_tombs()

    def _get_buildids(self):
        bim = BuildInfoManager()

        files = set(self.list_elf + self.list_dump)
        for dst in files:
            bim.find_buildid(dst)
            buildids = bim.get_buildids()
            self.dic_buildids[dst] = buildids

        print(self.dic_buildids)
        return 

    def _merged_big_small(self):
        keys = [ ['.big', '.small'], ['.BIG', '.SMALL']]
        rlist = self.list_dump
        for rfile in rlist:
            dir_upper = os.path.dirname(rfile)
            name_upper = os.path.basename(dir_upper)

            for key in keys:
                name_match = name_upper.replace(key[0], key[1])
                dir_match = os.path.join(os.path.dirname(dir_upper), name_match)
                print(f'{dir_upper} : {dir_match}')
                
                if name_upper != name_match and os.path.exists(dir_match):
                    files = [ os.path.join(dir_match, f) for f in os.listdir(dir_match) if os.path.isfile(os.path.join(dir_match, f)) ]
                    print(files)
                    for f in files:
                        shutil.move(f, dir_upper)

        return

    def _rename_ssr_for_crashscope(self):
        for file_apath in self.list_dump:
            finfo = os.path.split(file_apath)
            fdir = finfo[0]
            fname = finfo[1]

            s = re.search(r'ramdump_wlan(.*)', fname)
            if s is None:
                continue

            buildsid = self.dic_buildids[file_apath]
            if buildsid.get('WLAN') == None
                raise Exception('BUILDIDs[WLAN] is emptry. Enexpected')

            qc_image_version = self.BuildIDs['WLAN']['QC_IMAGE_VERSION_STRING'] 
            if 'WLAN.HL' in qc_image_version:
                dst_fname = 'pd_dump_wlan_process' + s.group(1)
                dst_apath = os.path.join(fdir, dst_fname)
                os.rename(file_apath, dst_apath)

                del self.dic_buildids[file_apath]
                self.dic_buildids[dst_apath] = buildsid
            elif 'HST' in qc_image_version or 'HSP' in qc_image_version:
                pass
                #split_ssr = SplitHSTSSR(self.logger, file_apath)
                #split_ssr.read_segments()
                #split_ssr.split_segments()
                #split_ssr.extract_from_rddm()
        return

    def _when_ramdump_direcotry_has_matching_chipsetid_name_subdir(self):
        # http://qwiki.qualcomm.com/public/Crashscope/faq.html#Crashscope_can_not_parse_ramdump_when_ramdump_.26_ELF_directories_are_in_the_same_folder 

        chipsets = [ 'sdx55m', 'sm8250', 'sm8350' ] 
        redo_traverse = False

        rlist = self.list_dump
        for rfile in rlist:
            dir_cur = os.path.dirname(rfile)
            dir_subs = [ d for d in os.listdir(dir_cur) if os.path.isdir(os.path.join(dir_cur, d)) ]
            print(f'{dir_cur}, {dir_subs}')

            for dir_name in dir_subs:
                for chipset in chipsets:
                    if dir_name.startswith(chipset):
                        dir_new = 'elf_' + dir_name
                        print(f'rename from {dir_name} to {dir_new}')

                        dir_old = os.path.join(dir_cur, dir_name)
                        dir_rename = os.path.join(dir_cur, dir_new)
                        os.rename(dir_old, dir_rename)

                        for file_elf in self.list_elf:
                            if file_elf.startswith(dir_old):
                                prev = file_elf
                                new = file_elf.replace(dir_old, dir_rename, 1)
                                print(f'{prev} moves to {new}')
                                self.list_elf.remove(prev)
                                self.list_elf.append(new)
 
    def _wa_for_crashscope(self):
        # A. RENAME from ramdump_wlan to pd_dump_wlan_process for CrashScope
        self._rename_ssr_for_crashscope()
        self._when_ramdump_direcotry_has_matching_chipsetid_name_subdir()

    def pre_processing(self):
        # 1. extract_files and add new files to lists 
        self._extracts()
        # 2. get ramdumps & elfs list
        self._get_file_lists()

        # 3. UNICODE Handling
        # wsc2? later

        # 4. Get BUILD STRING
        self._get_buildids()

        # 5. merged_big_small()
        self._merged_big_small()

        # 6. WA for Crashscope
        self._wa_for_crashscope()

        # 7. MINIDUMP

        # 8. pre-processing for  MICROSOFT 
        # later

    #############################################
    def main_processing(self):
        try:
            # Analyze RAMDUMP
            self.run_ramdump_analysis()
        except Exception as e:
            print('[CRITICAL] '+str(e))

        try:
            self.run_gps_analysis()
        except Exception as e:
            self.logger.critical(str(e))
            print('[CRITICAL] '+str(e))
        return

    def run_gps_analysis(self):
        list_qxdm_dir = self._get_qxdm_dirlist()

        # Merge

        # Filter

        # mail

        return         
        
         

    def _get_qxdm_dirlist(self):
        list_directory = []
        list_qxdm = self.list_qxdm 

        for file_qxdm in list_qxdm:
            dir_high = os.path.dirname(file_qxdm)
            if dir_high not in list_directory:
                list_directory.append(dir_high)

        return list_directory 




