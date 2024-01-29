# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import json
import lark_oapi as lark

from lark_oapi.api.auth.v3 import *
from lark_oapi.api.im.v1 import *

from FTCodeDetectorFeiShuChatID import FTCodeDetectorFeiShuChatID
from FTCodeDetectorHttpRequester import FTCodeDetectorHttpRequester
from FTCodeDetectorFeishuRequester import FTCodeDetectorFeiShuRequester

class FTCodeDetectorFeiShuChatRequester(FTCodeDetectorFeiShuRequester):
    def __init__(self, app_id: str, app_secret: str):
        super().__init__(app_id, app_secret)

    def all_chat_id(self, page_token: str = '') -> [FTCodeDetectorFeiShuChatID]:
        request: ListChatRequest = ListChatRequest.builder().user_id_type('open_id').page_token(page_token).build()
        response: ListChatResponse = self.client.im.v1.chat.list(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.im.v1.chat.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

        chat_list: [FTCodeDetectorFeiShuChatID] = []
        for item in response.data.items:
            chat_list.append(FTCodeDetectorFeiShuChatID(item))
        
        if response.data.has_more == True and response.data.page_token != None:
            chat_list.append(self.all_chat_id(response.data.page_token).extend())
        
        return chat_list

    def send_message(self, group_name: str = None, payload = None) -> bool:

        if payload == None or len(payload) == 0:
            return False

        chat_ids = self.all_chat_id()
        if chat_ids == None or len(chat_ids) <= 0:
            return False

        if group_name != None and len(group_name) > 0:
            for chat_id in chat_ids:
                if chat_id.name == group_name:
                    if self.send_message_(chat_id, payload) == True:
                        lark.logger.info('消息已成功发送到\'{name}\''.format(name = group_name))
                        return True
                    
                    lark.logger.error('给\'{name}\'发送消息失败'.format(name = group_name))
                    return False
        else:
            result: bool = True
            for chat_id in chat_ids:
                result = result and self.send_message_(chat_id, payload)

            if result == False:
                lark.logger.info('消息发送失败')

            lark.logger.info('消息已全部发送成功')

            return result
    
    def send_message_(self, chat_id: FTCodeDetectorFeiShuChatID, payload: dict) -> bool:

        if payload == None or len(payload) <= 0:
            return

        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type('chat_id') \
            .request_body(CreateMessageRequestBody.builder()
                .receive_id(chat_id.chat_id)
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
    