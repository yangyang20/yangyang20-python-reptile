import requests
from config import *
import pymysql
import json
from bs4 import BeautifulSoup

session = requests.session()

headers ={
    'Host': 'api.map.com.tw',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.family.com.tw/marketing/inquiry.aspx'

}

cookie = {
    'ASP.NET_SessionId':	'03coodnoxh5gnpss2rv2ttry',
    'ASPSESSIONIDQUCQDQDD':	'PIDHPDCCJKEMOIBELPFMKIFM',
    'ASPSESSIONIDQWAQDQDC':	'PGKBJCCCHJJBNICGOHMBDFBF',
    'ASPSESSIONIDQWASAQBD':	'DEMBMHCCELIJHMAHCCBGEAIO',
    'ASPSESSIONIDQWDRCQAC':	'OFFBOMBCJGIDFGJBMNOCGJNN',
    'ASPSESSIONIDSWAQDQAC':	'HANBBOBCMHKEEMOHLOCALJDE',
    'ServerName':	'www.family.com.tw'
}




def city():
    url = "https://www.family.com.tw/marketing/inquiry.aspx#"
    response = session.get(headers=headers, url=url)
    soup = BeautifulSoup(response.text, "html5lib")
    cityList = soup.select('.city')
    for item in cityList:
        city = item.get_text()
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
        cur = conn.cursor()
        effect_row = cur.execute(
            'INSERT IGNORE INTO `family_city`( `city`) VALUES (%s)',city)
        if effect_row:
            # 这一步才是真正的提交数据
            conn.commit()
        cityId =  int(cur.lastrowid)
        if cityId !=0:
            cur.close()
            conn.close()
            area(city,cityId)
        continue





def area(city,cityId):
    url = "https://api.map.com.tw/net/familyShop.aspx?searchType=ShowTownList&type=&city=%s&fun=storeTownList&key=6F30E8BF706D653965BDE302661D1241F8BE9EBC" % city
    response = session.get(headers=headers,url=url,cookies=cookie)
    str =  response.text [15:-2]
    storeTownList = str.split('},')
    for i in storeTownList :
        i = i.strip()
        # 解析多json对象字符串的方法
        if i.endswith('}') == False:
            i = i + '}'
        try:
            res = json.loads(i)
        except:
            print(i)
            continue
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
        cur = conn.cursor()
        effect_row = cur.execute(
            'INSERT IGNORE INTO `family_area`( `city_id`,`city`,`area`) VALUES (%s,%s,%s)', (cityId,city,res['town']))
        if effect_row:
            # 这一步才是真正的提交数据
            conn.commit()
        areaId = int(cur.lastrowid)
        if areaId !=0:
            cur.close()
            conn.close()
            # print(res)
            store(cityId,res['city'],areaId,res['town'])
        continue



def store(cityId, city, areaId,area):
    print(cityId, city, areaId,area)
    url = "https://api.map.com.tw/net/familyShop.aspx?searchType=ShopList&type=&city=%s&area=%s&road=&fun=showStoreList&key=6F30E8BF706D653965BDE302661D1241F8BE9EBC" % (city,area)
    response = session.get(headers=headers,url=url)
    res = response.text[15:-2]
    showStoreList = res.split('},')
    for item in showStoreList:
        item = item.strip()
        if item.endswith('}') == False:
            item = item + '}'
        try:
            res = json.loads(item)
        except:
            print(item)
            continue
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
        cur = conn.cursor()
        effect_row = cur.execute(
            'INSERT IGNORE INTO `family_store`( `city_id`,`city`,`area_id`,`area`,`store_name`,`store_num`,`site`,`road`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (cityId, city, areaId,area,res['NAME'],res['oldpkey'],res['addr'],res['road']))
        if effect_row:
            # 这一步才是真正的提交数据
            conn.commit()
        cur.close()
        conn.close()
        print(res)




if __name__ == '__main__' :
    city()