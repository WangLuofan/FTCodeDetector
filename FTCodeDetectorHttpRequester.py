# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import requests
import json

from FTCodeDetectorHttpResponse import FTCodeDetectorHttpResponse

class FTCodeDetectorHttpRequester():
    @staticmethod
    def GET(url, request_headers, data = None) -> FTCodeDetectorHttpResponse:
        resp = resp = requests.get(url=url, data=data, headers=request_headers)

        if resp == None or resp.text == None:
            return None
        
        text = json.loads(resp.text)
        return FTCodeDetectorHttpResponse(resp.status_code, text['code'] \
                                          if 'code' in text else '-1', \
                                            text['msg'] 
                                            if 'msg' in text else 'GET request error', \
                                                text['data'] \
                                                    if 'data' in text else None)

    @staticmethod
    def PUT(url, request_headers, data) -> FTCodeDetectorHttpResponse:
        resp = requests.put(url, headers=request_headers, data=data)
        if resp == None or resp.text == None:
            return

        text = json.loads(resp.text)
        return FTCodeDetectorHttpResponse(resp.status_code, text['code'] \
                                          if 'code' in text else '-1', \
                                            text['msg'] \
                                                if 'msg' in text else 'PUT request error', \
                                                    text['data'] \
                                                        if 'data' in text else None)

    @staticmethod
    def POST(url, request_headers, data) -> FTCodeDetectorHttpResponse:
        resp = requests.post(url=url, headers=request_headers, data=data)
        if resp == None or resp.text == None:
            return None

        text = json.loads(resp.text)
        return FTCodeDetectorHttpResponse(resp.status_code, text['code'] \
                                          if 'code' in text else '-1', \
                                            text['msg'] \
                                                if 'msg' in text else 'POST request error', \
                                                    text['data'] \
                                                        if 'data' in text else None)