import json
import os
import pymysql


connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='root',
                             db='test',
                             charset='utf8')
# 获取游标
cursor = connection.cursor()

def readFile():
    filePath = r"./json_goods_txt"
    fileList = os.listdir(filePath)
    for file in fileList:
        f = open(os.path.join(filePath, file), 'rb')
        # print(file) # 文件名
        str = f.read()
        conetent = json.loads(str)
        goods = conetent['content'][0]['productDetailInformation']
        updateGoods(goods)
    cursor.close()
    connection.close()

def updateGoods(goods):
    goods_id = goods['spuId']
    goods_reputation_count = goods['commentInformation']['totalCount']
    goods_reputation_rate = goods['commentInformation']['veryGoodCommentRate']
    sql = f'''
        UPDATE `yitiao` SET `goods_reputation_count` = '{goods_reputation_count}',`goods_reputation_rate`='{goods_reputation_rate}' WHERE `goods_id` = '{goods_id}'
    '''
    try:
        print(sql)
        cursor.execute(sql)
        connection.commit()
    except Exception:
        print(sql)
        print("sql有错误==")


if __name__ == '__main__':
    readFile()