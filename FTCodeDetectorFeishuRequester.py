# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import json
import datetime

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.drive.v1 import *
from lark_oapi.api.auth.v3 import *

from FTCodeDetectorHttpRequester import FTCodeDetectorHttpRequester
from FTCodeDetectorFtoaRequester import FTCodeDetectorFtoaRequester
from FTCodeDetectorFeiShuFile import *

class FTCodeDetectorFeiShuRequester():
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.client = lark.Client.builder().app_id(app_id).app_secret(app_secret).enable_set_token(True).log_level(lark.LogLevel.DEBUG).build()

        self.tenant_access_token = self.refresh_tenant_access_token()
        self.option = lark.RequestOption.builder().tenant_access_token(self.tenant_access_token).build()

    def create_file(self, file_name: str) -> FTCodeDetectorFeiShuFile:
        raise NotImplementedError('子类必须实现该方法')
    
    def write(self, file: FTCodeDetectorFeiShuFile, records: [Any]):
        raise NotImplementedError('子类必须实现该方法')
    
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
    
    # perm: view(可阅读角色)/edit(可编辑角色)/full_access(可管理角色)
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
    
    # def expire_status(self, expire_date: datetime) -> (str, str):
    #     ctime= datetime.now()
    #     cdate = datetime.strptime('{year}/{month}/{day}'.format(year = ctime.year, month = ctime.month, day = ctime.day), r'%Y/%m/%d')

    #     diff_date = expire_date - cdate

    #     if diff_date.days < 0:
    #         return ('已过期', '高')
    #     elif diff_date.days == 0:
    #         return ('今天过期', '高')
    #     elif diff_date.days > 0 and diff_date.days <= 7:
    #         return ('一周内过期', '中')
    #     elif diff_date.days > 7 and diff_date.days <= 14:
    #         return ('两周内过期', '低')
        
    #     return ('未过期', '低')

    def chat_id(self) -> dict:
        url = 'https://open.feishu.cn/open-apis/im/v1/chats'
        resp = FTCodeDetectorHttpRequester.GET(url, self.request_headers())

        if resp.status_code != 200 and resp.code != 0:
            lark.logger.error(
                f'chat_id 请求失败, code: {resp.code}, msg: {resp.msg}')
            return None
        
        lark.logger.info(f'chat_id 请求成功')
        return resp.data

    def send_message(self):
        items = []
        charIds = self.chat_id()
        if 'items' in charIds:
            items = charIds['items']

        if items == None or len(items) == 0:
            return False
        
        for item in items:
            if 'chat_id' not in item:
                continue

            chat_id = item['chat_id']
            if chat_id == None:
                continue

            if 'name' not in item:
                lark.logger.error('发送消息失败')
                continue

            if self.send_message(chat_id) == False:
                lark.logger.error('给\'{name}\'发送消息失败'.format(name = item['name']))
                continue
                
            lark.logger.info('消息已成功发送到\'{name}\''.format(name = item['name']))
    
    def send_message(self, chat_id: str, payload: dict) -> bool:

        # extensions = ''
        # for (index, ext) in enumerate(file_manager.extensions):
        #     if index != 0:
        #         extensions = extensions + '|'
        #     extensions += ext

        # url = 'https://futu.feishu.cn/base/{bitable_token}?table={table_id}&view={bitable_view_id}'.format(bitable_token = file_app_token, table_id = table_id, bitable_view_id = bitable_view_id)
        # if export_type == 'spreadsheets':
        #     url = 'https://futu.feishu.cn/sheets/{spread_sheet_id}?from=from_copylink'.format(spread_sheet_id = spread_sheet_id)

        # scan_result = []

        # item_count = min(3, len(result))
        # for idx in range(0, item_count):
        #     outdate = result[idx]

        #     filename = FTCodeDetectorFileManager.get_file_name(outdate.source_file)
        #     scan_result.append({
        #                     'scan_result_file': filename,
        #                     'scan_line_result': '{start} ~ {end}'.format(start = outdate.start_line + 1, end = outdate.end_line + 1),
        #                 })

        # ctime = datetime.now()
        # payload = {
        #     'type': 'template',
        #     'data': {
        #         'template_id': message_card_id,
        #         'template_variable': {
        #             'scan_date_time': '{year}-{month}-{day} {hour}:{minute}:{second}' \
        #                 .format(year = '%04d' % ctime.year, month = '%02d' % ctime.month, day = '%02d' % ctime.day, hour = '%02d' % ctime.hour, minute = '%02d' % ctime.minute, second = '%02d' % ctime.second),
        #             'scan_project_directory': file_manager.path,
        #             'scan_file_ext': extensions,
        #             'outdated_count': str(len(result)),
        #             'scan_result': scan_result,
        #             'scan_result_sheets_url': url
        #         }
        #     }
        # }

        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type('chat_id') \
            .request_body(CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type('interactive')
                .content(json.dumps(payload))
                .build()) \
        .build()
        
        response: CreateMessageResponse = self.client.im.v1.message.create(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False

        lark.logger.info(f"发送消息成功")
        return True

    def list_files(self) -> dict:
        request: ListFileRequest = ListFileRequest.builder().build()
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

        return files

    def request_headers(self):
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer {tenant_access_token}'.format(tenant_access_token = self.tenant_access_token)
        }