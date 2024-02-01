# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import sys
import os
import json

from FTCodeDetectorConstDefine import *

from FTCodeDetectorFeiShuFile import FTCodeDetectorFeiShuBitableFile
from FTCodeDetectorSingleton import FTCodeDetectorSingleton

class FTCodeDetectorBusinessConfig():
    def __init__(self, type: str, config: dict = None) -> None:
        self.business_type = type
        self.business_desc = type

        self.table_id = None
        self.file_url = None

        if config != None:

            if 'table_id' in config:
                self.table_id = config['table_id']

            if 'file_url' in config:
                self.file_url = config['file_url']

            if 'business_desc' in config:
                self.business_desc = config['business_desc']

    def update(self, bitable_file: FTCodeDetectorFeiShuBitableFile):
        if bitable_file == None:
            return
        
        self.table_id = bitable_file.table_id[self.business_type]
        self.file_url = '%s?table=%s' % (bitable_file.url, self.table_id)

@FTCodeDetectorSingleton
class FTCodeDetectorConfig():

    def __init__(self):
        self.FEISHU_APP_ID = None
        self.FEISHU_APP_SECRET = None

        self.FTOA_APP_KEY = None
        self.FTOA_APP_SEC = None

        self.file_manager = None

        self.chat_group = None

        self.platform = None

        self.message_card_id = None

        self.file_token = None
        self.file_url = None
        self.file_name = FTCodeDetectorConst.DEFAULT_FILE_NAME

        self.business: dict = {}

    def get_business(self, business_type: str) -> FTCodeDetectorBusinessConfig:
        if business_type == None or len(business_type) <= 0:
            return None
        
        if business_type not in self.business:
            return self.new_business(business_type)
        
        return self.business[business_type]

    def new_business(self, business_type: str) -> FTCodeDetectorBusinessConfig:
        if business_type in self.business:
            return

        business = FTCodeDetectorBusinessConfig(business_type)
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

        if 'file_name' in contents:
            self.file_name = contents['file_name']

        if 'chat_group' in contents:
            self.chat_group = contents['chat_group']

        if 'message_card_id' in contents:
            self.message_card_id = contents['message_card_id']

        if 'file_manager' in contents:
            self.file_manager = contents['file_manager']

        if 'business' in contents:
            for (business_type, item) in contents['business'].items():
                business = FTCodeDetectorBusinessConfig(business_type, item)
                self.business[business_type] = business

    def restore_config(self, config_file: str = 'config.json'):
        contents: dict = {
            'feishu_app_id': self.FEISHU_APP_ID,
            'feishu_app_secret': self.FEISHU_APP_SECRET,
            'ftoa_app_key': self.FTOA_APP_KEY,
            'ftoa_app_sec': self.FTOA_APP_SEC,
            'platform': self.platform if self.platform != None else 'Unknown',
        }

        if self.message_card_id != None and len(self.message_card_id) > 0:
            contents['message_card_id'] = self.message_card_id

        if self.file_manager != None and len(self.file_manager) > 0:
            contents['file_manager'] = self.file_manager
        
        with open(config_file, "w") as f:
            jstr = json.dumps(contents, indent = 4)
            f.write(jstr)

        self.load_config(config_file)

    def save_config(self, config_file: str = 'config.json'):

        contents: dict = {
            'feishu_app_id': self.FEISHU_APP_ID,
            'feishu_app_secret': self.FEISHU_APP_SECRET,
            'ftoa_app_key': self.FTOA_APP_KEY,
            'ftoa_app_sec': self.FTOA_APP_SEC,
            'platform': self.platform if self.platform != None else 'Unknown',
        }

        if self.file_name != None:
            contents['file_name'] = self.file_name

        if self.file_token != None:
            contents['file_token'] = self.file_token

        if self.file_url != None:
            contents['file_url'] = self.file_url

        if self.file_manager != None and len(self.file_manager) > 0:
            contents['file_manager'] = self.file_manager

        if self.message_card_id != None and len(self.message_card_id) > 0:
            contents['message_card_id'] = self.message_card_id

        business = {}
        for (business_type, item) in self.business.items():
            business_contents = {}

            if item.table_id != None and len(item.table_id) > 0:
                business_contents['table_id'] = item.table_id

            if item.file_url != None and len(item.file_url) > 0:
                business_contents['file_url'] = item.file_url

            if item.business_desc != None and len(item.business_desc) > 0:
                business_contents['business_desc'] = item.business_desc

            business[business_type] = business_contents

        contents['business'] = business

        with open(config_file, "w") as f :
            jstr = json.dumps(contents, indent = 4)
            f.write(jstr)

if __name__ == 'FTCodeDetectorConfig':
    sys.modules[__name__] = FTCodeDetectorConfig()