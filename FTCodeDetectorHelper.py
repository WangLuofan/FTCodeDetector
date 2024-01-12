# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import hashlib

class FTCodeDetectorHelper():

    @staticmethod
    def md5(text: str) -> str:
        if text == None or len(text) <= 0:
            return None

        md5 = hashlib.md5()
        md5.update(text.encode('utf-8'))

        return md5.hexdigest()