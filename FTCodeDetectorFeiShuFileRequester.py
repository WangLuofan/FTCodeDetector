# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

from typing import Any

import lark_oapi as lark

from lark_oapi.api.drive.v1 import *
from lark_oapi.api.auth.v3 import *

from FTCodeDetectorFtoaRequester import FTCodeDetectorFtoaRequester
from FTCodeDetectorFeiShuFile import *
from FTCodeDetectorFeishuRequester import FTCodeDetectorFeiShuRequester

class FTCodeDetectorFeiShuFileRequester(FTCodeDetectorFeiShuRequester):
    def __init__(self, app_id: str, app_secret: str):
        super().__init__(app_id, app_secret)
    
    def create_file(self, file_name: str) -> FTCodeDetectorFeiShuFile:
        raise NotImplementedError('子类必须实现该方法')
    
    def append_records(self, file: FTCodeDetectorFeiShuFile, records: [Any]) -> bool:
        raise NotImplementedError('子类必须实现该方法')
    
    def delete_file(self, file: FTCodeDetectorFeiShuFile) -> bool:
        if file == None:
            return False

        request: DeleteFileRequest = DeleteFileRequest.builder().file_token(file.token).type(file.type).build()
        response: DeleteFileResponse = self.client.drive.v1.file.delete(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.drive.v1.file.delete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return True

    def delete_all_files(self):
        files: dict = self.list_files()

        for (_, file) in files.items():
            self.delete_file(file)
    
    def add_member_perm(self, nick: str, file: FTCodeDetectorFeiShuFile, perm: str) -> bool:
        if file == None or nick == None or len(nick) == 0 \
            or perm == None or len(perm) == 0 \
                or perm not in ['view', 'edit', 'full_access']:
            return False

        user_info = FTCodeDetectorFtoaRequester.get_user_info(nick)
        if user_info == None or 'feishuOpenId' not in user_info :
            return False
        
        openId = user_info['feishuOpenId']

        request: CreatePermissionMemberRequest = CreatePermissionMemberRequest.builder() \
            .token(file.token) \
            .type(file.type) \
            .need_notification(False) \
            .request_body(BaseMember.builder()
                      .member_type('openid')
                      .member_id(openId)
                      .perm(perm)
                      .build()) \
            .build()
        
        response: CreatePermissionMemberResponse = self.client.drive.v1.permission_member.create(request, self.option)
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.permission_member.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        lark.logger.info(lark.JSON.marshal(response.data, indent = 4))
        return True

    def list_files(self, next_page_token: str = '') -> dict:
        request: ListFileRequest = ListFileRequest.builder() \
            .page_token(next_page_token) \
            .build()
        
        response: ListFileResponse = self.client.drive.v1.file.list(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.drive.v1.file.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return None
        
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

        files: dict = {}
        for f in response.data.files:
            file = FTCodeDetectorFeiShuBitableFile(f)
            files[file.token] = file

        if response.data.has_more == True and response.data.next_page_token != None:
            files.update(self.list_files(response.data.next_page_token))

        return files