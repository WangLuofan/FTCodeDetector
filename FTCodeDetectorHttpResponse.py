# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

class FTCodeDetectorHttpResponse():
    def __init__(self, status_code: int = 0, code: int = 0, msg: str = None, data: dict = None):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.data = data