# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import requests
import json

from FTCodeDetectorHttpResponse import FTCodeDetectorHttpResponse

class FTCodeDetectorHttpRequester():
    @staticmethod
    def GET(url, request_headers, data = None) -> FTCodeDetectorHttpResponse:
        resp = resp = requests.get(url=url, data=data, request_headers=request_headers)

        if resp == None or resp.text == None:
            return None
        
        text = json.loads(resp.text)
        return FTCodeDetectorHttpResponse(resp.status_code, text['code'], text['msg'], text['data'])

    @staticmethod
    def PUT(url, request_headers, data) -> FTCodeDetectorHttpResponse:
        resp = requests.put(url, request_headers=request_headers, data=data)
        if resp == None or resp.text == None:
            return

        text = json.loads(resp.text)
        return FTCodeDetectorHttpResponse(resp.status_code, text['code'], text['msg'], text['data'])

    @staticmethod
    def POST(url, request_headers, data) -> FTCodeDetectorHttpResponse:
        resp = requests.post(url=url, request_headers=request_headers, data=data)
        if resp == None or resp.text == None:
            return None

        text = json.loads(resp.text)
        return FTCodeDetectorHttpResponse(resp.status_code, text['code'], text['msg'], text['data'])