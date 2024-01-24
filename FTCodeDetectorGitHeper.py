# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import os
import subprocess

from FTCodeDetectorFileManager import FTCodeDetectorFileManager

class FTCodeDetectorGitHelper():

    @staticmethod
    def __get_repo_name(url: str) -> str:
        basename = os.path.basename(url)

        if basename.endswith('.git'):
            return basename[0 : len(basename) - len('.git')]
        
        return basename

    @staticmethod
    def git_version() -> str:
        git_version = subprocess.Popen(['git', '--version'], shell = False, stdout = subprocess.PIPE) \
            .stdout.readline().decode('utf-8') \
                .strip()
        return git_version

    @staticmethod
    def get_file_url(path: str) -> str:
        file_url: str = None
        if path == None or len(path) <= 0 \
            or os.path.exists(path) == False:
            return file_url
        
        cur_dir = os.getcwd()
        os.chdir(FTCodeDetectorFileManager.get_file_path(path))
        
        file_url = subprocess.Popen(['git', 'remote', 'get-url', 'origin', '--push'], shell = False, stdout = subprocess.PIPE) \
            .stdout.readline().decode('utf-8') \
                .strip()
        
        repo = FTCodeDetectorGitHelper.__get_repo_name(file_url)

        if file_url == None or len(file_url) <= 0:
            os.chdir(cur_dir)
            return None

        if file_url.startswith('https://') == False:
            file_url = file_url.replace(r':', r'/').replace(r'git@', r'https://')

        file_url = file_url.replace(r'.git', r'/blob')

        curr_branch = subprocess.Popen(['git', 'branch', '--show-current'], shell=False, stdout = subprocess.PIPE) \
            .stdout.readline().decode('utf-8') \
                .strip()
        if curr_branch == None or len(curr_branch) <= 0:
            os.chdir(cur_dir)
            return None
        
        file_url = file_url + '/{0}'.format((curr_branch))

        repo_index: int = path.find(repo)
        if repo_index == -1:
            os.chdir(cur_dir)
            return None
        
        file_url = file_url + path[repo_index + len(repo) : len(path)]
        
        os.chdir(cur_dir)
        return file_url