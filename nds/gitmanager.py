#!/usr/bin/env python3
# pip install pyyaml gitpython

import os
import yaml
from git import Repo

class GitManager():
    def __init__(self, dir_dsttop=None):
        self._top =  os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        self._yml = os.path.join(self._top, 'configure', 'external_gits.yml')
        self._dir_dsttop = dir_dsttop
        if not os.path.exists(self._yml) or not os.path.exists(self._dir_dsttop):
            raise Exception(f'{self._yml} or {self._dir_dsttop} is not present')
        print(self._yml)

    def _get_gits(self):
        # Read from YML and Get GIT List
        try:
            with open(self._yml, "r") as ymlfile:
                _cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

            gitlist = [ _cfg[section]['git'] for section in _cfg if 'git' in _cfg[section].keys() ]
            print(gitlist)
            return gitlist
        except Exception as ERR:
            print('[CRITICAL]In _get_gits() : '+str(ERR))

    def update_latests(self, gitlist):
        for url_git in gitlist:
            self.git_clone_or_pull(url_git)
        
        pass

    def git_clone_or_pull(self, url_git):
        basename = url_git[url_git.rfind(r'/')+1:url_git.rfind(r'.')]
        dir_dst = os.path.join(self._dir_dsttop, basename)
        print(f'git_clone_or_pull({url_git}, {dir_dst})')

        try:
            if not os.path.exists(dir_dst):
                repo = Repo.clone_from(url_git, dir_dst, recursive=True)
                print('repo clone is done')
            else:
                repo = Repo(dir_dst)
                o = repo.remotes.origin
                o.pull()
                print('repo pull is done')
        except Exception as ERR:
            print('[CRITICAL]In git_clone_or_pull() : '+str(ERR))

    def TestUnit(self):
        glist = self._get_gits()
        self.update_latests(glist)
        pass
        
g = GitManager(r'c:\temp')
g.TestUnit()