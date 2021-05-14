#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :
@Description: 一对多表的测试文件
@Date     :2021/02/25 17:52:31
@Author      :hotwa
@version      :1.0
'''

from sqlalchemy import Column, Integer, String, create_engine, DateTime,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import sys, os
from sqlalchemy.orm import sessionmaker,relationship
from datetime import datetime
from icecream import ic

#base
Base = declarative_base()

#define table

# test content
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)

    addresses = relationship('Address', backref='users')

    @classmethod
    def create_engine(cls):
        # 创建数据库的引擎实例对象
        engine = create_engine('mysql+pymysql://root:hotwa3.14@47.110.124.146:33306/blog',encoding="utf-8",echo=False,pool_pre_ping=True)
        return engine


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    address = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))  

def create_init():
    # 创建数据库的引擎实例对象
    # 数据库名称：xh
    # engine = create_engine("mysql+pymysql://root:数据库密码@localhost:3306/xh",
    #                             encoding="utf-8",
    #                             echo=True)
    engine = User.create_engine()
    Base.metadata.create_all(bind=engine, checkfirst=True)  # 创建数据表
    return engine

def insert(new_data: dict(type=object,help="input data in obj"))-> String:
    """insert  insert a record
    Keyword Arguments:
        new_data {[type]} -- [description] (default: {object,help="input data in obj")})
    Returns:
        [String] -- [status]
    
    """    
    engine = create_init()
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

def insert_muti(new_data_list: dict(type=list,help="list of obj")) -> String:
    """insert_muti add some date in the table
    
    [extended_summary]
    
    
    Keyword Arguments:
        new_data_list {[type]} -- [description] (default: {list,help="list of obj")})
    
    
    Returns:
        [String] -- [status]
    
    """    
    engine = create_init()
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

# for test
def main():
    ...


if __name__ == '__main__':
    now = datetime.now()
    ic(now)
    data_test = ['1','2','3','4','5','6','7','8','9']
    onerecord = User(id = data_test[0],name = data_test[1])
    insert(onerecord)





