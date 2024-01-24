# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import os

class FTCodeDetectorFileManager():
    def __init__(self, path: str, extensions: [str]):
        self.path = path
        self.extensions = extensions

    def get_file_extension(self, path: str):
        comps = os.path.splitext(path)
        return comps[-1]

    @staticmethod
    def get_file_name(path: str):
        return os.path.basename(path)

    @staticmethod
    def get_file_path(path: str):
        base_name: str = FTCodeDetectorFileManager.get_file_name(path)
        
        if base_name == None or len(base_name) <= 0:
            return None
        
        return path[0:len(path) - len(base_name)]

    def is_valid_file(self, path: str):
        ext = self.get_file_extension(path)

        if len(ext) <= 0:
            return False
        
        for e in self.extensions:
            if e == ext:
                return True

        return False

    def get_source_files(self):
        path = os.getcwd()

        source_files = self.__get_source_files(self.path)
        
        os.chdir(path)

        return source_files
    
    def __get_source_files(self, path: str):
        os.chdir(path)

        path = os.path.expanduser(path)

        dir = os.listdir(path)

        source_files = []
        if len(dir) > 0:
            for d in dir:
                if d.startswith('.') or os.path.islink(d):
                    continue

                abs_path = os.path.abspath(d)

                if os.path.isdir(abs_path):
                    source_files.extend(self.__get_source_files(abs_path))
                elif os.path.isfile(abs_path):
                    if self.is_valid_file(abs_path):
                        source_files.append(abs_path)
        
        os.chdir('..')
        return source_files

    @staticmethod
    def read_file_lines(file: str):
        if not os.path.exists(file):
            return ''
        
        contents: [str] = []
        with open(file, encoding='utf-8') as f:
            contents = f.readlines()

        return contents