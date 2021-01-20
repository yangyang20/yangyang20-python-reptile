import requests
import pymysql
from config import *
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

session = requests.session()

headers ={
    'Host': 'emap.pcsc.com.tw',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

cookie = {
    '_ga':	'GA1.3.1074955585.1563180940',
    '_gid':	'GA1.3.73295267.1563180940',
    'ASP.NET_SessionId':'jdfcoqekubnrf5igoovmvufd',
    'citrix_ns_id':	'O/XJDouXjP7mMTv9W5fAiHWYn8g0001',
    'SET_EC_COOKIE':'rd1378o00000000000000000000ffff0ac80807o443'
}

# 每个城市所对应的id
CityId ={
    '基隆市' : '02',
    '台北市' : '01',
    '新北市' : '03',
    '桃園市' : '04',
    '新竹市' : '05',
    '新竹縣' : '06',
    '苗栗縣' : '07',
    '台中市' : '08',
    '彰化縣' : '10',
    '南投縣' : '11',
    '雲林縣' : '12',
    '嘉義縣' : '14',
    '嘉義市' : '13',
    '台南市' : '15',
    '高雄市' : '17',
    '屏東縣' : '19',
    '宜蘭縣' : '20',
    '花蓮縣' : '21',
    '台東縣' : '22',
    '連江縣' : '24',
    '金門縣' : '25',
    '澎湖縣' : '23'
}

# 存储城市、县区信息
StoreMsg ={}

def city():
    url = "https://emap.pcsc.com.tw/emap.aspx"
    response = session.get(headers=headers,url=url,cookies=cookie)
    soup = BeautifulSoup(response.text, "html5lib")
    cityList = soup.select('#tw a')
    for item in cityList:
        city = item.get_text()
        # print(city)
        StoreMsg['city'] = city
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
        cur = conn.cursor()
        effect_row = cur.execute(
            'INSERT IGNORE INTO `711_city`( `city`) VALUES (%s)', city)
        if effect_row:
            # 这一步才是真正的提交数据
            conn.commit()
        cityId = int(cur.lastrowid)
        if cityId != 0:
            cur.close()
            conn.close()
            area(CityId[city], cityId)
        continue




def area(cityId,id):
    data = {
        'commandid':'GetTown',
        'cityid':cityId ,
        'leftMenuChecked': ''
    }
    url = 'https://emap.pcsc.com.tw/EMapSDK.aspx'
    response = session.post(headers=headers,url=url,data=data)
    # print(response.text)
    # 返回结果是xml，解析需要的信息，插入数据库
    xml = ET.fromstring(response.text)
    for table in xml.getiterator('GeoPosition'):
        townName = table.find('TownName')
        StoreMsg['area'] = townName.text
        # print(townName.text)
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
        cur = conn.cursor()
        effect_row = cur.execute(
            'INSERT IGNORE INTO `711_area`( `city_id`,`city`,`area`) VALUES (%s,%s,%s)', (id, StoreMsg['city'], StoreMsg['area']))
        if effect_row:
            # 这一步才是真正的提交数据
            conn.commit()
        areaId = int(cur.lastrowid)
        if areaId != 0:
            cur.close()
            conn.close()
            # print(res)
            store(id, areaId)
        continue



def store(cityId,areaId):
    url = 'https://emap.pcsc.com.tw/EMapSDK.aspx'
    data = {
        'commandid':'SearchStore',
        'city':StoreMsg['city'],
        'town':StoreMsg['area'],
        'roadname':'',
        'ID':'',
        'StoreName':'',
        'SpecialStore_Kind':'',
        'leftMenuChecked':'',
        'address':''
    }
    response = session.post(headers=headers,url=url,data=data)
    # print(response.text)
    xml = ET.fromstring(response.text)
    for table in xml.getiterator('GeoPosition'):
        POIName = table.find('POIName')
        POIID = table.find('POIID')
        Address = table.find('Address')
        Telno = table.find('Telno')
        storeName = (POIName.text).strip()
        storeNum = (POIID.text).strip()
        storeSite = (Address.text).strip()
        storePhoneNum = (Telno.text).strip()
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
        cur = conn.cursor()
        effect_row = cur.execute(
            'INSERT IGNORE INTO `711_store`( `city_id`,`city`,`area_id`,`area`,`store_name`,`store_num`,`site`,`phone_num`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (cityId, StoreMsg['city'], areaId, StoreMsg['area'], storeName, storeNum, storeSite, storePhoneNum))
        if effect_row:
            # 这一步才是真正的提交数据
            conn.commit()
        cur.close()
        conn.close()
        print(storeName,storeNum,storeSite,storePhoneNum)

if __name__ == '__main__':
    city()