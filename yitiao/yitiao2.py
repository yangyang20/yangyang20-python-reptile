from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
import json
import re
import pymysql
import time




# print(html)
# finally:
#     print("有错误")
#     driver.quit()


def parseHtml():
    driver = webdriver.Chrome()
    driver.get(r'https://h5.yit.com/r/category')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Category-CategoryR")))

    html = driver.find_element_by_id('wrapElementMain').get_attribute('innerHTML')
    doc = pq(html)

    # 分类列表
    categoryList = doc('div.Category ul.F1Category-ul li.F1Category-li')
    i=0
    for category in categoryList.items():
        categoryEl = driver.find_elements_by_css_selector('div.Category ul.F1Category-ul li.F1Category-li')
        categoryEl[i].click()
        subF1Category = category('ul.subF1Category li.F2Category-item')
        j=0
        for sub_category in subF1Category.items():
            subCategoryEl = driver.find_elements_by_css_selector('div.Category ul.F1Category-ul li.active  ul.subF1Category li.subF1Category-item')
            subCategoryEl[j].click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Category-CategoryR")))
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            html_new = driver.find_element_by_id('wrapElementMain').get_attribute('innerHTML')
            doc_new = pq(html_new)

            actCategory1= category('.F1Category-item span').text()
            actCategory2=sub_category('span').text()
            parseMain(doc_new,actCategory1,actCategory2)
            j+=1
            print(j)
        i+=1
        print(i)
    driver.quit()
    print("结束")

def parseMain(doc,actCategory1,actCategory2):
    # 当前一级类目
    # actCategory1 = doc('ul.F1Category-ul li.active div.F1Category-item span').text()
    print("一级类目：", actCategory1)

    # 二级类目
    # actCategory2 = doc('ul.F1Category-ul li.active ul.subF1Category li.active span').text()
    print("二级类目：", actCategory2)
    print("================")

    # 商品列表
    goodsList = doc('.Category-ProductLists .Category-ItemLine')
    # print(goodsList)
    i = 0
    for goods in goodsList.items():
        goodsItem = goods('div.GoodsItemLine-infoEle div.GoodsItemLine-info')
        goodsName = goodsItem('div.GoodsItemLine-info-detail div.GoodsItemLine-info-detail-title').text()
        goodsPrice = goods(
            'div.GoodsItemLine-info-price div.GoodsItemLine-content div.GoodsItemLine-info-price-saveprice span.GoodsItemLine-info-price-new').text()
        goodsUrlDoc = goods('div.GoodsItemLine-infoEle a')
        goodsUrl = goodsUrlDoc.attr('href')
        goodsStoreName = goodsUrlDoc('div.ShopNameEntrance span.ShopNameEntrance-storeName').text()

        Item = {}
        # print('商品名称:',goodsName)
        # print('商品价格:',goodsPrice)
        # print('商品链接:',goodsUrl)
        # print('商品店铺:',goodsStoreName)
        Item['goods_name'] = goodsName
        Item['cate_name_1'] = actCategory1
        Item['cate_name_2'] = actCategory2

        spm = goods.attr('data-spm')

        id = re.findall(r'productid-(\d+)', spm)[0]
        res = findGoods(id)
        if res:
            continue
        Item['goods_url'] = f'https://h5.yit.com/r/product?product_id={id}&_spm5=templateid-11+$productid-{id}'
        Item['goods_store_name'] = goodsStoreName
        Item['goods_price'] = goodsPrice

        # driver.switch_to.window(driver.window_handles[-1])
        i += 1
        parseGoodsHtml(Item)
    print('此次结束了：', i)

def parseGoodsHtml(goods):
    driver = webdriver.Chrome()
    try:
        driver.get(goods['goods_url'])
    # if True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "priceModule")))

        html = driver.find_element_by_id('wrapElementMain').get_attribute('innerHTML')
        doc = pq(html)
        # 商品id和副标题
        goods_detail=doc('div.Product div.Product-ProductName-module')
        goods_name_detail_str=goods_detail.attr('data-eventmore')
        goods_name_detail = json.loads(goods_name_detail_str)
        goods_vice_name=goods_name_detail['spu_des']
        goods_id=goods_name_detail['spu_id']
        if not goods['goods_name'] or goods['goods_name'] == "":
            goods['goods_name'] = goods_name_detail['spu_name']

        if not goods['goods_store_name'] or goods['goods_store_name'] == "":
            goods_store_name = doc('div.shopInfoModule p.ShopCard-shopName').text()
            goods['goods_store_name'] = goods_store_name

        goods_reputation_rate = doc('div.Product-module-ProductComment ul.listItems li.items div.leftTittle').text()
        goods_reputation_count = doc('div.Product-module-ProductComment ul.listItems li.scoreAndsalesVolume span:first').text()
        goods_volume = doc('div.Product-module-ProductComment ul.listItems li.scoreAndsalesVolume span:last').text()


        if goods['goods_price']:
            goods_price = re.findall('(\d+)',goods['goods_price'])
            if goods_price:
                goods['goods_price']=goods_price[0]

        if goods_reputation_rate:
            temp = re.findall('(\d+)',goods_reputation_rate)
            if temp:
                goods_reputation_rate=temp[0]

        if goods_reputation_count:
            goods_reputation_count_list = re.findall('(\d+)', goods_reputation_count)
            if goods_reputation_count_list:
                goods_reputation_count = ".".join(goods_reputation_count_list) + '%'

        if goods_volume:
            temp = re.findall('(\d+)',goods_volume)
            if temp:
                goods_volume =temp[0]

        goods['goods_id'] = goods_id
        goods['goods_reputation_rate'] = goods_reputation_rate
        goods['goods_reputation_count'] =goods_reputation_count
        goods['goods_vice_name'] = goods_vice_name
        goods['goods_volume'] = goods_volume
        driver.close()
        print(goods)
        print("===================")
        insertData(goods)
        return True

    except Exception:
        print("有错误")
        print(driver.current_url)
        driver.close()
        print("============")
        return False

def insertData(goods):
    connection = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 password='root',
                                 db='test',
                                 charset='utf8')
    # 获取游标
    cursor = connection.cursor()
    sql = f'''
           INSERT INTO `yitiao`
           (`cate_name_1`, `cate_name_2`,`goods_name`,`goods_id`,`goods_store_name`,`goods_price`,`goods_reputation_rate`,`goods_reputation_count`,`goods_url`,`goods_vice_name`,`goods_volume`) VALUES
           ('{goods['cate_name_1']}','{goods['cate_name_2']}','{goods['goods_name']}','{goods['goods_id']}','{goods['goods_store_name']}','{goods['goods_price']}','{goods['goods_reputation_rate']}','{goods['goods_reputation_count']}','{goods['goods_url']}','{goods['goods_vice_name']}','{goods['goods_volume']}')
           '''
    try:
        cursor.execute(sql)
        connection.commit()
    except Exception:
        print(sql)
        print("sql有错误==")
    cursor.close()
    connection.close()


def findGoods(id):
    connection = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 password='root',
                                 db='test',
                                 charset='utf8')
    # 获取游标
    cursor = connection.cursor()
    sql = f'SELECT * FROM `yitiao` WHERE goods_id={id}'
    cursor.execute(sql)
    info = cursor.fetchone()
    if info:
        return True
    else:
        return False

if __name__ == '__main__':
    parseHtml()