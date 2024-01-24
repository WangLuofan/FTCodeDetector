# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from time import sleep
from progressbar import *

class FTCodeDetectorProgressBar():
    def __init__(self, hint: str = '扫描中: ') -> None:
        widgets = [hint, Percentage(), ' ', Bar('>>'), ' ', Timer(), ' ', ETA(), ' ']
        self.progress = progressbar.ProgressBar(maxval = 100, widgets = widgets).start()
    
    def update(self):
        sleep(0.02)
        self.progress.update(2)