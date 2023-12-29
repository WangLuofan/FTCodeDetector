# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from typing import Any


class FTCodeDetectorMarco():
    def __init__(self, tag: str):
        self.tag = tag
        self.attributes = {
            'type': 'text',
            'desc': tag
        }
        self.value = None

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
        self.business_type = None
        self.business_desc = None
        self.source_file = None
        self.source_lines = []
        
        self.user_defined: [FTCodeDetectorMarco] = []

class FTCodeDetectorBusinessModel():
    def __init__(self, business_type: str, business_desc: str, models: [FTCodeDetectorModel]):
        self.business_type = business_type
        self.business_desc = business_desc

        self.models = models
