# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import os
import json

class FTCodeDetectorConfigUtil():
    @staticmethod
    def load_config(config_file: str = 'config.json'):
        if os.path.exists(config_file) == False:
            return None

        with open(config_file, "r") as f:
            contents = json.loads(f.read())

        from FTCodeDetectorConfig import FTCodeDetectorConfig

        config = FTCodeDetectorConfig()
        if 'feishu_app_id' in contents:
            config.FEISHU_APP_ID = contents['feishu_app_id']

        if 'feishu_app_secret' in contents:
            config.FEISHU_APP_SECRET = contents['feishu_app_secret']

        if 'ftoa_app_key' in contents:
            config.FTOA_APP_KEY = contents['ftoa_app_key']

        if 'ftoa_app_sec' in contents:
            config.FTOA_APP_SEC = contents['ftoa_app_sec']
        
        if 'platform' in contents:
            config.platform = contents['platform']

        if 'file_token' in contents:
            config.file_token = contents['file_token']

        if 'file_url' in contents:
            config.file_url = contents['file_url']

        if 'business' in contents:
            for (business_type, item) in contents['business'].items():
                from FTCodeDetectorConfig import FTCodeDetectorBusinessConfig
                
                business = FTCodeDetectorBusinessConfig(business_type, item)
                config.business[business_type] = business

        return config

    @staticmethod
    def save_config(config_file: str = 'config.json'):
        import FTCodeDetectorConfig

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
            if item.message_card_id != None and len(item.message_card_id) > 0:
                business_contents['message_card_id'] = item.message_card_id
            if item.table_id != None and len(item.table_id) > 0:
                business_contents['table_id'] = item.table_id
            if item.file_url != None and len(item.file_url) > 0:
                business_contents['file_url'] = item.file_url

            business[business_type] = business_contents

        contents['business'] = business

        with open(config_file, "w") as f :
            jstr = json.dumps(contents, indent=4)
            f.write(jstr)