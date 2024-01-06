# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from FTCodeDetectorModel import FTCodeDetectorModel

class FTCodeDetectorModelStack():
    def __init__(self):
        self.stack = []
    
    @property
    def top(self) -> FTCodeDetectorModel:
        if len(self.stack) <= 0:
            return None
        return self.stack[-1]
    
    def size(self):
        return len(self.stack)
    
    def empty(self) -> bool:
        return self.size() == 0
    
    def push(self, model: FTCodeDetectorModel):
        if model == None:
            return
        self.stack.append(model)

    def pop(self):
        if self.empty():
            return
        self.stack.pop()

    def clear(self):
        if self.empty():
            return
        self.stack.clear()