import pymysql
import re


connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='root',
                             db='test',
                             charset='utf8')
# 获取游标
cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

sql=f'select * from `yitiao2`'

cursor.execute(sql)

res = cursor.fetchall()

for item in res:
    try:
        goods_price=''
        goods_reputation_rate=''
        goods_reputation_count=''
        if item['goods_price']:
            goods_price = re.findall('(\d+)',item['goods_price'])[0]
        if  item['goods_reputation_rate']:
            goods_reputation_rate = re.findall('(\d+)',item['goods_reputation_rate'])[0]
        if item['goods_reputation_count']:
            goods_reputation_count_list = re.findall('(\d+)',item['goods_reputation_count'])
            goods_reputation_count = ".".join(goods_reputation_count_list)+'%'
        sql_u = f"UPDATE `yitiao2` SET `goods_price` = '{goods_price}',`goods_reputation_rate` = '{goods_reputation_rate}',goods_reputation_count='{goods_reputation_count}' WHERE `id` = {item['id']}"
        print(sql_u)
        # 执行SQL语句
        cursor.execute(sql_u)
        # 提交到数据库执行
        connection.commit()
    except:
        # 发生错误时回滚
        print(item)
        print('123')
        continue
