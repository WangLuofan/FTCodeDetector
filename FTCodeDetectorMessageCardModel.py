# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang
#
#         # 扫描时间: scan_date_time
#         # 扫描目录: scan_project_directory
#         # 扫描扩展: scan_file_ext
#         # 扫描数量: scan_count_result
#         # 业务新增: scan_result_business
#             # 业务名称: scan_busi_name
#             # 业务总数: scan_busi_total_count
#             # 新增数量: scan_busi_new_count
#             # 待处理数量: scan_unhandle_count
#         # 扫描结果: scan_result
#             # 所属文件: scan_result_file
#             # 所在行数: scan_line_result
#             # 所属平台: scan_platform_result
#             # 负责人: scan_principal_result
#         # 扫描文件url: scan_result_sheets_url

import FTCodeDetectorConfig
from datetime import datetime

class FTCodeDetectorBusinessMessageCardModel():
    def __init__(self) -> None:
        self.scan_busi_name: str = None
        self.scan_busi_new_count: int = 0
        self.scan_busi_total_count: int = 0
        self.scan_unhandle_count: int = 0

    def payload(self) -> dict:
        payload = {
            'scan_busi_name': self.scan_busi_name if self.scan_busi_name != None else 'Unknown',
            'scan_busi_total_count': self.scan_busi_total_count if self.scan_busi_total_count != None else 0,
            'scan_busi_new_count': self.scan_busi_new_count if self.scan_busi_new_count != None else 0,
            'scan_unhandle_count': self.scan_unhandle_count if self.scan_unhandle_count != None else 0
        }

        return payload

class FTCodeDetectorScanResultMessageCardModel():
    def __init__(self) -> None:
        self.scan_result_file: str = None
        self.scan_line_result: str = None
        self.scan_platform_result: str = None
        self.scan_principal_result: str = None

    def payload(self) -> dict:
        payload = {
            'scan_result_file': self.scan_result_file if self.scan_result_file != None else 'Unknown',
            'scan_line_result': self.scan_line_result  if self.scan_line_result != None else 'Unknown',
            'scan_platform_result': self.scan_platform_result  if self.scan_platform_result != None else 'Unknown',
            'scan_principal_result': self.scan_principal_result  if self.scan_principal_result != None else 'Unknown'
        }

        return payload

class FTCodeDetectorMessageCardModel():
    def __init__(self) -> None:
        ctime = datetime.now()

        self.scan_date_time: str = '{year}-{month}-{day} {hour}:{minute}:{second}' \
                        .format(year = '%04d' % ctime.year, 
                                month = '%02d' % ctime.month, 
                                day = '%02d' % ctime.day, 
                                hour = '%02d' % ctime.hour, 
                                minute = '%02d' % ctime.minute, 
                                second = '%02d' % ctime.second)
        
        self.scan_project_directory: str = None
        self.scan_file_ext: str = None
        self.scan_count_result: int = None
        self.scan_result_business: [FTCodeDetectorBusinessMessageCardModel] = []
        self.scan_result_sheets_url: str = None
        self.scan_result_item: [FTCodeDetectorScanResultMessageCardModel] = [] 

    def payload(self) -> dict:
        scan_result_item: [] = []
        for (index, s) in enumerate(self.scan_result_item):
            if index >= 3:
                break

            scan_result_item.append(s.payload())

        scan_result_business: [] = []
        for s in self.scan_result_business:
            scan_result_business.append(s.payload())

        payload = {
            'type': 'template',
            'data': {
                'template_id': FTCodeDetectorConfig.message_card_id,
                'template_variable': {
                    'scan_date_time': self.scan_date_time,
                    'scan_project_directory': self.scan_project_directory if self.scan_project_directory != None else 'Unknown',
                    'scan_file_ext': self.scan_file_ext if self.scan_file_ext != None else 'Unknown',
                    'scan_count_result': self.scan_count_result if self.scan_count_result != None else 0,
                    'scan_result_item': scan_result_item,
                    'scan_result_business': scan_result_business,
                    'scan_result_sheets_url': self.scan_result_sheets_url
                }
            }
        }

        return payload