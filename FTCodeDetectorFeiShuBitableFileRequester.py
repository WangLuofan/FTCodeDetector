# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

from FTCodeDetectorFeiShuFile import *
from FTCodeDetectorHttpRequester import FTCodeDetectorHttpRequester
from FTCodeDetectorFeiShuFileRequester import FTCodeDetectorFeiShuFileRequester

class FTCodeDetectorFeiShuBitableFileRequester(FTCodeDetectorFeiShuFileRequester):

    def __init__(self, app_id: str, app_secret: str):
        super().__init__(app_id, app_secret)

    def list_fields(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str) -> [FTCodeDetectorFeiShuBitableField]:
        request: ListAppTableFieldRequest = ListAppTableFieldRequest.builder() \
            .app_token(file.token) \
            .table_id(table_id) \
            .build()
        
        response: ListAppTableFieldResponse = self.client.bitable.v1.app_table_field.list(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_field.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

        items = []
        for item in response.data.items:
            items.append(FTCodeDetectorFeiShuBitableField(item.field_name, item.type))

        return items

    def list_records(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str, page_token: str = '') -> [FTCodeDetectorFeiShuBitableRecord]:

        request: ListAppTableRecordRequest = ListAppTableRecordRequest.builder() \
            .app_token(file.token) \
            .table_id(table_id) \
            .page_token(page_token) \
            .build()
        
        response: ListAppTableRecordResponse = self.client.bitable.v1.app_table_record.list(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        
        records: [FTCodeDetectorFeiShuBitableRecord] = []
        if response.data.items == None:
            return records

        for item in response.data.items:
            records.append(FTCodeDetectorFeiShuBitableRecord(item))
        
        if response.data.has_more == True and response.data.page_token != None:
            records.extend(self.list_records(file, table_id))

        return records

    def clear_records(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str):
        records: [FTCodeDetectorFeiShuBitableRecord] = self.list_records(file, table_id)
        if records == None and len(records) <= 0:
            return

        request: BatchDeleteAppTableRecordRequest = BatchDeleteAppTableRecordRequest.builder() \
            .app_token(file.token) \
            .table_id(table_id) \
            .request_body(BatchDeleteAppTableRecordRequestBody \
                          .builder() \
                          .records([record.record_id for record in records]) \
                          .build()) \
            .build()
        
        response: BatchDeleteAppTableRecordResponse = self.client.bitable.v1.app_table_record.batch_delete(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.batch_delete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return 

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return 

    def create_field(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str, field: FTCodeDetectorFeiShuBitableField):

        request: CreateAppTableFieldRequest = CreateAppTableFieldRequest.builder() \
            .app_token(file.token) \
            .table_id(table_id) \
            .request_body(AppTableField.builder()
                          .field_name(field.field_title)
                          .type(field.get_field_type())
                          .ui_type(field.get_field_ui_type())
                          .build()) \
                    .build()
        
        response: CreateAppTableFieldResponse = self.client.bitable.v1.app_table_field.create(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_field.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    def create_fields_if_needed(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str, fields: [FTCodeDetectorFeiShuBitableField]):
        if file == None or fields == None or len(fields) <= 0:
            return
        
        all_fields = self.list_fields(file, table_id)
        fields_need_create: [FTCodeDetectorFeiShuBitableField] = fields if all_fields == None or len(all_fields) <= 0 else []

        if all_fields != None and len(all_fields) > 0 and len(fields_need_create) <= 0:
            for field in fields:
                if field not in all_fields:
                    fields_need_create.append(field)
        
        self.create_fields(file, table_id, fields_need_create)

    def create_fields(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str, fields: [FTCodeDetectorFeiShuBitableField]):
        if fields == None or len(fields) <= 0:
            return
        
        for field in fields:
            self.create_field(file, table_id, field)

    def write(self, file: FTCodeDetectorFeiShuBitableFile, table_id: str, records: [AppTableRecord]) -> bool:
        if records == None or len(records) <= 0:
            return

        self.clear_records(file, table_id)

        request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
            .app_token(file.token) \
            .table_id(table_id) \
            .user_id_type('user_id') \
            .request_body(BatchCreateAppTableRecordRequestBody.builder() \
                          .records(records) \
                .build()) \
            .build()
        
        response: BatchCreateAppTableRecordResponse = self.client.bitable.v1.app_table_record.batch_create(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.batch_create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return True

    def create_file(self, file_name: str) -> (FTCodeDetectorFeiShuBitableFile, str):
        request: CreateAppRequest = CreateAppRequest.builder() \
            .request_body(ReqApp.builder()
                          .name(file_name)
                          .build()) \
                    .build()
        
        response: CreateAppResponse = self.client.bitable.v1.app.create(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        file: FTCodeDetectorFeiShuBitableFile = FTCodeDetectorFeiShuBitableFile(bitable_app = response.data.app)
        
        return (file, response.data.app.default_table_id)
    
    def create_table(self, file: FTCodeDetectorFeiShuBitableFile, table_name: str, fields: [FTCodeDetectorFeiShuBitableField]) -> str:
        if file == None or table_name == None or len(table_name) <= 0:
            return False
        
        headers: [AppTableCreateHeader] = []
        for field in fields:
            header: AppTableCreateHeader = AppTableCreateHeader.builder() \
                .field_name(field.field_title) \
                .type(field.get_field_type()) \
                .build()
            headers.append(header)
        
        request: CreateAppTableRequest = CreateAppTableRequest.builder() \
            .app_token(file.token) \
            .request_body(CreateAppTableRequestBody.builder()
                          .table(ReqTable.builder()
                                 .name(table_name)
                                 .fields(headers)
                                 .build())
                            .build()) \
                .build()
        
        response: CreateAppResponse = self.client.bitable.v1.app_table.create(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data.table_id

    def list_table(self, app_token: str):
        request: ListAppTableRequest = ListAppTableRequest.builder() \
            .app_token(app_token) \
            .build()
        
        response: ListAppTableResponse = self.client.bitable.v1.app_table.list(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    def delete_table(self, app_token: str, table_id: str):
        request: DeleteAppTableRequest = DeleteAppTableRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .build()
        
        response: DeleteAppTableResponse = self.client.bitable.v1.app_table.delete(request, self.option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table.delete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return

        # 处理业务结果
        lark.logger.info(f"client.bitable.v1.app_table.delete succeed")