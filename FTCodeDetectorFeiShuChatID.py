# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import lark_oapi

class FTCodeDetectorFeiShuChatID():
    def __init__(self, chat_id: lark_oapi.api.im.v1.list_chat.ListChat):
        self.avatar = chat_id.avatar
        self.chat_id = chat_id.chat_id
        self.description = chat_id.description
        self.external = chat_id.external
        self.name = chat_id.name
        self.owner_id = chat_id.owner_id
        self.owner_id_type = chat_id.owner_id_type
        self.tenant_key = chat_id.tenant_key

    def __eq__(self, __value: object) -> bool:
        return self.chat_id == __value.chat_id and self.name == __value.name