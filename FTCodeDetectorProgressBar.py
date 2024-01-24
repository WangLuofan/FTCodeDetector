# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from progressbar import *

class FTCodeDetectorProgressBar():
    def __init__(self, hint: str = '扫描中: ', maxval: int = 100) -> None:
        widgets = [hint, Percentage(), ' ', Bar('>'), ' ', Timer(), ' ']

        self.value = 0
        self.progress = progressbar.ProgressBar(maxval = maxval, widgets = widgets).start()
    
    def update(self):
        self.value = self.value + 1
        self.progress.update(self.value)

    def finish(self):
        self.progress.finish()