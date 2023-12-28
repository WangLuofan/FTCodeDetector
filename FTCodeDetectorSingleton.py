# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from typing import Any

class FTCodeDetectorSingleton(object):
    def __init__(self, cls) -> None:
        self._cls = cls
        self._instance = {}
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]