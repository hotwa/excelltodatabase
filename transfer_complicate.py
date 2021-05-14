#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file        :transfer.py
@Description:       : 入口文件，将excell文件转入相应的数据库
@Date     :2021/03/18 19:52:56
@Author      :hotwa
@version      :2.0
'''

import sys,os,re,sqlite3
from sqlalchemy import (ForeignKey,BigInteger, Column, DateTime, Integer, MetaData, String, Table, create_engine, Text,Float,DECIMAL,Date,DateTime,Time,Enum) # import some types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.sql.expression import label
import toml
try:
    from .readmodule.xlsx_base import xlsx_base
except (ModuleNotFoundError,ImportError):
    from readmodule.xlsx_base import xlsx_base
from icecream import ic
try:
    from .writemodule.db.reinforcedynamic import muti,database_forwards,dyaddlabel,template,create_sqlite,TablenameError,create_model,create_tables
except (ModuleNotFoundError,ImportError):
    from writemodule.db.reinforcedynamic import muti,database_forwards,dyaddlabel,template,create_sqlite,TablenameError,create_model,create_tables

# init data
try:
    filename = sys.argv[1]
except:
    filename = './v3_20210330remove_empty.xlsx'
path = os.getcwd()# get absolute path
excellfile = os.path.join(path, filename.replace('./',''))

# 开发者模式
mode = 'production'

# 环境变量
cfgfilename = 'config.toml' if (mode == 'production') else 'configdev.toml'
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
database_string = cfg['database']['name']

mysqlconnect_url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'

if database_string == 'mysql' or database_string == 'Mysql' or database_string == 'MYSQL':
    database_path = mysqlconnect_url
elif database_string == 'sqlite3' or database_string == 'sqlite':
    database_path = sqlite3_path
else:
    raise NotImplementedError(f'{database_string} have not supported')

def get_labels(xlsx:dict(help='object',type=object)):
    """get_labels [获取第一行或者第一列的标签，并返回列表，并对列表中的空格转化为下划线，过长空格节选部分参数作为labels]
    
    [extended_summary]
    
    :param excellfile: [需要转化的excell文件的绝对路径]
    :type excellfile: [string,path]
    """
    llist = xlsx.read_sheet_lable() # sheet_mode = col 可以以列读取
    lt =[]
    for i in llist:
        res = re.split('\s{2,}',i) # 剔除含有多个空格的labels通过切片第一个元素
        if len(res) == 1:
            add_text = res[0].replace(' ', '_') # 对含有一个空格的labels进行下划线替换
        elif len(res) >= 2:
            add_text = res[0]
        lt.append(add_text)
    return lt

def create_dict(tablename,label_list,advanced_dic = dict()):
    dic = {
        '__tablename__':tablename, # 表名最好与类名一致，可以区分大小写
        '__doc__':'Create by hotwa template class, which is dynamic',
    }
    for i in label_list:
        dic[i] = Column(String(255)) # 默认至支持长度为256的字符串
    if advanced_dic: 
        for k,v in advanced_dic.items():
            dic[k] = v # 按照字典字符串添加类型
    return dic

def insert_data_to_db(cursor_link,xlsx_data_list):
    try:
        cursor_link.insert_muti(xlsx_data_list) # cursor_link.insert(cclass(Id = {}
    except SyntaxError:
        raise IndexError('Label to repeat,存在同名标签，修改标签后导入！')

def create_eval_stentence(sentence,id,label_list: dict(help="a row data")):
    label_list = [i[0] if isinstance(i,tuple) else i for i in label_list]
    # print(sentence.format(id,*label_list))
    return sentence.format(id,*label_list)

# "Id", "Number", "Reversible    Y/N", "Name", "Residue", "Leaving Group", "SMILES", "Binding ID", "Example"
def add_braces(labels,string):
    # add_string = ',{}={}'
    for i in labels:
        string = string + ',{}='.format(i) + '{}'
    string = string + ')' # cursor_link.insert(cclass(Id = {}, {}={}))
    # print(string)
    return string
    
def create_muti_moduleclass(**kwargs: dict(help="a muti json to create tables and return class",type=dict)):
    __dic = dict()
    word = 'cereate' + len(kwargs) + 'class/tables'
    ic(word)
    for k,v in kwargs.items(): # 拆解字典
        raw_dict = create_dict(tablename=k,advanced_dic = v) # 创建字典
        exec(f'{k} = create_model(in__tablename=k,ad = raw_dict)') # 创建k变量值的module类
        exec(f'__dic[{k}] = {v}') # 可以通过classname.__dict__读取可以添加的labels
    return __dic
        
def last_handle(i):
    # 对最后example不规范的\n等数据进行强制更改为分隔符|
    _a=i.split()
    s=''
    for i in _a:
        s = s +'|'+ i
    return s

def get_all_data(xlsx:object,line_counts:int)->list:
    __xlsx_all_data_list = []
    for i in range(line_counts)[1:]: # 跳过第一行labels
        _l = xlsx.read_row(i,read_cell_picture=True,base64c=True,pic_column=['E','G','K'])
        if _l: __l = clear_line_data(_l)
        __xlsx_all_data_list.append(__l)
    return __xlsx_all_data_list

def clear_line_data(a):
    a_last = [last_handle(i) for i in a[11:] if i] # 对空格等不规范制表符全部使用哪个|替换，还原时需要注意
    a_last_str = str(a_last) # 使用exec语句进行还原
    a_start = a[:11]
    a_start.append(a_last_str)
    a = [i if i else 'empty' for i in a_start]
    return a

def main1():
    # 原始数据强制上传，不顾及合理性与规范性单表
    print(f'导入数据库{excellfile}')
    xlsx = xlsx_base(excellfile)
    cinfos = xlsx.xlsx_sheets_info # 显示当前文件结构
    # 0. 初始化数据 生成
    dict_all = {
        cinfos[0][1] : { # key 作为表名和类名
            'Id' : Column(Integer, primary_key=True),
            # 特殊的类型放在labels上，此处之下，无需在labels在次传入
            'labels' : [] # 从xlsx中读取
        }
    }
    # 1.从excell读取labels 存入dict
    ic(xlsx.current_sheet_num) # 当前选中表的导入
    for li in cinfos:
        xlsx.current_sheet_name = li[1]
        l = xlsx.read_sheet_lable()
        dict_all[li[1]]['labels'] = l
    # 1.1 对labels 指定特定的sqlalchemy特定类型(元组) # ! 单表处理
    labl = dict_all[cinfos[0][1]]['labels']
    # for i,j in enumerate(labl):
    #     if j == 'Warhead':
    #         labl[i] = (j,'LargeBinary')
    #     if j == 'Mechanism_or_End_product':
    #         labl[i] = (j,'LargeBinary')
    #     if j == 'Leaving_Group2':
    #         labl[i] = (j,'LargeBinary')
    dict_all[cinfos[0][1]]['labels'] = labl
    # 2.创建多重联结表的module类，以字典返回 需要几个类可自己创建几个按照顺序创建，先创建低级表
    mudule_class = muti.create_muti_moduleclass(**dict_all)
    # ic(dict_all)
    # 3.创建数据表
    Localengine = create_engine(database_path, encoding="utf-8", echo=True)
    # 根据类一个创建table
    # for k,v in mudule_class.items():
        # v.metadata.create_all(bind=Localengine, checkfirst=True)
    # 一次性创建所有列表
    create_tables(engine=Localengine)
    # 4.插入数据
    dbinsert = database_forwards(database_path)
    # 4.1 创建类 
    mudule_class = muti.create_muti_moduleclass(**dict_all) # 创建module类 # ! 返回的是字典key为表名例如Sheet1，对应value是创建的相应对象
    cclass = mudule_class[li[1]] # 得到创建的mapping类对象
    # 4.2 读取xlsx中的行数据
    info = xlsx.xlsx_sheets_info
    # insert_list = []
    insert_list_all= []
    xlsx_data_list = []
    for i in range(info[0][2]):
        lll = xlsx.read_row(row_num = i + 1,read_cell_picture=True,pic_column=['E','G','K'],base64c=True)
        if lll:
            # 处理最后一坨数据
            num_index = l.index('Example_Pro_DOI_PDB') # 获取合并cell初始位置
            lab = lll[:num_index]
            la = lll[num_index:] # slice [example] all cells
            lal = [str(i).replace('\n', '|') for i in la if i] # 回车处理严禁单元格出现\n异常处理机器麻烦
            example_data=';'.join(lal)
            lab.append(example_data)
            insert_list_all.append(lab)
        pre_string = 'cclass(Id = {}'
        l=[i[0] if isinstance(i,tuple) else i for i in l]
        no_data_sentence =  add_braces(labels=l,string = pre_string)
        # print(no_data_sentence,'11')
        # 4.3 将行数据创建至类实例并插入至总列表
        oneline_data = lab
        oneline_data = ['"'+str(i)+'"' for i in oneline_data]
        s_t = create_eval_stentence(no_data_sentence,i,oneline_data)
        # dbinsert.insert(eval(s_t))# 单条插入
        xlsx_data_list.append(eval(s_t))
    insert_data_to_db(dbinsert,xlsx_data_list)

def main2():
    # ! 原始拆分郑强整理的Example数据，将其整理为两个表，多表模式，放弃，后期有需要在继续编写本函数
    xlsx = xlsx_base(excellfile)
    # 高级模式
    # 0. 初始化数据 生成
    dict_all = {
        'warhead' : { # key 作为表名和类名
            'Id' : Column(Integer, primary_key=True),
            # 特殊的类型放在labels上，此处之下，无需在labels在次传入
            'labels' : [] # 从xlsx中读取
        },
        'paperlist' : {
            'Id' : Column(Integer, primary_key=True),
            'Warhead_id' : Column(Integer, ForeignKey('warhead.Id')), # 外键关联到warhead的Id上
            'warhead' : relationship('warhead',backref='paper_of_warhead'), #允许你可以在paperlist表里通过paper_of_warhead字段反查warhead所有数据
            'labels' : [] # 从xlsx中读取
        }
    }
    # 1.从excell读取labels 存入dict
    cinfos = xlsx.xlsx_sheets_info # 显示当前文件结构
    ic(xlsx.current_sheet_num) # 当前选中表的导入
    for li in cinfos:
        xlsx.current_sheet_name = li[1]
        l = xlsx.read_sheet_lable()
        dict_all[li[1]]['labels'] = l
    # 2.创建多重联结表的module类，以字典返回 需要几个类可自己创建几个按照顺序创建，先创建低级表
    mudule_class = muti.create_muti_moduleclass(**dict_all)
    # ic(dict_all)
    # 3.创建数据表
    Localengine = create_engine(database_path, encoding="utf-8", echo=True)
    # 根据类一个创建table
    # for k,v in mudule_class.items():
    #     v.metadata.create_all(bind=Localengine, checkfirst=True)
    # 一次性创建所有列表
    create_tables(engine=Localengine)
    # 4.写入数据库
    

# the script entry
if __name__ == '__main__':
    # 原始数据强制上传，不顾及合理性与规范性单表
    print(f'导入数据库{excellfile}')
    xlsx = xlsx_base(excellfile)
    cinfos = xlsx.xlsx_sheets_info # 显示当前文件结构
    # 0. 初始化数据 生成
    dict_all = {
        cinfos[0][1] : { # key 作为表名和类名
            'Id' : Column(Integer, primary_key=True),
            # 特殊的类型放在labels上，此处之下，无需在labels在次传入
            'labels' : [] # 从xlsx中读取
        }
    }
    # 1.从excell读取labels 存入dict
    # ic(xlsx.current_sheet_num) # 当前选中表的导入
    for li in cinfos:
        xlsx.current_sheet_name = li[1]
        l = xlsx.read_sheet_lable()
        dict_all[li[1]]['labels'] = l
    # 1.1 对labels 指定特定的sqlalchemy特定类型(元组) # ! 单表处理
    labl = dict_all[cinfos[0][1]]['labels']
    for i,j in enumerate(labl): # 对特殊的列含有图片使用长文本进行导入，其余则使用默认string(255)
        if j == 'Warhead':
            labl[i] = (j,'LONGTEXT')
        if j == 'Mechanism_or_End_product':
            labl[i] = (j,'LONGTEXT')
        if j == 'Leaving_Group2':
            labl[i] = (j,'LONGTEXT')
        if j == 'Example_Pro_DOI_PDB':
            labl[i] = (j,'TEXT')
    dict_all[cinfos[0][1]]['labels'] = labl
    # 2.创建多重联结表的module类，以字典返回 需要几个类可自己创建几个按照顺序创建，先创建低级表
    mudule_class = muti.create_muti_moduleclass(**dict_all) # 创建module类 # ! 返回的是字典key为表名例如Sheet1，对应value是创建的相应对象
    # ic(dict_all)
    # 3.创建数据表
    Localengine = create_engine(database_path, encoding="utf-8", echo=True)
    # 根据类一个创建table
    # for k,v in mudule_class.items():
        # v.metadata.create_all(bind=Localengine, checkfirst=True)
    # 一次性创建所有列表
    create_tables(engine=Localengine)
    # 4.创建插入数据的engine
    dbinsert = database_forwards(database_path) # engine
    # 4.1 从创建类中的dict获取具体的class
    cclass = mudule_class[li[1]] # 得到创建的mapping类对象
    # 4.2 读取单行数据（测试单行数据写入）
    a = xlsx.read_row(8,read_cell_picture=True,base64c=True) # 尝试读取单元格图片并base64转ASCII同时decode #!还原时encode 然后使用base解码即可得到bytes
    # 4.3 数据清洗，规范化并获得所有数据
    all_data = get_all_data(xlsx,cinfos[0][2]+1) # +1 读取最后一行数据
    # 4.2.1 写入单行数据
    # exa=cclass(Id=3,Number=a[0],Reversible=a[1],Residue=a[2],Leaving_Group1=a[3],Warhead=a[4],Name=a[5],Leaving_Group2=a[6],SMILES=a[7],Bonding_ID=a[8],SMARTS_match_note=a[9],Mechanism_or_End_product=a[10],Example_Pro_DOI_PDB=a[11])
    # dbinsert.insert(exa) # 单条插入
    # 5 多条数据写入
    obj_all_list = []
    # all_data = list(set(all_data))
    for num in range(len(all_data))[1:]:
        a = all_data[num]
        # print(f'{num}数据{a}')
        exa=cclass(Id=num,Number=a[0],Reversible=a[1],Residue=a[2],Leaving_Group1=a[3],Warhead=a[4],Name=a[5],Leaving_Group2=a[6],SMILES=a[7],Bonding_ID=a[8],SMARTS_match_note=a[9],Mechanism_or_End_product=a[10],Example_Pro_DOI_PDB=a[11])
        # dbinsert.insert(exa)
        obj_all_list.append(exa)
    dbinsert.insert_muti(obj_all_list) # 多条插入