#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :reinforcedynamic.py
@Description:       : 使用sqlalchemy动态创建表，并可以从数据库中表的结构直接创建其相应映射的类
@Date     :2021/03/17 15:55:57
@Author      :hotwa
@version      :2.0
'''

import datetime
from sqlalchemy import (BigInteger, Column, DateTime, Integer, MetaData, String, Table, create_engine, LargeBinary,TEXT)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper,sessionmaker
from sqlalchemy.schema import CreateTable
import os,sys,re
from icecream import ic

# 调试配置
def time_format():
    return f'{datetime.datetime.now()}|> '
ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=True)

# 创建sqlalchemy基类，使用BaseSQL.metadata.create_all可以创建继承该基类的所有创建的module类
BaseSQL = declarative_base()
# metadata = MetaData() # 初始化表的元数据定义

# module template模板 默认创建主键为Id，防止传入没有创建
class template(BaseSQL):
    __abstract__ = True  # 关键语句,定义所有数据库表对应的父类
    __table_args__ = {"extend_existing": True}  # 允许表已存在
    Id = Column(Integer, primary_key=True)

    # 需要可以自行对动态类添加返回信息
    # def __repr__(self):
    #     """__repr__ print result
    #     :return: result
    #     """
    #     return f"<table(id:{template.Id}"

class dyaddlabel(object):
    __doc__ = 'dynamic add module labels class, 动态的添加标签，主要是静态方法'

    @staticmethod
    def get_table_model_cls(cid:dict(help="tablename",type = str),
        intemplate:dict(help="normal class template") = template,
        cid_class_dict={},
        ude:dict(help="update template class __dict__") = {}
        ):
        """get_table_model_cls [创建一个module类，默认创建主键Id]
        
        [默认使用template类创建module类，在创建module类前先对template动态增加属性,！注意在使用该方法时要提前对template类进行属性添加，否则会只创建id的表]
        
        :param cid: [__tablename__]
        :type cid: [string]
        :param intemplate: [class template]
        :type intemplate: [class], defaults to template class
        :param cid_class_dict: [用来返回class的字典], defaults to {}
        :type cid_class_dict: [dict], optional
        :return: [description]
        :rtype: [type]
        """
        __setrr = {'__tablename__': cid}
        __setrr.update(ude)
        if cid not in cid_class_dict:
            cls_name = table_name = cid
            cls = type(cls_name, (intemplate, ), __setrr) # 以其他设计好的module模型创建一个无继承关系的类
            cid_class_dict[cid] = cls # 将该类存储至该字典并返回
        return cid_class_dict[cid]

    @staticmethod
    def dict_add_to_class(class_name,d):
        """dict_add_to_class [将d字典中键值对添加至class_name属性里面]
        
        [extended_summary]
        
        :param class_name: [类]
        :type class_name: [class]
        :param dict: [需要添加属性的字典]]
        :type dict: [dict]
        """
        if isinstance(d,dict):
            for k,v in d.items():
                setattr(class_name,k,v) # 动态添加方法
        else:
            raise ValueError("Invalid dictionary!", d)
        return class_name

class generate_mclass(object):
    __doc__ = '通过复制已经存在的表来生成对应的module类'

    @staticmethod
    def getModel(name, engine):
        """getModel [从已有的数据库中的表名为name的表，根据这张表的结构返回一个新的model类(表名不变)]
        
        [extended_summary]
        
        :param name: [数据库表名]
        :type name: [string]
        :param engine: [create by function create_engine,reate_engine返回的对象，指定要操作的数据库连接，from sqlalchemy import create_engine]
        :type engine: [object]
        :return: [modle class and rewirte __tablename__]
        :rtype: [modle object]
        """
        BaseSQL.metadata.reflect(engine)
        table = BaseSQL.metadata.tables[name]
        t = type(name, (object,), dict())
        mapper(t, table)
        BaseSQL.metadata.clear()
        return t

    # ----------------------------------------------------------------
    # 其他人源码未修改、测试
    @staticmethod
    def getNewModel(name, tableNam, engine):
        """copy一个表的表结构并创建新的名为name的表并返回model类
        name:数据库表名
        tableNam:copy的表表名
        engine:create_engine返回的对象，指定要操作的数据库连接，from sqlalchemy import create_engine
        """
        generate_mclass.createTableFromTable(name, tableNam, engine)
        return generate_mclass.getModel(name, engine)

    # ----------------------------------------------------------------
    # 其他人源码未修改、测试
    @staticmethod
    def createTableFromTable(name, tableNam, engine):
        """copy一个已有表的结构，并创建新的表
        """
        metadata = MetaData(engine)
        BaseSQL.metadata.reflect(engine)
        # 获取原表对象
        table = BaseSQL.metadata.tables[tableNam]
        # 获取原表建表语句
        c = str(CreateTable(table))
        print(c)
        print(tableNam, name)
        # 替换表名
        c = c.replace('"', '').replace('CREATE TABLE {}'.format(tableNam), "CREATE TABLE if not exists {}".format(name))
        print(c)
        db_conn = engine.connect()
        db_conn.execute(c)
        db_conn.close()
        BaseSQL.metadata.clear()


class database_forwards(object):
    __doc__ = 'manipulate database methods'

    def __init__(self,database_path:dict(help='database path',type=str)):
        self.path = database_path
        self.engine = create_engine(self.path, encoding="utf-8", echo=True)

    def del_existing_table(self, tableName):
        """del_existing_table [使用原生sql语句删除单个表]
        
        [可以使用循环删除多个表]
        
        :param engine: [create by function create_engine]
        :type engine: [object]
        :param tableName: [the table you want to delete]
        :type tableName: [string]
        """
        conn = self.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {tableName};')
        result = cursor.fetchall()
        ic(result)
        cursor.close()
        conn.close()

    def insert(self,new_data: dict(type=object,help="input data in obj"))-> String:
        """insert  insert a record 插入数据前要根据module类先创建相应的表，在进行操作
        Keyword Arguments:
            new_data {[type]} -- [description] (default: {object,help="input data in obj")})
        Returns:
            [String] -- [status]
        """    
        engine = self.engine
        ic("创建数据库引擎，并初始化表")
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        ic("创建session对象")
        session.add(new_data)
        ic("添加数据到session")
        session.commit()
        ic("提交数据到数据库")
        session.close()
        ic("关闭数据库连接")
        return "success"

    def insert_muti(self,new_data_list: dict(type=list,help="list of obj")) -> String:
        """insert_muti add some date in the table 插入数据前要根据module类先创建相应的表，在进行操作
        [extended_summary]
        Keyword Arguments:
            new_data_list {[type]} -- [description] (default: {list,help="list of obj")})
        Returns:
            [String] -- [status]
        """    
        engine = self.engine
        ic("创建数据库引擎，并初始化表")
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        ic("创建session对象")
        session.add_all(new_data_list)
        ic("添加[多条]数据到session")
        session.commit()
        ic("提交数据到数据库")
        session.close()
        ic("关闭数据库连接")
        return "success"

class TablenameError(Exception):
    __doc__ = 'define catch exception by hotwa'
    def __init__(self,tablename):
        self.description_tn = tablename
    def __str__(self):
        return f'sqlite3.OperationalError: near "{self.description_tn}": syntax error, please change your tablename. 请修改表名，重新导入'

def main_test():
    """
    @description : 用于单脚本测试
    ---------
    @param : 
    -------
    @Returns : 
    -------
    """
    dynamic_db_name = 'dydatabase.db' # sqlite3 file name
    sqlite3_path = 'sqlite:///' + os.path.join(sys.path[0], f'{dynamic_db_name}') + "?check_same_thread=False"
    # 使用sqlite3作为本地测试数据库
    engineLocal = create_engine(sqlite3_path, encoding="utf-8", echo=True)
    # 创建添加标签的字典dic
    dic = {
        '__tablename__':'tn', # 表名最好与类名一致，可以区分大小写
        '__doc__':'Create by hotwa template class, which is dynamic',
        'name':Column(String(255)),
        'city':Column(String(255)),
    }
    # 将字典标签添加至template类
    dyaddlabel.dict_add_to_class(class_name = template,d=dic)
    # # 查看是否添加类成功
    # try:
    #     ic(tn.__dict__)
    # except ValueError as e:
    #     ic(e)
    # 动态创建需要的类
    tn = dyaddlabel.get_table_model_cls(cid='tn') # 创建module类
    BaseSQL.metadata.create_all(bind=engineLocal, checkfirst=True)  # 创建数据表

def create_sqlite(dbname='database.db',sheetname = 'tn',path:dict(help='sqlite3 database path(abopath)',type=str) = None, dv: dict(help='dynamic add module class features',type=dict)={}):
    """create_sqlite [创建sqlite3数据库，并建立sheetname表]

    [extended_summary]

    :param dbname: [description], defaults to 'database.db'
    :type dbname: [type], optional
    :param sheetname: [description], defaults to 'tn'
    :type sheetname: [type], optional
    :param path: [description], defaults to None
    :type path: [type], optional
    :param dv: [description], defaults to {}
    :type dv: [type], optional
    :raises ValueError: [description]
    """
    if path:
        sqlite3_path = path
    else:
        sqlite3_path = 'sqlite:///' + os.path.join(sys.path[0], f'{dbname}') + "?check_same_thread=False"
    if dv == {}:
        raise ValueError('empty dict')
    engineLocal = create_engine(sqlite3_path, encoding="utf-8", echo=True)
    dyaddlabel.dict_add_to_class(class_name = template,d=dv)
    tn = dyaddlabel.get_table_model_cls(cid=f'{sheetname}') # 创建module类,表名和类名尽可能保持一致
    BaseSQL.metadata.create_all(bind=engineLocal, checkfirst=True)  # 创建数据表
    return tn

def create_tables(engine):
    BaseSQL.metadata.create_all(bind=engine, checkfirst=True)  # 创建所有继承BaseSQL类的数据表


def create_model(in__tablename: dict(help='__tablename__',type=str),ad:dict(help='model dictionary',type=dict)):
    return dyaddlabel.get_table_model_cls(cid=f'{in__tablename}')

class muti():
    """muti 针对多表构建的类
    
    [extended_summary]
    
    :return: [description]
    :rtype: [type]
    """
    @staticmethod
    def create_dict(tablename,label_list):
        dic = {
            '__tablename__':tablename, # 表名最好与类名一致，可以区分大小写
            '__doc__':'Create by hotwa template class, which is dynamic',
        }
        # label_list = muti.clear_tables(label_list)
        for i in label_list:
            if isinstance(i,tuple):
                exec(f'dic["{i[0]}"] = Column({i[1]})')
            else:
                dic[i] = Column(String(255)) # 默认至支持长度为256的字符串
        return dic

    @staticmethod
    def create_muti_moduleclass(**kwargs: dict(help="a muti json to create tables and return class",type=dict)):
        _dic = {}
        word = 'cereate ' + str(len(kwargs)) + ' class/tables'
        ic(word)
        for k,v in kwargs.items(): # 拆解字典
            ic(k,v)
            raw_dict = muti.create_dict(label_list = kwargs[k]['labels'],tablename=k) # 创建字典
            ic(raw_dict)
            exec(f'{k} = dyaddlabel.get_table_model_cls(cid=k,ude = raw_dict)') # 创建k变量值的module类
            exec(f'_dic["{k}"] = {k}') # 可以通过classname.__dict__读取可以添加的labels
        return _dic # ! 返回的是字典key为表名例如Sheet1，对应value是创建的相应对象

    @staticmethod
    def create_tables(engine,m_class:dict(help="module class")):
        m_class.metadata.create_all(bind=engine, checkfirst=True)  # 创建所有继承基类BaseSQL的数据表

    # @staticmethod  
    # def clear_tables(li):
    #     # labels 清洗
    #     lt =[]
    #     for i in li:
    #         res = re.split('\s{2,}',i) # 剔除含有多个空格的labels通过切片第一个元素
    #         if len(res) == 1:
    #             add_text = res[0].replace(' ', '_') # 对含有一个空格的labels进行下划线替换
    #         elif len(res) >= 2:
    #             add_text = res[0]
    #         lt.append(add_text)
    #     return lt



if __name__ == '__main__':
    main_test()
