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
from FTCodeDetectorFtoaRequester import FTCodeDetectorFtoaRequester
from FTCodeDetectorFeiShuFile import *
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

        if len(self.directory) == 0 or len(self.ext) == 0:
            return
        
        result: [FTCodeDetectorModel] = []
        
        file_manager = FTCodeDetectorFileManager(self.directory, self.ext)
        source_files = file_manager.get_source_files()

        cpu_count = min(multiprocessing.cpu_count(), 8)
        slice = int(len(source_files) / cpu_count) + 1
        cpu_usage = int(len(source_files) / slice) + (1 if len(source_files) % slice != 0 else 0)

        threads = []
        thread_lock = threading.Lock()
        for i in range(0, cpu_usage):
            start = i * slice
            if start >= len(source_files):
                break
            files = source_files[start : start + slice]

            thread = FTCodeDetectorThreading(files, thread_lock, result)
            threads.append(thread)

        for t in threads:
            t.start()
            t.join()

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

        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.FILE_DESC, FTCodeDetectorConst.FIELD_TYPE_TEXT))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.SOURCE_LINE_DESC, FTCodeDetectorConst.FIELD_TYPE_TEXT))
        fields.append(FTCodeDetectorFeiShuBitableField(FTCodeDetectorConst.PLATFORM_DESC, FTCodeDetectorConst.FEILD_TYPE_SINGLE))
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

        del fields_dic
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

    def write(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester, file: FTCodeDetectorFeiShuBitableFile, business_model: FTCodeDetectorBusinessModel) -> bool:
        records: [AppTableRecord] = []
        for model in business_model.models:
            feishuId = self.get_feishu_id(model.principal_marco.value if model.principal_marco != None else 'Unknown')

            fields = {
                FTCodeDetectorConst.FILE_DESC: FTCodeDetectorFileManager.get_file_name(model.source_file),
                FTCodeDetectorConst.SOURCE_LINE_DESC: '{start} ~ {end}'.format(start = model.start_line, end = model.end_line),
                FTCodeDetectorConst.PLATFORM_DESC: FTCodeDetectorConfig.platform,
                FTCodeDetectorConst.BUSINESS_DESC: model.business_marco.value,
                FTCodeDetectorConst.CODEFRAG_DESC: ''.join(s for (_, s) in model.source_lines)
            }

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
                                date = datetime.strptime(marco.value, r'%Y/%m/%d')
                            except ValueError:
                                ctime = datetime.now()
                                date = datetime.strptime('{year}/{month}/{day}'.format(year = ctime.year, month = ctime.month, day = ctime.day), r'%Y/%m/%d')

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
            
            records.append(AppTableRecord.builder().fields(fields).build())

        return feiShuRequester.write(file, file.table_id[business_model.business_type], records)
    
    def add_manager_perm(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester, file: FTCodeDetectorFeiShuBitableFile):
        if FTCodeDetectorConfig.file_manager == None or len(FTCodeDetectorConfig.file_manager) <= 0:
            return
        
        for manager in FTCodeDetectorConfig.file_manager:
            feiShuRequester.add_member_perm(manager, file, FTCodeDetectorConst.FILE_PERM_EDIT)

    def update_config(self, file: FTCodeDetectorFeiShuFile, business_type: str):
        if file == None:
            return
        
        business_config = FTCodeDetectorConfig.get_business(business_type)
        business_config.update(file)

        FTCodeDetectorConfig.file_url = file.url
        FTCodeDetectorConfig.file_token = file.token

    def create_file(self, feiShuRequester: FTCodeDetectorFeiShuBitableFileRequester) -> (FTCodeDetectorFeiShuBitableFile, str):
        (file, default_table_id) = feiShuRequester.create_file(FTCodeDetectorConfig.file_name)

        if file == None:
            return None
        
        self.add_manager_perm(feiShuRequester, file)
        
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

                self.update_config(file, business_type)
            elif business_config.table_id == None:
                file.table_id[business_type] = feiShuRequester.create_table(file, business_model.business_desc, all_fields)
                business_config.update(file)
            else:
                file.update(business_config)
                feiShuRequester.create_fields_if_needed(file, file.table_id[business_type], all_fields)
        
        return file

    def send_message(self, business_dict: dict):
        extensions = ''
        for (index, ext) in enumerate(self.ext):
            if index != 0:
                extensions = extensions + '|'
            extensions += ext

        url = 'https://futu.feishu.cn/base/{bitable_token}'.format(bitable_token = FTCodeDetectorConfig.file_token)

        scan_result = []

        item_count = min(3, len(business_dict[FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE].models))
        models: [FTCodeDetectorModel] = business_dict[FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE].models

        for idx in range(0, item_count):
            model = models[idx]

            filename = FTCodeDetectorFileManager.get_file_name(model.source_file)
            scan_result.append({
                            'scan_result_file': filename,
                            'scan_line_result': '{start} ~ {end}'.format(start = model.start_line + 1, end = model.end_line + 1),
                            'scan_platform_result': FTCodeDetectorConfig.platform,
                            'scan_principle_result': '<at email={principal}@futunn.com></at>'.format(principal = model.principal_marco.value) if model.principal_marco != None and \
                                len(model.principal_marco.value) > 0 else 'Unknown'
                        })

        ctime = datetime.now()
        payload = {
            'type': 'template',
            'data': {
                'template_id': FTCodeDetectorConfig.message_card_id,
                'template_variable': {
                    'scan_date_time': '{year}-{month}-{day} {hour}:{minute}:{second}' \
                        .format(year = '%04d' % ctime.year, 
                                month = '%02d' % ctime.month, 
                                day = '%02d' % ctime.day, 
                                hour = '%02d' % ctime.hour, 
                                minute = '%02d' % ctime.minute, 
                                second = '%02d' % ctime.second),
                    'scan_project_directory': self.directory,
                    'scan_file_ext': extensions,
                    'scan_count_result': str(len(models)),
                    'scan_result': scan_result,
                    'scan_result_sheets_url': url
                }
            }
        }

        chatRequester: FTCodeDetectorFeiShuChatRequester = FTCodeDetectorFeiShuChatRequester(FTCodeDetectorConfig.FEISHU_APP_ID, FTCodeDetectorConfig.FEISHU_APP_SECRET)
        chatRequester.send_message(FTCodeDetectorConfig.chat_group, payload)

    def feishu(self, business_dict: dict) -> bool:

        if len(business_dict) <= 0:
            return True
        
        feiShuRequester = FTCodeDetectorFeiShuBitableFileRequester(FTCodeDetectorConfig.FEISHU_APP_ID, FTCodeDetectorConfig.FEISHU_APP_SECRET)
        feiShuRequester.delete_all_files()

        file: FTCodeDetectorFeiShuBitableFile = self.create_file_or_table_if_needed(feiShuRequester, business_dict)
        if file == None:
            return False
        
        for (_, business_model) in business_dict.items():
            self.write(feiShuRequester, file, business_model)

        if FTCodeDetectorConfig.message_card_id != None and len(FTCodeDetectorConfig.message_card_id) >= 0:
            self.send_message(business_dict)

        return True

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