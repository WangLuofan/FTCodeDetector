# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import os
import re
import threading

from FTCodeDetectorModel import *
from FTCodeDetectorFileManager import FTCodeDetectorFileManager
from FTCodeDetectorModelStack import FTCodeDetectorModelStack

comment_begin = r'/**'
start_marco = r'FT_FINANCIAL_CODE_MARK_BEGIN'
business_marco = r'business'
end_marco = r'FT_FINANCIAL_CODE_MARK_END'
comment_end = r'*/'

class FTCodeDetectorScanOperation(threading.Thread):
    def __init__(self, files: [str], thread_lock: threading.Lock, result: dict):
        threading.Thread.__init__(self)
        self.result = result
        self.files = files
        self.thread_lock = thread_lock

    def add_marco(self, groups: tuple, desc: str = None) -> FTCodeDetectorMarco:
        if len(groups) <= 0:
            return None
        
        marco = FTCodeDetectorMarco(groups[0])
        if groups[1] != None and len(groups[1]) > 2:
            marco.parse_attributes(groups[1])
        marco.value = groups[2]

        if desc != None and len(desc) > 0:
            marco.update_desc(desc)

        return marco

    def run(self):
        regex = re.compile(r'^<([_a-zA-Z0-9]+)(?:\s+(.+))*>\s*(\S*)')
        for f in self.files:
            lines = self.__read_file_contents(f)

            stack = FTCodeDetectorModelStack()
            
            model_list = []

            state: bool = False
            for l in range(0, len(lines)):
                contents = lines[l].strip()
                matchs = regex.match(contents)

                if matchs == None:
                    if state == False:
                        continue

                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))
                        if l == len(lines) - 1:
                            while stack.size() != 1:
                                stack.pop()

                            stack.top().end_line = l + 1
                            model_list.append(stack.top())

                            stack.pop()
                            continue
                    state = False
                    continue

                groups = matchs.groups()
                if groups[0] == start_marco:
                    if l == 0 or (lines[l - 1].strip()) != comment_begin:
                        continue

                    state = True

                    model = FTCodeDetectorModel()
                    model.start_line = l - 1
                    model.source_lines.append((l - 1, lines[l - 1]))
                    model.source_lines.append((l, lines[l]))
                    model.source_file = FTCodeDetectorFileManager.get_file_name(f)

                    stack.push(model)

                elif groups[0] == end_marco:
                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))
                        model_list.append(stack.top())

                        if l + 1 < len(lines) and lines[l + 1].strip() == comment_end:
                            comment_end_line = lines[l + 1]
                            stack.top().end_line = l + 1
                            stack.top().source_lines.append((l + 1, comment_end_line))
                        
                        stack.pop()
                        state = False

                elif groups[0] == business_marco:
                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))
                        model.business = groups[2]
                        model.user_defined.append(self.add_marco(groups))

                else:
                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))
                        marco = self.add_marco(groups)
                        model.user_defined.append(marco)

            self.category(model_list)

    def category(self, models: [FTCodeDetectorModel]):
        if models == None or len(models) <= 0:
            return

        model_dict: dict = {}
        for model in models:
            if model.business not in model_dict:
                model_dict[model.business] = []
            model_dict[model.business].append(model)

        self.thread_lock.acquire(True)

        for (business, models) in model_dict.items():
            if business not in self.result:
                self.result[business] = models
            else:
                self.result[business].append(models.extend())

        self.thread_lock.release()

    def __read_file_contents(self, file: str):
        if not os.path.exists(file):
            return ''
        
        contents = ''
        with open(file, encoding='utf-8') as f:
            contents = f.readlines()

        return contents