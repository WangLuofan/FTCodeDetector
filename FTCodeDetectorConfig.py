# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import sys
import os
import json

from FTCodeDetectorFeiShuFile import FTCodeDetectorFeiShuBitableFile
from FTCodeDetectorSingleton import FTCodeDetectorSingleton

class FTCodeDetectorBusinessConfig():
    def __init__(self, type: str, config: dict = None) -> None:
        self.business_type = type

        self.message_card_id = None
        self.table_id = None
        self.file_url = None

        if config != None:

            if 'message_card_id' in config:
                self.message_card_id = config['message_card_id']

            if 'table_id' in config:
                self.table_id = config['table_id']

            if 'file_url' in config:
                self.file_url = config['file_url']

    def update(self, bitable_file: FTCodeDetectorFeiShuBitableFile):
        if bitable_file == None:
            return
        
        self.table_id = bitable_file.table_id
        self.file_url = '%s?table=%s' % (bitable_file.url, bitable_file.table_id)

@FTCodeDetectorSingleton
class FTCodeDetectorConfig():

    def __init__(self):
        self.FEISHU_APP_ID = None
        self.FEISHU_APP_SECRET = None
        self.FTOA_APP_KEY = None
        self.FTOA_APP_SEC = None
        self.platform = None
        self.file_token = None
        self.file_url = None
        self.business: dict = {}

        self.load_config()

    def get_business(self, business_type: str) -> FTCodeDetectorBusinessConfig:
        if business_type == None or len(business_type) <= 0:
            return None
        
        if business_type not in self.business:
            return self.new_business(business_type)
        
        return self.business[business_type]

    def new_business(self, business_type: str) -> FTCodeDetectorBusinessConfig:
        if business_type in self.business:
            return

        business = FTCodeDetectorBusinessConfig(type)
        self.business[business_type] = business

        return business

    def load_config(self, config_file: str = 'config.json'):
        if os.path.exists(config_file) == False:
            return None

        with open(config_file, "r") as f:
            contents = json.loads(f.read())

        if 'feishu_app_id' in contents:
            self.FEISHU_APP_ID = contents['feishu_app_id']

        if 'feishu_app_secret' in contents:
            self.FEISHU_APP_SECRET = contents['feishu_app_secret']

        if 'ftoa_app_key' in contents:
            self.FTOA_APP_KEY = contents['ftoa_app_key']

        if 'ftoa_app_sec' in contents:
            self.FTOA_APP_SEC = contents['ftoa_app_sec']
        
        if 'platform' in contents:
            self.platform = contents['platform']

        if 'file_token' in contents:
            self.file_token = contents['file_token']

        if 'file_url' in contents:
            self.file_url = contents['file_url']

        if 'business' in contents:
            for (business_type, item) in contents['business'].items():
                from FTCodeDetectorConfig import FTCodeDetectorBusinessConfig
                
                business = FTCodeDetectorBusinessConfig(business_type, item)
                self.business[business_type] = business

    def save_config(config_file: str = 'config.json'):

        contents: dict = {
            'feishu_app_id': FTCodeDetectorConfig.FEISHU_APP_ID,
            'feishu_app_secret': FTCodeDetectorConfig.FEISHU_APP_SECRET,
            'ftoa_app_key': FTCodeDetectorConfig.FTOA_APP_KEY,
            'ftoa_app_sec': FTCodeDetectorConfig.FTOA_APP_SEC,
            'platform': FTCodeDetectorConfig.platform
        }

        if FTCodeDetectorConfig.file_token != None:
            contents['file_token'] = FTCodeDetectorConfig.file_token

        if FTCodeDetectorConfig.file_url != None:
            contents['file_url'] = FTCodeDetectorConfig.file_url

        business = {}
        for (business_type, item) in FTCodeDetectorConfig.business.items():
            business_contents = {}
            if item.message_card_id != None and len(item.message_card_id) > -1:
                business_contents['message_card_id'] = item.message_card_id
            if item.table_id != None and len(item.table_id) > -1:
                business_contents['table_id'] = item.table_id
            if item.file_url != None and len(item.file_url) > -1:
                business_contents['file_url'] = item.file_url

            business[business_type] = business_contents

        contents['business'] = business

        with open(config_file, "w") as f :
            jstr = json.dumps(contents, indent=3)
            f.write(jstr)

if __name__ == 'FTCodeDetectorConfig':
    sys.modules[__name__] = FTCodeDetectorConfig()