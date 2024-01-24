# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import threading

from FTCodeDetectorModel import *
from FTCodeDetectorNFA import FTCodeDetectorNFA

class FTCodeDetectorThreading(threading.Thread):
    def __init__(self, files: [str], thread_lock: threading.Lock, result: [FTCodeDetectorModel], updater = None):
        threading.Thread.__init__(self)

        self.result = result
        self.updater = updater
        self.files = files
        self.thread_lock = thread_lock

    def run(self):
        for f in self.files:
            models = FTCodeDetectorNFA().match(f)

            if models != None and len(models) > 0:
                self.thread_lock.acquire(True)
                self.result.extend(models)
                self.thread_lock.release()

            self.updater()