# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import json

import lark_oapi as lark
from lark_oapi.api.auth.v3 import *

class FTCodeDetectorFeiShuRequester():
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

        self.client = lark.Client.builder().app_id(app_id).app_secret(app_secret).enable_set_token(True).log_level(lark.LogLevel.DEBUG).build()

        self.tenant_access_token = self.refresh_tenant_access_token()
        self.option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()
    
    def refresh_tenant_access_token(self) -> str:

        request: InternalTenantAccessTokenRequest = InternalTenantAccessTokenRequest.builder() \
            .request_body(InternalAppAccessTokenRequestBody.builder()
                          .app_id(self.app_id)
                          .app_secret(self.app_secret)
                          .build()) \
            .build()
        response: InternalAppAccessTokenResponse = self.client.auth.v3.tenant_access_token.create(request)

        if not response.success():
            lark.logger.error(
                f'client.auth.v3.auth.tenant_access_token_internal failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}')
            return None
        
        data = json.loads(response.raw.content)

        if 'tenant_access_token' not in data:
            return None

        return data['tenant_access_token']

    def request_headers(self):
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer {tenant_access_token}'.format(tenant_access_token = self.tenant_access_token)
        }