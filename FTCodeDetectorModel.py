# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import FTCodeDetectorHelper
from FTCodeDetectorConstDefine import *

class FTCodeDetectorMarco():
    def __init__(self, tag: str, desc: str = None, value: str = FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN):
        self.tag = tag
        self.attributes = {
            'type': 'text',
            'desc': desc if desc != None else tag
        }

        self.value = value

    def get_type(self) -> str:
        if 'type' in self.attributes:
            return self.attributes['type']
        
        return 'text'
    
    def get_desc(self) -> str:
        if 'desc' in self.attributes:
            return self.attributes['desc']
        
        return self.tag

    def update_type(self, type: str):
        if type not in ('text', 'datetime', 'checkbox', 'person'):
            return
        
        self.attributes['type'] = type

    def update_desc(self, desc: str):
        if desc == None or len(desc) <= 0:
            return
        
        self.attributes['desc'] = desc

    def parse_attributes(self, attributes: str):
        key = None

        text: str = ''
        for s in attributes:
            if s == ' ':
                if key == None:
                    key = text
                    text = ''
                elif len(text) > 0:
                    self.attributes[key] = text
                    text = ''
                    key = None

                continue

            if s == '=':
                if key == None:
                    key = text

                text = ''
                continue

            text = text + s

        if key != None and len(text) > 0:
            self.attributes[key] = text

class FTCodeDetectorModel():
    def __init__(self):
        self.start_line = -1
        self.end_line = -1

        self.business_marco = None
        self.principal_marco = None
        
        self.abs_path = None
        self.source_file = None
        self.source_lines = []

        self.user_defined: [FTCodeDetectorMarco] = []

    @property
    def hexdigest(self) -> str:
        text: str = self.source_file \
            .join(self.business_marco.value if self.business_marco != None else FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN) \
                .join(str(self.start_line)) \
                .join(str(self.end_line)) \
                .join(t[1] for t in self.source_lines)
        
        return FTCodeDetectorHelper.FTCodeDetectorHelper.md5(text)


class FTCodeDetectorBusinessModel():
    def __init__(self, business_type: str, business_desc: str, models: [FTCodeDetectorModel] = None):
        self.business_type = business_type
        self.business_desc = business_desc

        self.models = models if models != None else []

    def append_models(self, models: [FTCodeDetectorModel]):
        self.models.extend(models)

    def append_model(self, model: FTCodeDetectorModel):
        self.models.append(model)
