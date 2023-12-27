# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import lark_oapi
from lark_oapi.api.drive.v1 import *

class FTCodeDetectorFeiShuFile():
    class FTCodeDetectorFeiShuFileShortCutInfo():
        def __init__(self, shortcut_info: lark_oapi.api.drive.v1.model.file.ShortcutInfo):
            self.target_token = shortcut_info.target_token
            self.target_type = shortcut_info.target_type

    def __init__(self, f: lark_oapi.api.drive.v1.model.file.File):
        self.token = f.token
        self.name = f.name
        self.type = f.type
        self.parent_token = f.parent_token
        self.url = f.url
        self.created_time = f.created_time
        self.modified_time = f.modified_time
        self.owner_id = f.owner_id

        self.shortcut_info = self.FTCodeDetectorFeiShuFileShortCutInfo(f.shortcut_info)