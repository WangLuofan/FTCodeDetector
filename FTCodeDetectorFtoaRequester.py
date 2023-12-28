# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import FTCodeDetectorConfig
from Ftoa import Ftoa

class FTCodeDetectorFtoaRequester():
    @staticmethod
    def get_user_info(nick: str) -> dict:
        
        if len(nick) <= 0:
            return None

        ftoa = Ftoa.Ftoa({
            'appKey': FTCodeDetectorConfig.FTOA_APP_KEY,
            'appSecret': FTCodeDetectorConfig.FTOA_APP_SEC,
            'region': 'ML',
        })

        user_info: dict = ftoa.getStaffByNick(nick)

        return user_info