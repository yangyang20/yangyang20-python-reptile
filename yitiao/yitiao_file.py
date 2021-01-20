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
    cate_name_1=''
    cate_name_2=''
    filePath=r"./json_txt"
    fileList=os.listdir(filePath)
    for file in fileList:
        try:
            f=open(os.path.join(filePath,file),'rb')
            # print(file) # 文件名
            str = f.read()
            conetent = json.loads(str)
            list = conetent['content'][0]['products']
            for item in list:
                parseGoods(item,cate_name_1,cate_name_2)
        except Exception:
            print("有错误")
            continue
    cursor.close()
    connection.close()

def parseGoods(item,cate_name_1,cate_name_2):
    saleInfo = item['saleInfo']
    goods_id = saleInfo['spuId']
    goods_name = saleInfo['title']
    goods_vice_name = saleInfo['subTitle']
    spuPriceInfo = saleInfo['spuPriceInfo']
    goods_store_name = saleInfo['shopName']
    goods_volume = saleInfo['saleCount']
    goods_url = f"https://h5.yit.com/r/product?product_id={goods_id}&_spm5=templateid-11+$productid-{goods_id}"
    goods_reputation_count=''
    goods_reputation_rate=''
    goods_price = spuPriceInfo['minPriceInfo']['price'] /100
    cate_name_2 = cate_name_2
    cate_name_1 = cate_name_1
    sql =f'''
           INSERT INTO `yitiao`
           (`cate_name_1`, `cate_name_2`,`goods_name`,`goods_id`,`goods_store_name`,`goods_price`,`goods_reputation_rate`,`goods_reputation_count`,`goods_url`,`goods_vice_name`,`goods_volume`) VALUES
           ('{cate_name_1}','{cate_name_2}','{goods_name}','{goods_id}','{goods_store_name}','{goods_price}','{goods_reputation_rate}','{goods_reputation_count}','{goods_url}','{goods_vice_name}','{goods_volume}')
           '''
    try:
        # print(sql)
        cursor.execute(sql)
        connection.commit()
    except Exception:
        print(sql)
        print("sql有错误==")



if __name__ == '__main__':
    readFile()