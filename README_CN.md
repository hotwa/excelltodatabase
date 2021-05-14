# Excelltomysql Tool

[TOC]



✒️ [English](./README.md)| [中文](./README_CN.md)

## 使用提示

> 推荐使用conda或者virtualenv管理包。
>
> 这个工具的开发为了研究人员快速的开发。
>
> 不建议在商业环境下使用

## 开发环境

> python3.9
>
> windows 10 x64

### 推荐的环境操作如下

```shell
virtualenv -p python3.9 venv # create environment
# windows10 activate
.\venv\Scripts\activate.ps1
# macos/linux activate 
source .\venv\bin\activate
# install
pip install -r .\requirements.txt
```



## 目标

将excell文件列如 xlsx，xls文件中的内容转化至数据库，目前支持sqlite3和mysql。理论上，只要是sqlalchemy支持的数据库均可以进行导入，如果您有需求，请自行修改。并开源相关我贡献的代码。

### 注意

### !这个操作只有覆盖你数据库中的原本存在的数据

### 做好数据备份工作

## 快速使用

### 安装依赖

`pip install -r requirements.txt`

### 修改配置文件

config.toml

```toml
# 使用前务必确认配置正确，并提前创建好mysql数据库
# Make sure that the configuration is correct and the MySQL database is created in advance.


[database]
# 默认使用sqlite3作为本地数据库，可以选择其他数据库mysql(已测试)等
name = "sqlite3"

[mysql]
host = "47.110.114.146"
user     = "root"
password = "pwd"
port     = 3306
database = "db"

[mysql.parameters]
pool_size = 5
charset   = "utf-8"
```

### 启动

```python
python transfer_complicate.py 'yourfilename.xlsx'
```



## 文件目录结构

```shell
├─example
├─photo
├─readmodule
└─writemodule
    └─db
        └─Complextable
```

## excell中图片读取操作

```python
import os,sys

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
```

> 在导入图片格式时对于二进制（base64压缩后，encode转string）写入mysql 推荐colum使用LONGTEXT
>
> 对于在导入的第一行label做为属性值时，不要出现()/-等python作为运算符的符号以及""、\n等。脚本无法运行，可以使用_下划线等合法字符替代。