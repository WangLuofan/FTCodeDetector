# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import sys
import threading
import multiprocessing

import FTCodeDetectorConfig

from datetime import datetime
from lark_oapi.api.bitable.v1 import *

from FTCodeDetectorModel import *
from FTCodeDetectorFtoaRequester import FTCodeDetectorFtoaRequester
from FTCodeDetectorConfigUtil import FTCodeDetectorConfigUtil
from FTCodeDetectorFeiShuFile import *
from FTCodeDetectorScanOperation import FTCodeDetectorScanOperation
from FTCodeDetectorFileManager import FTCodeDetectorFileManager
from FTCodeDetectorFeiShuBitableRequester import FTCodeDetectorFeiShuBitableRequester

result = {}

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

    def run(self):
        if self.parse_arg() == False:
            return

        if len(self.directory) == 0 or len(self.ext) == 0:
            return
        
        file_manager = FTCodeDetectorFileManager(self.directory, self.ext)
        source_files = file_manager.get_source_files()

        cpu_count = min(multiprocessing.cpu_count(), 8)
        slice = int(len(source_files) / cpu_count) + 1
        cpu_usage = int(len(source_files) / slice) + 1

        threads = []
        thread_lock = threading.Lock()
        for i in range(0, cpu_usage):
            start = i * slice
            if start >= len(source_files):
                break
            files = source_files[start : start + slice]

            thread = FTCodeDetectorScanOperation(files, thread_lock, result)
            threads.append(thread)

        for t in threads:
            t.start()
            t.join()

        return self.feishu()
    
    def file_exists(self, files: dict, token: str) -> FTCodeDetectorFeiShuBitableFile:
        if token == None or len(token) <= 0:
            return None

        for (app_token, file) in files.items():
            if token == app_token:
                return file
        return None
    
    def get_all_fields(self, models) -> [FTCodeDetectorFeiShuBitableField]:
        fields: [FTCodeDetectorFeiShuBitableField] = []
        fields_dic: dict = {}

        fields.append(FTCodeDetectorFeiShuBitableField('所属文件', 'text'))
        fields.append(FTCodeDetectorFeiShuBitableField('所在行数', 'text'))
        for model in models:
            for marco in model.user_defined:
                if marco.tag in fields_dic:
                    continue

                field: FTCodeDetectorFeiShuBitableField = FTCodeDetectorFeiShuBitableField(marco.get_desc(), marco.get_type())
                fields.append(field)

                fields_dic[marco.tag] = field

        del fields_dic
        return fields

    def write_file(self, feiShuRequester: FTCodeDetectorFeiShuBitableRequester, file: FTCodeDetectorFeiShuBitableFile, models: [FTCodeDetectorModel]):
        records: [AppTableRecord] = []
        for model in models:
            fields = {
                '所属文件': FTCodeDetectorFileManager.get_file_name(model.source_file),
                '所在行数': '{start} ~ {end}'.format(start = model.start_line + 1, end = model.end_line + 1)
            }

            for marco in model.user_defined:
                if 'type' in marco.attributes:
                    if marco.attributes['type'] == 'datetime':
                        try:
                            date = datetime.strptime(marco.value, r'%Y/%m/%d')
                        except ValueError:
                            ctime = datetime.now()
                            date = datetime.strptime('{year}/{month}/{day}'.format(year = ctime.year, month = ctime.month, day = ctime.day), r'%Y/%m/%d')

                        fields[marco.attributes['desc']] = int(date.timestamp() * 1000)
                    elif marco.attributes['type'] == 'person':
                        feiShuRequester.add_member_perm(marco.value, file, 'view')

                        user_info = FTCodeDetectorFtoaRequester.get_user_info(marco.value)
                        if user_info != None and 'feishuId' in user_info:
                            fields[marco.attributes['desc']] = [{
                                'id': user_info['feishuId']
                            }]
                        else:
                            user_info = '<at email={principal}@futunn.com>{principal}</at>'.format(principal = model.value)
                            fields[marco.attributes['desc']] = user_info
                    else:
                        fields[marco.attributes['desc']] = marco.value
            
            records.append(AppTableRecord.builder().fields(fields).build())

        feiShuRequester.write(file, records)

    def update_config(self, file: FTCodeDetectorFeiShuFile, business_type: str):
        if file == None:
            return
        
        business_config = FTCodeDetectorConfig.get_business(business_type)
        business_config.update(file)

        FTCodeDetectorConfig.file_url = file.url
        FTCodeDetectorConfig.file_token = file.token

    def update_and_write(self, feiShuRequester: FTCodeDetectorFeiShuBitableRequester):
        for (business_type, models) in result.items():
            business_config = FTCodeDetectorConfig.get_business(business_type)

            file: FTCodeDetectorFeiShuBitableFile = self.file_exists(feiShuRequester.list_files(), FTCodeDetectorConfig.file_token)
            if file == None:
                file = feiShuRequester.create_file('业务代码统计')
                if file == None:
                    return False
                
                all_fields = self.get_all_fields(models)

                default_table_id = file.table_id
                file.table_id = feiShuRequester.create_table(file, business_type, all_fields)

                feiShuRequester.delete_table(file.token, default_table_id)

                self.update_config(file, business_type)
            elif business_config.table_id == None:
                all_fields = self.get_all_fields(models)
                file.table_id = feiShuRequester.create_table(file, business_type, all_fields)

                business_config.update(file)
            else:
                file.update(business_config)
            
            self.write_file(feiShuRequester, file, models)

    def feishu(self) -> bool:

        if len(result) <= 0:
            return True
        
        feiShuRequester = FTCodeDetectorFeiShuBitableRequester(FTCodeDetectorConfig.FEISHU_APP_ID, FTCodeDetectorConfig.FEISHU_APP_SECRET)
        self.update_and_write(feiShuRequester)

        return True

    def print(self):
        if len(result) <= 0:
            return 
        
        print('Total Record Count: ', len(result))
        print()

        for (business_type, models) in result.items():
            print('business_type:', business_type)
            for model in models:
                print('    *******************************')

            if model.source_file != None:
                print('    {0:16}{1}'.format('Source:', model.source_file))

            for marco in model.user_defined:
                if marco.tag != None and len(marco.tag) > 0 and marco.value != None:
                    print('    {0:16}{1}'.format('%s:' % marco.tag, marco.value))

            if model.start_line != -1:
                print('    {0:16}{1}'.format('Start Line:', model.start_line + 1))

            if model.end_line != -1:
                print('    {0:16}{1}'.format('End Line:', model.end_line + 1))

            print('    *******************************')

            if len(model.source_lines) > 0:
                for line in model.source_lines:
                    print('    ', line[0] + 1, '    ', line[1])
            
            print('    *******************************')
            print()
            

if __name__ == '__main__':
    codeDetector: FTCodeDetector = FTCodeDetector()

    if codeDetector.run():
        codeDetector.print()

    del result
    FTCodeDetectorConfigUtil.save_config()