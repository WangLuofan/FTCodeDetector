# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import sys
import threading
import multiprocessing

import FTCodeDetectorConst
import FTCodeDetectorConfig

from datetime import datetime
from lark_oapi.api.bitable.v1 import *

from FTCodeDetectorModel import *
from FTCodeDetectorGitHeper import *
from FTCodeDetectorFtoaRequester import FTCodeDetectorFtoaRequester
from FTCodeDetectorFeiShuFile import *
from FTCodeDetectorProgressBar import *
from FTCodeDetectorMessageCardModel import FTCodeDetectorBusinessMessageCardModel, FTCodeDetectorMessageCardModel, FTCodeDetectorScanResultMessageCardModel
from FTCodeDetectorThreading import FTCodeDetectorThreading
from FTCodeDetectorFileManager import FTCodeDetectorFileManager
from FTCodeDetectorFeiShuChatRequester import FTCodeDetectorFeiShuChatRequester
from FTCodeDetectorFeiShuBitableFileRequester import FTCodeDetectorFeiShuBitableFileRequester

class FTCodeDetector():
    def __init__(self):
        self.ext = ['.h', '.hpp', '.c', '.cxx', '.cpp', '.cc', '.m', '.mm', '.swift']

    def print_usage(self):
        print()
        print('*******************************')
        print('Usage: python ./FTCodeDetector \{arguments\}')
        print('--clean:', 'Clean all Project Files. BE CAREFUL')
        print('-d:', 'Specify The Project Directory')
        print('-e:', 'Specify The Files Extensions to Detect, \',\' for split')
        print('*******************************')
        print()

    def parse_arg(self) -> bool:
        if len(sys.argv) <= 1:
            self.print_usage()
            return False
        
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == '-d':
                if i + 1 < len(sys.argv):
                    self.directory = sys.argv[i + 1]
                else:
                    print('Must Specify Project Directory When \'-d\' Specified')
                    return False
            
            if sys.argv[i] == '-e':
                if i + 1 < len(sys.argv):
                    exts = sys.argv[i + 1].split(',')
                    if exts != None:
                        self.ext = exts
                else:
                    print('Must Specify File Extensions When \'-e\' Specified')
                    return False
                
        return True

    def run(self) -> dict:

        if self.parse_arg() == False:
            return

        self.do_clean_if_needed()

        if len(self.directory) == 0 or len(self.ext) == 0:
            return
        
        result: [FTCodeDetectorModel] = []
        
        file_manager = FTCodeDetectorFileManager(self.directory, self.ext)
        source_files = file_manager.get_source_files()

        cpu_count = min(multiprocessing.cpu_count(), 8)
        slice = int(len(source_files) / cpu_count) + 1
        cpu_usage = int(len(source_files) / slice) + (1 if len(source_files) % slice != 0 else 0)

        progress: FTCodeDetectorProgressBar = FTCodeDetectorProgressBar(maxval = len(source_files))
        progress_lock = threading.Lock()

        threads = []
        thread_lock = threading.Lock()
        for i in range(0, cpu_usage):
            start = i * slice
            if start >= len(source_files):
                break
            files = source_files[start : start + slice]

            thread = FTCodeDetectorThreading(files, thread_lock, result, lambda :(progress_lock.acquire(), progress.update(), progress_lock.release()))
            threads.append(thread)

        for t in threads:
            t.start()
            t.join()

        progress.finish()

        business_dict = self.do_categorize(result)
        self.feishu(business_dict)

        return business_dict
    
    def file_exists(self, files: dict, token: str) -> FTCodeDetectorFeiShuBitableFile:
        if token == None or len(token) <= 0:
            return None

        for (app_token, file) in files.items():
            if token == app_token:
                return file
        
        return None
    
    def get_all_fields(self, business_model) -> [FTCodeDetectorFeiShuBitableField]:
        fields: [FTCodeDetectorFeiShuBitableField] = []
        fields_dic: dict = {}

        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.FILE_DESC, FTCodeDetectorConst.FIELD_TYPE_LINK))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.SOURCE_LINE_DESC, FTCodeDetectorConst.FIELD_TYPE_TEXT))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.PLATFORM_DESC, FTCodeDetectorConst.FEILD_TYPE_SINGLE))
        # fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.DEPARTMENT_DESC, FTCodeDetectorConst.FEILD_TYPE_SINGLE))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.BUSINESS_DESC, FTCodeDetectorConst.FEILD_TYPE_SINGLE))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.PRINCIPAL_DESC, FTCodeDetectorConst.FIELD_TYPE_PERSON))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.CODEFRAG_DESC, FTCodeDetectorConst.FIELD_TYPE_TEXT))

        if business_model.business_type != FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE:
            for model in business_model.models:
                for marco in model.user_defined:
                    if marco.tag in fields_dic:
                        continue

                    field: FTCodeDetectorFeiShuBitableField = FTCodeDetectorFeiShuBitableField(marco.get_desc(), marco.get_type())
                    fields.append(field)

                    fields_dic[marco.tag] = field

        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.DIGEST_DESC, FTCodeDetectorConst.FIELD_TYPE_TEXT))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.HANDLED_DESC, FTCodeDetectorConst.FEILD_TYPE_SINGLE, [
            FTCodeDetectorFeiShuBitableFieldOption(FTCodeDetectorConst.HANDLED_RESULT_NONE),
            FTCodeDetectorFeiShuBitableFieldOption(FTCodeDetectorConst.HANDLED_RESULT_NO),
            FTCodeDetectorFeiShuBitableFieldOption(FTCodeDetectorConst.HANDLED_RESULT_YES),
            FTCodeDetectorFeiShuBitableFieldOption(FTCodeDetectorConst.HANDLED_RESULT_IN)
        ]))

        return fields

    def is_manager(self, nick: str) -> bool:
        if FTCodeDetectorConfig.file_manager == None or len(FTCodeDetectorConfig.file_manager) <= 0:
            return False

        for manager in FTCodeDetectorConfig.file_manager:
            if nick.lower() == manager.lower():
                return True
        
        return False
    
    def get_feishu_id(self, nick: str) -> str:
        user_info = FTCodeDetectorFtoaRequester.get_user_info(nick)

        if user_info == None or 'feishuId' not in user_info:
            return None
        
        return user_info['feishuId']
    
    def get_user_department(self, nick: str) -> str:

        department_info = FTCodeDetectorFtoaRequester.get_user_department(nick)

        if department_info == None or len(department_info) <= 0:
            return None
        
        department: dict = department_info[0]
        if 'department' not in department and 'name' not in department['department']:
            return None

        return department['department']['name']

    def append_or_update_records(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester, \
                                 file: FTCodeDetectorFeiShuBitableFile, business_model: FTCodeDetectorBusinessModel, \
                                    messageCardModel: FTCodeDetectorMessageCardModel) -> bool:

        all_records: [FTCodeDetectorFeiShuBitableRecord] = feiShuRequester.list_records(file, file.table_id[business_model.business_type])

        all_records_dict: {str: FTCodeDetectorFeiShuBitableRecord} = {}
        records_deleted_dict: {str: FTCodeDetectorFeiShuBitableRecord} = {}

        unhandled_count: int = 0
        if all_records != None and len(all_records) > 0:
            for item in all_records:
                all_records_dict[item.hexdigest] = item
                records_deleted_dict[item.hexdigest] = item

        recordsToAppend: [AppTableRecord] = []
        recordsToUpdate: [FTCodeDetectorFeiShuBitableRecord] = []

        git_version = FTCodeDetectorGitHelper.git_version()

        for model in business_model.models:

            fields = {
                FTCodeDetectorConst.SOURCE_LINE_DESC: '{start} ~ {end}'.format(start = model.start_line, end = model.end_line),
                FTCodeDetectorConst.PLATFORM_DESC: FTCodeDetectorConfig.platform,
                FTCodeDetectorConst.BUSINESS_DESC: model.business_marco.value,
                FTCodeDetectorConst.CODEFRAG_DESC: ''.join(s[1] for s in model.source_lines),
                FTCodeDetectorConst.DIGEST_DESC: model.hexdigest,
            }

            if git_version != None and len(git_version) > 0:
                git_url: str = FTCodeDetectorGitHelper.get_file_url(model.abs_path)
                fields[FTCodeDetectorConst.FILE_DESC] = {
                    'text': model.source_file,
                    'link': git_url if git_url != None and len(git_url) > 0 else ''
                }
            else:
                fields[FTCodeDetectorConst.FILE_DESC] = {
                    'text': model.source_file,
                    'link': ''
                }

            fields[FTCodeDetectorConst.HANDLED_DESC] = FTCodeDetectorConst.HANDLED_RESULT_NONE
            if model.principal_marco != None and model.principal_marco.value != None:
                fields[FTCodeDetectorConst.HANDLED_DESC] = FTCodeDetectorConst.HANDLED_RESULT_NO
                unhandled_count += 1

                # department_name: str = self.get_user_department(model.principal_marco.value)
                # if department_name != None and len(department_name) > 0:
                #     fields[FTCodeDetectorConst.DEPARTMENT_DESC] = department_name
                # elif 'module' in model.user_defined and model.user_defined['module'] != None:
                #     fields[FTCodeDetectorConst.DEPARTMENT_DESC] = FTCodeDetectorConfig.Platform + model.user_defined['module'].value

                feishuId = self.get_feishu_id(model.principal_marco.value)
                if feishuId != None:
                    fields[FTCodeDetectorConst.PRINCIPAL_DESC] = [{
                        'id': feishuId
                    }]

                    if self.is_manager(feishuId) == False:
                        feiShuRequester.add_member_perm(feishuId, file, FTCodeDetectorConst.FILE_PERM_VIEW)

            if business_model.business_type != FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE:
                for marco in model.user_defined:
                    if marco.tag == FTCodeDetectorConst.BUSINESS_MARCO:
                        fields[FTCodeDetectorConst.BUSINESS_DESC] = marco.value

                    elif 'type' in marco.attributes:
                        if marco.attributes['type'] == FTCodeDetectorConst.FIELD_TYPE_DATETIME:
                            try:
                                date = datetime.datetime.strptime(marco.value, r'%Y/%m/%d')
                            except ValueError:
                                ctime = datetime.datetime.now()
                                date = datetime.datetime.strptime('{year}/{month}/{day}'.format(year = ctime.year, month = ctime.month, day = ctime.day), r'%Y/%m/%d')

                            fields[marco.attributes['desc']] = int(date.timestamp() * 1000)

                        elif marco.attributes['type'] == FTCodeDetectorConst.FIELD_TYPE_PERSON:
                            feishuId = self.get_feishu_id(marco.value)

                            if self.is_manager(marco.value) == False:
                                feiShuRequester.add_member_perm(marco.value, file, FTCodeDetectorConst.FILE_PERM_VIEW)

                            if feishuId != None:
                                fields[marco.attributes['desc']] = [{
                                    'id': feishuId if feishuId != None and len(feishuId) > 0 else 'Unknown'
                                }]

                        elif marco.attributes['type'] == FTCodeDetectorConst.FIELD_TYPE_CHECKBOX:
                            if marco.value.lower() == 'true':
                                fields[marco.attributes['desc']] = True

                            else:
                                fields[marco.attributes['desc']] = False

                        else:
                            fields[marco.attributes['desc']] = marco.value
            
            if model.hexdigest in all_records_dict:
                if all_records_dict[model.hexdigest] != fields:
                    all_records_dict[model.hexdigest].fields = fields
                    recordsToUpdate.append(all_records_dict[model.hexdigest])

                if model.hexdigest in records_deleted_dict:
                    records_deleted_dict.pop(model.hexdigest)
            else:
                recordsToAppend.append(AppTableRecord.builder().fields(fields).build())

        for (_, item) in records_deleted_dict.items(): 
            item.fields = {FTCodeDetectorConst.HANDLED_DESC : FTCodeDetectorConst.HANDLED_RESULT_YES}
            recordsToUpdate.append(item)

        result: bool = False 
        if len(recordsToAppend) > 0:
            feiShuRequester.append_records(file, file.table_id[business_model.business_type], recordsToAppend)
            result = True

        if len(recordsToUpdate) > 0:
            feiShuRequester.update_records(file, file.table_id[business_model.business_type], recordsToUpdate)
            result = result or True

        if business_model.business_type != FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE:
            busiMessageCardModel: FTCodeDetectorBusinessMessageCardModel = FTCodeDetectorBusinessMessageCardModel()
            busiMessageCardModel.scan_busi_name = business_model.business_desc
            busiMessageCardModel.scan_busi_total_count = len(business_model.models if business_model.models != None else [])
            busiMessageCardModel.scan_busi_new_count = len(recordsToAppend)
            busiMessageCardModel.scan_unhandle_count = unhandled_count

            messageCardModel.scan_result_business.append(busiMessageCardModel)

        return result
    
    def add_manager_perm(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester, file: FTCodeDetectorFeiShuBitableFile):
        if FTCodeDetectorConfig.file_manager == None or len(FTCodeDetectorConfig.file_manager) <= 0:
            return
        
        for manager in FTCodeDetectorConfig.file_manager:
            feiShuRequester.add_member_perm(manager, file, FTCodeDetectorConst.FILE_PERM_FULLACCESS)

    def update_config(self, file: FTCodeDetectorFeiShuFile, business_model: FTCodeDetectorBusinessModel):
        if file == None or business_model == None:
            return
        
        business_config = FTCodeDetectorConfig.get_business(business_model.business_type)
        business_config.business_desc = business_model.business_desc
        
        business_config.update(file)

        FTCodeDetectorConfig.file_url = file.url
        FTCodeDetectorConfig.file_token = file.token

    def create_file(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester) -> (FTCodeDetectorFeiShuBitableFile, str):
        (file, default_table_id) = feiShuRequester.create_file(FTCodeDetectorConfig.file_name)

        if file == None:
            return None
                
        return (file, default_table_id)

    def create_file_or_table_if_needed(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester, business_dict: dict) -> FTCodeDetectorFeiShuBitableFile:
        all_files = feiShuRequester.list_files()
        for (business_type, business_model) in business_dict.items():
            business_config = FTCodeDetectorConfig.get_business(business_type)

            all_fields: [FTCodeDetectorFeiShuBitableField] = self.get_all_fields(business_model)
            file: FTCodeDetectorFeiShuBitableFile = self.file_exists(all_files, FTCodeDetectorConfig.file_token)

            if file == None:
                (file, default_table_id) = self.create_file(feiShuRequester)
                all_files[file.token] = file

                file.table_id[business_type] = feiShuRequester.create_table(file, business_model.business_desc, all_fields)
                feiShuRequester.delete_table(file.token, default_table_id)

                self.update_config(file, business_model)

            elif business_config.table_id == None:
                file.table_id[business_type] = feiShuRequester.create_table(file, business_model.business_desc, all_fields)
                business_config.update(file)

            else:
                file.update(business_config)
                feiShuRequester.create_fields_if_needed(file, file.table_id[business_type], all_fields)
        
        return file

    def send_message(self, messageCardModel: FTCodeDetectorMessageCardModel):
        if messageCardModel == None:
            return

        chatRequester: FTCodeDetectorFeiShuChatRequester = FTCodeDetectorFeiShuChatRequester(FTCodeDetectorConfig.FEISHU_APP_ID, FTCodeDetectorConfig.FEISHU_APP_SECRET)
        chatRequester.send_message(FTCodeDetectorConfig.chat_group, messageCardModel.payload())

    def feishu(self, business_dict: dict) -> bool:

        if len(business_dict) <= 0:
            return True

        feiShuRequester = FTCodeDetectorFeiShuBitableFileRequester(FTCodeDetectorConfig.FEISHU_APP_ID, FTCodeDetectorConfig.FEISHU_APP_SECRET)

        file: FTCodeDetectorFeiShuBitableFile = self.create_file_or_table_if_needed(feiShuRequester, business_dict)
        if file == None:
            return False

        self.add_manager_perm(feiShuRequester, file)

        messageCardModel: FTCodeDetectorMessageCardModel = FTCodeDetectorMessageCardModel()
        messageCardModel.scan_project_directory = self.directory
        messageCardModel.scan_file_ext = ','.join(self.ext)
        
        for (_, business_model) in business_dict.items():
            self.append_or_update_records(feiShuRequester, file, business_model, messageCardModel)

        models: [FTCodeDetectorModel] = business_dict[FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE].models

        messageCardModel.scan_count_result = len(models if models != None else [])
        messageCardModel.scan_result_sheets_url = 'https://futu.feishu.cn/base/{bitable_token}'. \
            format(bitable_token = FTCodeDetectorConfig.file_token)
        
        for model in models:
            scanResultModel: FTCodeDetectorScanResultMessageCardModel = FTCodeDetectorScanResultMessageCardModel()
            scanResultModel.scan_result_file = model.source_file
            scanResultModel.scan_line_result = '{start} ~ {end}'.format(start = model.start_line + 1, end = model.end_line + 1)
            scanResultModel.scan_platform_result = FTCodeDetectorConfig.platform
            scanResultModel.scan_principal_result = '<at email={principal}@futunn.com></at>'.format(principal = model.principal_marco.value) if model.principal_marco != None and \
                                 len(model.principal_marco.value) > 0 else 'Unknown'
            
            messageCardModel.scan_result_item.append(scanResultModel)

        if FTCodeDetectorConfig.message_card_id != None and len(FTCodeDetectorConfig.message_card_id) >= 0:
            self.send_message(messageCardModel)

        return True

    def do_clean_if_needed(self):
        if '--clean' not in sys.argv:
            return
        
        feiShuRequester = FTCodeDetectorFeiShuBitableFileRequester(FTCodeDetectorConfig.FEISHU_APP_ID, FTCodeDetectorConfig.FEISHU_APP_SECRET)
        feiShuRequester.delete_all_files()

        FTCodeDetectorConfig.restore_config()
        FTCodeDetectorConfig.load_config()

    def print(self, business_dict: dict):
        if len(business_dict) <= 0:
            return 
        
        print('Total Record Count: ', len(business_dict))
        print()

        for (_, business_model) in business_dict.items():
            for model in business_model.models:
                print('    *******************************')

                if FTCodeDetectorConfig.platform != None:
                    print('    {0:16}{1}'.format('Platform:', FTCodeDetectorConfig.platform))

                if business_model.business_type != None:
                    print('    {0:16}{1}'.format('BusinessType:', business_model.business_desc))

                if model.source_file != None:
                    print('    {0:16}{1}'.format('Source:', model.source_file))

                for marco in model.user_defined:
                    if marco.tag != None and len(marco.tag) > 0 and marco.value != None:
                        print('    {0:16}{1}'.format('%s:' % marco.tag, marco.value))

                if model.start_line != -1:
                    print('    {0:16}{1}'.format('Start Line:', model.start_line))

                if model.end_line != -1:
                    print('    {0:16}{1}'.format('End Line:', model.end_line))

                if model.principal_marco != None:
                    print('    {0:16}{1}'.format('Principal:', model.principal_marco.value))

                print('    *******************************')

                if len(model.source_lines) > 0:
                    for line in model.source_lines:
                        print('    ', line[0], '    ', line[1])
                
                print('    *******************************')
                print()

    def do_categorize(self, result: [FTCodeDetectorModel]) -> dict:
        business_dict: dict = {}

        for (business_type, business_config) in FTCodeDetectorConfig.business.items():
            business_dict[business_type] = FTCodeDetectorBusinessModel(business_type, business_config.business_desc)

        for item in result:
            if item.business_marco == None:
                item.business_marco = FTCodeDetectorMarco(FTCodeDetectorConst.BUSINESS_MARCO)
                item.business_marco.update_desc(FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN_DESC)
                item.business_marco.update_type(FTCodeDetectorConst.FEILD_TYPE_SINGLE)
                item.business_marco.value = FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN

            if item.business_marco.value not in business_dict:
                business_dict[item.business_marco.value] = FTCodeDetectorBusinessModel(item.business_marco.value, item.business_marco.attributes['desc'])

            business_dict[item.business_marco.value].append_model(item)

        business_dict[FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE] = FTCodeDetectorBusinessModel(FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE, FTCodeDetectorConst.SUMMARY_TABLE_NAME, result)
        return business_dict


if __name__ == '__main__':
    codeDetector: FTCodeDetector = FTCodeDetector()

    codeDetector.print(codeDetector.run())
    FTCodeDetectorConfig.save_config()