# -*- encoding: utf-8 -*-

# 测试结论 直接使用datetime.datetime.now()进行时间的插入

import MySQLdb
import datetime
    
conn = MySQLdb.connect(host='localhost',
	                       user='root',
	                       db='component',
	                       port=3306,
	                       passwd='')

#自动提交 没添加之前 存在没有保存的情况
conn.autocommit(1)

cursor = conn.cursor()

update_sql = "update cpu set price3tmall=%s, price4jingdong=%s, price345updatetime=%s where id=%s"

cursor.execute(update_sql, (120, 240, datetime.datetime.now(), 1))