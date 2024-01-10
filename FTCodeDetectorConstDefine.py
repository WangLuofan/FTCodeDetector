# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import FTCodeDetectorConst

FTCodeDetectorConst.DEFAULT_FILE_NAME = '业务代码扫描'

FTCodeDetectorConst.FILE_DESC = '所属文件'
FTCodeDetectorConst.SOURCE_LINE_DESC = '所在行数'
FTCodeDetectorConst.PLATFORM_DESC = '所属平台'
FTCodeDetectorConst.BUSINESS_DESC = '所属业务'
FTCodeDetectorConst.DEPARTMENT_DESC = '所属部门'
FTCodeDetectorConst.CODEFRAG_DESC = '代码片段'

FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN = 'Unknown'
FTCodeDetectorConst.BUSINESS_TYPE_UNKNOWN_DESC = '未知业务'

FTCodeDetectorConst.PRINCIPAL_DESC = '负责人'

FTCodeDetectorConst.SUMMARY_BUSINESS_TYPE = 'Summary'
FTCodeDetectorConst.SUMMARY_TABLE_NAME = '汇总信息'

FTCodeDetectorConst.FIELD_TYPE_TEXT = 'text'
FTCodeDetectorConst.FIELD_TYPE_DATETIME = 'datetime'
FTCodeDetectorConst.FEILD_TYPE_SINGLE = 'single'
FTCodeDetectorConst.FIELD_TYPE_CHECKBOX = 'checkbox'
FTCodeDetectorConst.FIELD_TYPE_PERSON = 'person'

FTCodeDetectorConst.FIELD_UI_TYPE_TEXT = 'Text'
FTCodeDetectorConst.FIELD_UI_TYPE_DATETIME = 'DateTime'
FTCodeDetectorConst.FIELD_UI_TYPE_SINGLE = 'SingleSelect'
FTCodeDetectorConst.FIELD_UI_TYPE_CHECKBOX = 'Checkbox'
FTCodeDetectorConst.FIELD_UI_TYPE_PERSON = 'User'

FTCodeDetectorConst.FILE_PERM_VIEW = 'view'
FTCodeDetectorConst.FILE_PERM_EDIT = 'edit'
FTCodeDetectorConst.FILE_PERM_FULLACCESS = 'full_access'

FTCodeDetectorConst.COMMENT_BEGIN = r'/**'
FTCodeDetectorConst.START_MARCO = r'<FT_FINANCIAL_CODE_MARK_BEGIN>'
FTCodeDetectorConst.BUSINESS_MARCO = r'businessType'
FTCodeDetectorConst.PRINCIPAL_MARCO = r'principal'
FTCodeDetectorConst.END_MARCO = r'<FT_FINANCIAL_CODE_MARK_END>'
FTCodeDetectorConst.COMMENT_END = r'*/'