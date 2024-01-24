# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import re

from enum import IntEnum, unique
from typing import Any

from FTCodeDetectorModel import *
from FTCodeDetectorFileManager import FTCodeDetectorFileManager
from FTCodeDetectorConstDefine import FTCodeDetectorConst
from FTCodeDetectorStack import FTCodeDetectorStack

@unique
class FTCodeDetectorNFAState(IntEnum):
    STATE_INITIAL = 0,
    STATE_NORMAL_CODE = 1,
    STATE_COMMENT_BEGIN = 2,
    STATE_COMMENT_BEGIN_BEGIN = 3,
    STATE_COMMENT_BEGIN_CONTENT = 4,
    STATE_COMMENT_BEGIN_END = 5,
    STATE_COMMENT_NORMAL_CODE = 6,
    STATE_COMMENT_END_END = 8,
    STATE_ACCEPT = 9,
    STATE_ERROR = 10

class FTCodeDetectorNFA():
    def __init__(self):
        self.stateStack: FTCodeDetectorStack = FTCodeDetectorStack()

        self.modelStack: FTCodeDetectorStack = FTCodeDetectorStack()

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
    
    def add_line_if_needed(self, line: (int, str)):
        if self.modelStack.empty or line == None:
            return

        self.modelStack.top.source_lines.append(line)

    def match(self, file: str) -> [FTCodeDetectorModel]:
        regex = re.compile(r'^<([_a-zA-Z0-9]+)(?:\s+(.+))*>\s*(.*)')
        lines = FTCodeDetectorFileManager.read_file_lines(file)
        models: [FTCodeDetectorModel] = []

        for (line, content) in enumerate(lines):
            if content == None or len(content.strip()) <= 0:
                continue

            if content.strip() == FTCodeDetectorConst.COMMENT_BEGIN:
                self.stateStack.push(FTCodeDetectorNFAState.STATE_COMMENT_BEGIN)

            elif content.strip() == FTCodeDetectorConst.COMMENT_END:
                if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_END_END:
                    self.stateStack.top = FTCodeDetectorNFAState.STATE_ACCEPT
                    
                    self.add_line_if_needed((line + 1, content))
                    self.modelStack.top.end_line = line + 1

                    topModel = self.modelStack.top
                    models.append(topModel)

                    self.modelStack.pop()
                    self.modelStack.top.source_lines.extend(topModel.source_lines) if self.modelStack.empty == False else None

                    self.stateStack.pop()
                
                elif self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CONTENT or self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_BEGIN:
                    self.stateStack.top = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_END

                    self.add_line_if_needed((line + 1, content))

                elif self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
                    self.add_line_if_needed((line + 1, content))

                elif self.stateStack.top == FTCodeDetectorNFAState.STATE_INITIAL:
                    self.modelStack.pop()

            elif content.strip() == FTCodeDetectorConst.START_MARCO:
                if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN:
                    self.stateStack.top = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_BEGIN

                    model: FTCodeDetectorModel = FTCodeDetectorModel()
                    model.start_line = line
                    model.abs_path = file
                    model.source_file = FTCodeDetectorFileManager.get_file_name(file)
                
                    self.modelStack.push(model)

                    prevLine = lines[line - 1] if (line - 1) < len(lines) else None
                    
                    self.add_line_if_needed((line, prevLine))
                    self.add_line_if_needed((line + 1, content))

            elif content.strip() == FTCodeDetectorConst.END_MARCO:
                self.stateStack.pop()

                if self.stateStack.top == FTCodeDetectorNFAState.STATE_NORMAL_CODE:
                    self.stateStack.top = FTCodeDetectorNFAState.STATE_INITIAL
                
                else:
                    self.stateStack.top = FTCodeDetectorNFAState.STATE_COMMENT_END_END
                    self.add_line_if_needed((line + 1, content))

            else:

                if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_BEGIN or self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CONTENT:
                    self.stateStack.top = FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_CONTENT

                    matchs = regex.match(content.strip())
                    groups = matchs.groups() if matchs != None else None

                    if groups == None:
                        self.stateStack.top = FTCodeDetectorNFAState.STATE_ERROR
                        return None

                    self.add_line_if_needed((line + 1, content))


                    if groups[0] == FTCodeDetectorConst.BUSINESS_MARCO:
                        marco: FTCodeDetectorMarco = self.add_marco(groups, groups[2])
                        marco.update_type(FTCodeDetectorConst.FEILD_TYPE_SINGLE)    
                        self.modelStack.top.business_marco = marco
                        continue
                    
                    elif groups[0] == FTCodeDetectorConst.PRINCIPAL_MARCO:
                        marco: FTCodeDetectorMarco = self.add_marco(groups)
                        marco.update_type(FTCodeDetectorConst.FIELD_TYPE_PERSON)
                        self.modelStack.top.principal_marco = marco
                        continue

                    marco: FTCodeDetectorMarco = self.add_marco(groups)
                    self.modelStack.top.user_defined.append(marco)

                else:

                    if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN_END or \
                                self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
                        
                        self.add_line_if_needed((line + 1, content))
                        self.stateStack.top = FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE

                    else:

                        if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN or self.stateStack.top == FTCodeDetectorNFAState.STATE_NORMAL_CODE:
                            if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_BEGIN:
                                prevLine = lines[line - 1] if (line - 1) < len(lines) else None
                                self.add_line_if_needed((line, prevLine))

                            self.stateStack.pop()
                            self.add_line_if_needed((line + 1, content))

                        elif self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
                            self.add_line_if_needed((line + 1, content))

                        else:
                            if self.stateStack.empty == False:
                                self.stateStack.top = FTCodeDetectorNFAState.STATE_INITIAL

        if self.stateStack.top == FTCodeDetectorNFAState.STATE_COMMENT_NORMAL_CODE:
            self.stateStack.top = FTCodeDetectorNFAState.STATE_ACCEPT
            
            self.add_line_if_needed((len(lines), lines[-1]))
            self.modelStack.top.end_line = len(lines)

            models.append(self.modelStack.top)
            self.modelStack.pop()

            self.stateStack.top = self.stateStack.top
            self.stateStack.pop()

        return models
