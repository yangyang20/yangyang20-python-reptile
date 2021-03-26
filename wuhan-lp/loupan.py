from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq

import re
import pymysql
from selenium.webdriver.chrome.options import Options

opts = Options()
# opts.headless = True

opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--headless')
opts.add_argument('blink-settings=imagesEnabled=false')
opts.add_argument('--disable-gpu')
drive_path='./chromedriver'

baseUrl='https://wuhan.newhouse.fang.com'
driver = webdriver.Chrome(executable_path=drive_path,options=opts)


def parsePage():
    urlOne = '/house/s/'
    # urlOne = '/house/s/jiangan1/b91/'
    url = baseUrl+urlOne
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "otherpage")))
    html = driver.find_element_by_class_name('otherpage').get_attribute('innerHTML')

    doc = pq(html)
    pages = doc('span')
    pageRow = re.findall(r'\/(\d+)',pages.text())
    pageCount = int(pageRow[0])
    for i in range(1,pageCount):
        # try:
        page = f'9{i}/'
        temp = url + page
        parseHtml(temp)
        # except Exception as e:
        #     print(e)
        #     continue
    driver.quit()

def parseHtml(url):
    print(url)
    driver = webdriver.Chrome(executable_path=drive_path,options=opts)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "newhouse_loupai_list")))

    html = driver.find_element_by_id('newhouse_loupai_list').get_attribute('innerHTML')
    doc = pq(html)


    list = doc('ul li')

    for item in list.items():

        if item.attr("id") and "lp_"in item.attr("id"):
            # print(item.html())
            loupan = {}
            id = item.attr("id")
            loupan['lp_id'] = re.findall('(\d+)',id)[0]
            loupan['lp_name'] = item('div.nlcd_name a').text()
            loupan['lp_price'] = item('div.nhouse_price span').text()
            loupan['lp_address'] = item('div.address a').text()
            loupan['house_type'] = item('div.house_type a')
            loupan['inSale'] = item('div.fangyuan span').text()
            loupan['fangyuan'] = item('div.fangyuan a')
            parseItem(loupan)
            # print("=================")
    driver.close()


def parseItem(item):
    temp=''
    for fangyuan in item['fangyuan'].items():
        temp+=fangyuan.text()+"-"
    item['fangyuan'] = temp[:-1]
    temp=''
    for house_type in item['house_type'].items():
        temp+=house_type.text()+'-'
    item['house_type'] = temp[:-1]

    item['region'] = re.findall(r'\[(.*?)\]',item['lp_address'])[0]

    print(item)
    insterData(item)
    # pass



def insterData(data):
    connection = pymysql.connect(host='127.0.0.1',
                                 port=3306,
                                 user='root',
                                 password='393622951',
                                 db='wuhan_loupan',
                                 charset='utf8')
    # 获取游标
    cursor = connection.cursor()
    sql = f'''
             INSERT INTO `wuhan`
             (`lp_id`, `lp_name`,`lp_price`,`lp_address`,`house_type`,`inSale`,`fangyuan`,`region`) VALUES
             ('{data['lp_id']}','{data['lp_name']}','{data['lp_price']}','{data['lp_address']}','{data['house_type']}','{data['inSale']}','{data['fangyuan']}','{data['region']}')
             '''
    print(sql)
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    parsePage()