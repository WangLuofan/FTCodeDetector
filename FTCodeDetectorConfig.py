# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import sys

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

from FTCodeDetectorConfigUtil import FTCodeDetectorConfigUtil
sys.modules[__name__] = FTCodeDetectorConfigUtil.load_config()