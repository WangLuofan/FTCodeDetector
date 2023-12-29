# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import os
import re
import threading

from FTCodeDetectorConstDefine import *

from FTCodeDetectorModel import *
from FTCodeDetectorFileManager import FTCodeDetectorFileManager
from FTCodeDetectorModelStack import FTCodeDetectorModelStack

class FTCodeDetectorScanOperation(threading.Thread):
    def __init__(self, files: [str], thread_lock: threading.Lock, result: [FTCodeDetectorModel]):
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
                            if stack.top().business_marco == None:
                                stack.top().business_marco = self.add_marco((FTCodeDetectorConst.BUSINESS_MARCO, None, FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN), FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN_DESC)

                            model_list.append(stack.top())

                            stack.pop()
                            continue
                    state = False
                    continue

                groups = matchs.groups()
                if groups[0] == FTCodeDetectorConst.START_MARCO:
                    if l == 0 or (lines[l - 1].strip()) != FTCodeDetectorConst.COMMENT_BEGIN:
                        continue

                    state = True

                    model = FTCodeDetectorModel()
                    model.start_line = l - 1
                    model.source_lines.append((l - 1, lines[l - 1]))
                    model.source_lines.append((l, lines[l]))
                    model.source_file = FTCodeDetectorFileManager.get_file_name(f)

                    stack.push(model)

                elif groups[0] == FTCodeDetectorConst.END_MARCO:
                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))
                        model_list.append(stack.top())

                        if l + 1 < len(lines) and lines[l + 1].strip() == FTCodeDetectorConst.COMMENT_END:
                            comment_end_line = lines[l + 1]
                            stack.top().end_line = l + 1
                            stack.top().source_lines.append((l + 1, comment_end_line))

                        if stack.top().business_marco == None:
                            stack.top().business_marco = self.add_marco((FTCodeDetectorConst.BUSINESS_MARCO, None, FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN), FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN_DESC)
                        
                        stack.pop()
                        state = False

                elif groups[0] == FTCodeDetectorConst.BUSINESS_MARCO:
                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))

                        marco: FTCodeDetectorMarco = self.add_marco(groups)
                        marco.update_type(FTCodeDetectorConst.FEILD_TYPE_SINGLE)
                        
                        model.business_marco = marco

                else:
                    if stack.empty() == False:
                        stack.top().source_lines.append((l, lines[l]))
                        marco = self.add_marco(groups)
                        model.user_defined.append(marco)

            if len(model_list) > 0:
                self.thread_lock.acquire(True)
                self.result.extend(model_list)
                self.thread_lock.release()

    def __read_file_contents(self, file: str):
        if not os.path.exists(file):
            return ''
        
        contents = ''
        with open(file, encoding='utf-8') as f:
            contents = f.readlines()

        return contents