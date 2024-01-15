# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import re

from enum import IntEnum, unique
from typing import Any

from FTCodeDetectorModel import *
from FTCodeDetectorFileManager import FTCodeDetectorFileManager
from FTCodeDetectorConstDefine import FTCodeDetectorConst
from FTCodeDetectorModelStack import FTCodeDetectorModelStack

@unique
class FTCodeDetectorNFAState(IntEnum):
    STATE_INITIAL = 0,
    STATE_NORMAL_CODE = 1,
    STATE_COMMENT_BEGIN = 2,
    STATE_COMMENT_BEGIN_BEGIN = 3,
    STATE_COMMENT_BEGIN_CONTENT = 4,
    STATE_COMMENT_BEGIN_CLOSE = 5,
    STATE_COMMENT_NORMAL_CODE = 6,
    STATE_COMMENT_END_BEGIN = 7,
    STATE_COMMENT_END_END = 8,
    STATE_ACCEPT = 9,
    STATE_ERROR = 10

class FTCodeDetectorNFA():
    def __init__(self):
        self.state = FTCodeDetectorNFAState.STATE_INITIAL
        self.stack = FTCodeDetectorModelStack()

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == 'state':
            if __value == FTCodeDetectorNFAState.STATE_ERROR:
                raise Exception('COMMENT ERROR')
            
        return super().__setattr__(__name, __value)
    
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
    
    def add_line_if_state_correct(self, line: (int, str)):
        if self.stack.empty():
            self.state = FTCodeDetectorNFAState.STATE_ERROR
            return

        self.stack.top.source_lines.append(line)

    def match(self, file: str) -> [FTCodeDetectorModel]:
        regex = re.compile(r'^<([_a-zA-Z0-9]+)(?:\s+(.+))*>\s*(.*)')
        lines = FTCodeDetectorFileManager.read_file_lines(file)
        models: [FTCodeDetectorModel] = []

        for (line, content) in enumerate(lines):
            if content == None or len(content.strip()) <= 0:
                continue

            if content.strip() == FTCodeDetectorConst.COMMENT_BEGIN:
                if self.state == FTCodeDetectorNFAState.STATE_INITIAL:
                    self.state = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN

                    model: FTCodeDetectorModel = FTCodeDetectorModel()
                    model.start_line = line + 1
                    model.abs_path = file
                    model.source_file = FTCodeDetectorFileManager.get_file_name(file)
                    model.source_lines.append((line + 1, content))
                
                    self.stack.push(model)
                
                elif self.state == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
                    self.state = FTCodeDetectorNFAState.STATE_COMMENT_END_BEGIN

                    self.add_line_if_state_correct((line + 1, content))

            elif content.strip() == FTCodeDetectorConst.COMMENT_END:
                if self.state == FTCodeDetectorNFAState.STATE_COMMENT_END_END:
                    self.state = FTCodeDetectorNFAState.STATE_ACCEPT
                    
                    self.add_line_if_state_correct((line + 1, content))
                    self.stack.top.end_line = line + 1

                    models.append(self.stack.top)
                    self.stack.pop()
                
                elif self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CONTENT or self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_BEGIN:
                    self.state = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CLOSE

                    self.add_line_if_state_correct((line + 1, content))

                elif self.state == FTCodeDetectorNFAState.STATE_INITIAL:
                    self.stack.pop()

            elif content.strip() == FTCodeDetectorConst.START_MARCO:
                if self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN:
                    self.state = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_BEGIN
                    self.add_line_if_state_correct((line + 1, content))

            elif content.strip() == FTCodeDetectorConst.END_MARCO:
                if self.state == FTCodeDetectorNFAState.STATE_COMMENT_END_BEGIN:
                    self.state = FTCodeDetectorNFAState.STATE_COMMENT_END_END
                    self.add_line_if_state_correct((line + 1, content))

                elif self.state == FTCodeDetectorNFAState.STATE_NORMAL_CODE:
                    self.state = FTCodeDetectorNFAState.STATE_INITIAL

            else:

                if self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_BEGIN or self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CONTENT:
                    self.state = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CONTENT

                    matchs = regex.match(content.strip())
                    groups = matchs.groups() if matchs != None else None

                    if groups == None:
                        self.state = FTCodeDetectorNFAState.STATE_ERROR
                        return None

                    self.add_line_if_state_correct((line + 1, content))

                    marco: FTCodeDetectorMarco = self.add_marco(groups)

                    if groups[0] == FTCodeDetectorConst.BUSINESS_MARCO:
                        marco.update_type(FTCodeDetectorConst.FEILD_TYPE_SINGLE)    
                        self.stack.top.business_marco = marco
                        continue
                    
                    elif groups[0] == FTCodeDetectorConst.PRINCIPAL_MARCO:
                        marco.update_type(FTCodeDetectorConst.FIELD_TYPE_PERSON)
                        self.stack.top.principal_marco = marco
                        continue

                    self.stack.top.user_defined.append(marco)

                else:

                    if self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CLOSE or \
                            self.state == FTCodeDetectorNFAState.STATE_COMMENT_END_BEGIN or \
                                self.state == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
                        
                        self.add_line_if_state_correct((line + 1, content))
                        self.stack.top.text_lines.append(content)

                        self.state = FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE

                    else:

                        if self.state == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN or self.state == FTCodeDetectorNFAState.STATE_NORMAL_CODE:
                            self.state = FTCodeDetectorNFAState.STATE_NORMAL_CODE
                        else:
                            self.state = FTCodeDetectorNFAState.STATE_INITIAL

                        self.stack.pop()

        if self.state == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
            self.state = FTCodeDetectorNFAState.STATE_ACCEPT
            
            self.add_line_if_state_correct((len(lines), lines[-1]))
            self.stack.top.end_line = len(lines)

            models.append(self.stack.top)
            self.stack.pop()
        
        return models
