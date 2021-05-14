#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :xlsx_base_a.py
@Description:       :抽象基类文件，专注要做的方法
@Date     :2021/01/16 10:51:13
@Author      :hotwa
@version      :1.0
'''
# ? 抽象基类方法
# ! 修改抽象基类方法后，相应的继承类要做相应的实现

from abc import ABC,abstractmethod

# abstract class parts of xlsx
# 可以把一些属性放至抽象基类，继承的类可以至专注于方法
class casheet(ABC):
    def __init__(self,filename='demo.xlsx'):
        self.__filename = filename

    @property
    def filename(self):
        return self.__filename
    
    @filename.setter
    def filename(self, value):
        self.__filename = value

    @abstractmethod
    def read_xlsx_info(self):
        ...

    @abstractmethod
    def read_sheet_lable(self):
        ...

    @abstractmethod
    def read_sheet_line(self,mode):
        ...

# class parts of mysql
class mysql_c(ABC):
    @abstractmethod
    def connet_sql():
        pass
