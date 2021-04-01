import configparser

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
import re
import pymysql
from selenium.webdriver.chrome.options import Options
import json
import os
import time


curpath = "../"
cfgpath = os.path.join(curpath, "setting.conf")


cf = configparser.ConfigParser()
cf.read(cfgpath, encoding="utf-8")


opts = Options()
# opts.headless = True
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--headless')
opts.add_argument('blink-settings=imagesEnabled=false')
opts.add_argument('--disable-gpu')
drive_path = cf.get("path","drive_path")

class XiaoHongShu:

    def __init__(self):
        # self.baseUrl = f'https://www.xiaohongshu.com/discovery/item/{id}'
        self.status = 0
        self.data = {}
        self.error=''
        self.url=''

    def requestUrl(self,url):
        # try:
        driver = webdriver.Chrome(executable_path=drive_path, options=opts)
        # url = baseUrl + '60500ecf000000002103f257'

        # self.data['xiaohongshu_id'] = id
        driver.get(url)
        self.data['url'] = url
        self.url = url
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "slide")))
        html = driver.find_element_by_id('app').get_attribute('innerHTML')

        self.parseHtml(html)
        self.data['real_url'] = driver.current_url
        driver.close()
        # except Exception as error:
        #     print(error)
        #     self.error =  f"{self.url}网址有问题:"
        #     self.status=-1


    def parseHtml(self,html):
        # try:
        doc = pq(html)
        imageList = doc('.slide li span')
        imageUrl = []
        for item in imageList.items():
            style = item.attr('style')
            temp = re.findall(r'\/\/(.*)\/', style)[0]
            imageUrl.append('http://' + temp + '.jpg')

        self.data['images'] = imageUrl
        # print(imageUrl)

        titleDoc = doc('h1.title')
        title = titleDoc.text()
        self.data['title'] = title
        # print(title)

        contentList = []
        contentDoc = doc('.all-tip .content p')
        for item in contentDoc.items():
            contentList.append(item.text())
        self.data['content'] = contentList
            # print(contentList)

        # except Exception as error:
        #     print(error)
        #     self.error =  f"{self.url}解析有问题"
        #     self.status=-1


    def download(self):
        # try:
        imageList = self.data['images']
        title = self.data['title']
        contentList = self.data['content']
        i = 1
        path = f'./{title[0:4]}'
        folder = os.path.exists(path)
        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)
        for url in imageList:
            r = requests.get(url)
            if r.status_code == 200:
                imagePath = f'{path}/{i}.jpg'
                open(f'{imagePath}', 'wb').write(r.content)  # 将内容写入图片
                i += 1
        f = open(f'{path}/content.txt', 'a', encoding='utf-8')
        f.write(str(title) + '\n')
        for item in contentList:
            f.write(str(item) + '\n')
        f.close()
        self.status=1
        # except Exception as error:
        #     print(error)
        #     self.error=  f"{self.url}下载有问题"
        #     self.status=-1




    def insertData(self,connection):
        # 获取游标
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # try:
            cursor = connection.cursor()

            images = json.dumps(self.data['images'])
            content = "\n".join(self.data['content'])
            sql = f'''
                       INSERT INTO `dh_xiaohongshu_data`
                       (`title`, `url`,`real_url`,`images`,`content`,`created_at`,`updated_at`) VALUES
                       ('{self.data['title']}','{self.data['url']}','{self.data['real_url']}','{images}','{content}','{now_time}','{now_time}')
                       '''
            print(sql)
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            self.status=1
        except Exception as error:
            self.error =  f"{self.url}数据库插入错误" + error
            self.status=-1



if __name__ == '__main__':
    xiaohongshu = XiaoHongShu()
    xiaohongshu.requestUrl('http://www.baidu.com')








