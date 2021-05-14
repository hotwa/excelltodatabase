#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :test_extra_pic.py
@Description:       :decode test
@Date     :2021/05/14 09:54:01
@Author      :hotwa
@version      :1.0
'''

import os,sys

# o_path = os.getcwd() # 返回当前工作目录
# sys.path.append(o_path) # 添加自己指定的搜索路径

o_path = os.getcwd() # 返回当前工作目录
sys.path.append('../') # 添加自己指定的搜索路径

try:
    from ..readmodule.xlsx_base import xlsx_base
except (ModuleNotFoundError,ImportError):
    from readmodule.xlsx_base import xlsx_base

import base64

filename = '../test.xlsx'
xlsx = xlsx_base(filename)
a = xlsx.read_row(2,read_cell_picture=True,base64c=True) # 尝试读取单元格图片并base64转ASCII同时decode #!还原时encode 然后使用base解码即可得到bytes
picstring = a[4]
picbytes = picstring.encode() # 转bytes
image_64_decode = base64.b64decode(picbytes) # 解码
with open('a.png','wb+') as f:
    f.write(image_64_decode)