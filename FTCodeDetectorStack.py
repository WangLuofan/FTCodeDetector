# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from typing import Any

class FTCodeDetectorStack():
    def __init__(self, initial: Any = None):
        self.stack = []

        if initial != None:
            self.stack.append(initial)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == 'top':
            self.stack[-1] = __value
            return

        return super().__setattr__(__name, __value)
    
    @property
    def top(self) -> Any:
        if len(self.stack) <= 0:
            return None
        
        return self.stack[-1]
    
    @property
    def size(self):
        return len(self.stack)
    
    @property
    def empty(self) -> bool:
        return self.size == 0
    
    def push(self, value: Any):
        if value == None:
            return
        
        self.stack.append(value)

    def pop(self) -> Any:
        if self.empty:
            return
        
        top = self.top
        
        self.stack.pop()

        return top

    def clear(self):
        if self.empty:
            return
        
        self.stack.clear()