# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import FTCodeDetectorConfig
from Ftoa import Ftoa

class FTCodeDetectorFtoaRequester():
    @staticmethod
    def new_ftoa() -> Ftoa:
        ftoa = Ftoa.Ftoa({
            'appKey': FTCodeDetectorConfig.FTOA_APP_KEY,
            'appSecret': FTCodeDetectorConfig.FTOA_APP_SEC,
            'region': 'ML',
        })

        return ftoa

    @staticmethod
    def get_user_info(nick: str) -> dict:
        
        if nick == None or len(nick) <= 0:
            return None

        user_info: dict = FTCodeDetectorFtoaRequester.new_ftoa().getStaffByNick(nick)

        return user_info

    @staticmethod
    def get_user_department(nick: str) -> list:
        if nick == None or len(nick) <= 0:
            return None
        
        return FTCodeDetectorFtoaRequester.new_ftoa().getStaffDepartmentListByNick(nick)