import configparser
import pymysql
import os
import XiaoHongShuSlider
import time
import json


curpath = "../"
cfgpath = os.path.join(curpath, "setting.conf")


cf = configparser.ConfigParser()
cf.read(cfgpath, encoding="utf-8")

connection = pymysql.connect(host=cf.get("db","db_host"),
                                 port=int(cf.get("db","db_port")),
                                 user=cf.get("db","db_user"),
                                 password=cf.get("db","db_pass"),
                                 db='dream_home',
                                 charset='utf8',cursorclass=pymysql.cursors.DictCursor)

def read(url_str):
    url_list = json.loads(url_str)
    print(url_list)
    for url in url_list:
        print(url)
        res = start(url,'insert')
        time.sleep(2)
        yield res





def start(url,output):
    xiaohongshu = XiaoHongShuSlider.XiaoHongShu()
    xiaohongshu.requestUrl(url)
    if xiaohongshu.status < 0:
        return xiaohongshu.error
    if output == 'download':
        xiaohongshu.download()
    elif output == 'insert':
        xiaohongshu.insertData(connection)
    if xiaohongshu.status == 1:
        return True
    elif xiaohongshu.status <0:
        return xiaohongshu.error



if __name__ == '__main__':
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor = connection.cursor()
    sql = f'''SELECT * from dh_xiaohongshu_collection WHERE status = 0'''
    cursor.execute(sql)
    data = cursor.fetchall()
    msg = ' '
    if len(data)==0:
        print("没有待处理的数据")
    for item in data:
        url_list = item['url_list']
        for res in read(url_list):
            print(res)
            if res != True:
                msg += res
        print(msg)
        update_sql = f'''
            update dh_xiaohongshu_collection set `updated_at` = '{now_time}' ,`status`= 1,`msg`="{msg}" where id={item['id']}
        '''
        print(update_sql)
        cursor.execute(update_sql)

    connection.commit()
    cursor.close()
    connection.close()







