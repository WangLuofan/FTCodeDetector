# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from progressbar import *

class FTCodeDetectorProgressBar():
    def __init__(self, hint: str = r'扫描中: ', maxval: int = 100) -> None:
        widgets = [Percentage(), ' ', Bar('>'), ' ', Timer(), ' ']

        self.value = 0
        self.hint = hint
        self.hint_output = False
        self.progress = progressbar.ProgressBar(maxval = maxval, widgets = widgets).start()
    
    def update(self):
        self.value = self.value + 1

        if self.hint_output == False:
            print(self.hint, )
            self.hint_output = True

        self.progress.update(self.value)

    def finish(self):
        self.progress.finish()