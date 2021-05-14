#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :extractxl.py
@Description:       : 在 F:\F\programing\auto-tools-for-researcher\excelltomysqlgithub\example> 目录下执行
@Date     :2021/05/08 10:01:41
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

if __name__ == '__main__':
    xlo = xlsx_base('../test.xlsx')
    byte = xlo.get_cell_pic('E2')
    string = xlo.get_cell_pic('E3',base64c=True)
    print(f'byte type:{type(byte)},string type:{type(string)}')