# Excelltomysql Tool

[TOC]



✒️ [English](./README.md)| [中文](./README_CN.md)

## Using Tips

> Recommond virtualenv or conda to manage your pakage.
>
> These tools just for researcher to imporve efficiency.
>
> Please do not use it for commercial purposes.

## Development environment

> python3.9
>
> windows 10 x64

### Use Development environment(Recommond )

```shell
virtualenv -p python3.9 venv # create environment
# windows10 activate
.\venv\Scripts\activate.ps1
# macos/linux activate 
source .\venv\bin\activate
# install
pip install -r .\requirements.txt
```



## Target

`Transfer the excell files, xlsx, to mysql database`

### Notice

### !`Overwrite database tables!`

### Please backup your data!

## Usage

### Install dependencies

`pip install -r requirements.txt`

### Modify Profile

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

### launch

```python
python transfer_complicate.py 'yourfilename.xlsx'
```



## TREE

```shell
├─example
├─photo
├─readmodule
└─writemodule
    └─db
        └─Complextable
```

