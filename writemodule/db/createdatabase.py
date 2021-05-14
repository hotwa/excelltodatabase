#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :createdatabase.py
@Description:       : 将xlsx转化为至相应数据库
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
import toml

#base
Base = declarative_base()

# 环境变量
path = os.getcwd()# get absolute path
cfgfilename = 'config.toml'
path_abo = os.path.join(path, cfgfilename)
cfg = toml.load(path_abo) # load configuration

# sqlite3 config
# ? 默认使用sqlite3数据库测试
sqlite3_name = 'database.db'
sqlite3_path = 'sqlite:///' + os.path.join(
        sys.path[0], f'{sqlite3_name}') + "?check_same_thread=False"

# mysql configuration
execution_options={"timeout": 100,"statement_timeout": 100,
                                    "query_timeout": 100,
                                    "execution_timeout": 100} # 超时设置
# read config file
user = cfg['mysql']['user']
password = cfg['mysql']['password']
port = cfg['mysql']['port']
database = cfg['mysql']['database']
host = cfg['mysql']['host']
pool_size = cfg['mysql']['parameters']['pool_size']
charset = cfg['mysql']['parameters']['charset']

mysqlconnect_url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'

if cfg['database']['name'] == 'mysql' or 'Mysql':
    database_path = mysqlconnect_url
elif cfg['database']['name'] == 'sqlite3' or 'sqlite':
    database_path = sqlite3_path
else:
    db = cfg['database']['name']
    raise NotImplementedError(f'{db} have not supported')

# for test
def main():
    ...


if __name__ == '__main__':
    now = datetime.now()
    ic(now)