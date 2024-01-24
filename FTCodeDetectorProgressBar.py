# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from time import sleep
from progressbar import *

class FTCodeDetectorProgressBar():
    def __init__(self, hint: str = '扫描中: ', maxval: int = 100) -> None:
        widgets = [hint, Percentage(), ' ', Bar('>>'), ' ', Timer(), ' ', ETA(), ' ']
        self.progress = progressbar.ProgressBar(maxval = maxval, widgets = widgets).start()
    
    def update(self, value: int):
        self.progress.update(value)