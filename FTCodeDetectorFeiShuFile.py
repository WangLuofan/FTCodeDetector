# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import lark_oapi
from lark_oapi.api.bitable.v1.model.app import App

from lark_oapi.api.drive.v1 import *
from lark_oapi.api.drive.v1.model.file import File

import FTCodeDetectorConst

class FTCodeDetectorFeiShuFile():
    class FTCodeDetectorFeiShuFileShortCutInfo():
        def __init__(self, shortcut_info: lark_oapi.api.drive.v1.model.file.ShortcutInfo):
            self.target_token = shortcut_info.target_token
            self.target_type = shortcut_info.target_type

    def __init__(self, file: lark_oapi.api.drive.v1.model.file.File):
        self.token = None
        self.name = None
        self.type = None
        self.parent_token = None
        self.url = None
        self.created_time = None
        self.modified_time = None
        self.owner_id = None
        self.shortcut_info = None

        if file != None:
            self.token = file.token
            self.name = file.name
            self.type = file.type
            self.parent_token = file.parent_token
            self.url = file.url
            self.created_time = file.created_time
            self.modified_time = file.modified_time
            self.owner_id = file.owner_id

            if file.shortcut_info != None:
                self.shortcut_info = self.FTCodeDetectorFeiShuFileShortCutInfo(file.shortcut_info)

    def update(self, business_config):
        if business_config.file_url != None:
            self.url = business_config.file_url

class FTCodeDetectorFeiShuBitableField():
    def __init__(self, title: str, type: str) -> None:
        self.field_title = title
        self.field_type = type

        self.__dict__[title] = type

    def __eq__(self, __value: object) -> bool:
        return self.field_title == __value.field_title


    def field_exist(self, title: str) -> bool:
        return title in self.__dict__

    def get_field_type(self) -> int:
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_TEXT:
            return 1
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_DATETIME:
            return 5
        if self.field_type == FTCodeDetectorConst.FEILD_TYPE_SINGLE:
            return 3
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_CHECKBOX:
            return 7
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_PERSON:
            return 11
        
        return 1
    
    def get_field_ui_type(self) -> str:
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_TEXT:
            return FTCodeDetectorConst.FIELD_UI_TYPE_TEXT
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_DATETIME:
            return FTCodeDetectorConst.FIELD_UI_TYPE_DATETIME
        if self.field_type == FTCodeDetectorConst.FEILD_TYPE_SINGLE:
            return FTCodeDetectorConst.FIELD_UI_TYPE_SINGLE
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_CHECKBOX:
            return FTCodeDetectorConst.FIELD_UI_TYPE_CHECKBOX
        if self.field_type == FTCodeDetectorConst.FIELD_TYPE_PERSON:
            return FTCodeDetectorConst.FIELD_UI_TYPE_PERSON
        
        return FTCodeDetectorConst.FIELD_TYPE_TEXT

class FTCodeDetectorFeiShuBitableFile(FTCodeDetectorFeiShuFile):
    def __init__(self, file: File = None, bitable_app: App = None):
        super().__init__(file)
        self.table_id = None

        if bitable_app != None:
            self.token = bitable_app.app_token
            self.name = bitable_app.name
            self.url = bitable_app.url
            self.table_id = bitable_app.default_table_id
            self.type = 'bitable'

    def update(self, business_config):
        if business_config == None:
            return
        
        super().update(business_config)
        
        if business_config.table_id != None:
            self.table_id = business_config.table_id