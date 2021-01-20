from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
import json







# print(html)
# finally:
#     print("有错误")
#     driver.quit()


def parseHtml():
    driver = webdriver.Chrome()
    driver.get(r'https://h5.yit.com/r/category')

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Category-CategoryR")))

    html = driver.find_element_by_id('wrapElementMain').get_attribute('innerHTML')
    doc = pq(html)

    # 当前一级类目

    actCategory1 = doc('ul.F1Category-ul li.active div.F1Category-item span')
    print("一级类目：", actCategory1.text())

    # 二级类目
    actCategory2 = doc('ul.F1Category-ul li.active ul.subF1Category li.active span')
    print("二级类目：", actCategory2.text())
    print("================")
    # 商品列表
    goodsList = doc('.Category-ProductLists .Category-ItemLine')
    i=0
    for goods in goodsList.items():

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Category-ProductLists")))

        goodsItem=goods('div.GoodsItemLine-infoEle div.GoodsItemLine-info')
        goodsName=goodsItem('div.GoodsItemLine-info-detail div.GoodsItemLine-info-detail-title').text()
        goodsPrice=goods('div.GoodsItemLine-info-price div.GoodsItemLine-content div.GoodsItemLine-info-price-saveprice span.GoodsItemLine-info-price-new').text()
        goodsUrlDoc=goods('div.GoodsItemLine-infoEle a')
        goodsUrl = goodsUrlDoc.attr('href')
        goodsStoreName = goodsUrlDoc('div.ShopNameEntrance span.ShopNameEntrance-storeName').text()

        Item={}
        # print('商品名称:',goodsName)
        # print('商品价格:',goodsPrice)
        # print('商品链接:',goodsUrl)
        # print('商品店铺:',goodsStoreName)
        Item['goods_name'] = goodsName
        Item['cate_name_1'] = actCategory1.text()
        Item['cate_name_2'] = actCategory2.text()
        Item['goods_url'] = 'https://h5.yit.com'+goodsUrl
        Item['goods_store_name'] = goodsStoreName
        Item['goods_price'] = goodsPrice

        # print(goods.html())
        print("==============================")
        print('当前url:',driver.current_url)
        divEl = driver.find_elements_by_css_selector('div.Category-ProductLists div.Category-ItemLine')

        # divEl = driver.find_elements_by_xpath(f"//div[@id='wrapElementMain']//div[@class='Category-ProductLists']/div")
        print(len(divEl))

        print(i)
        divEl[i].click()
        # driver.switch_to.window(driver.window_handles[-1])
        goods_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "wrapElementMain")))

        goods_html = driver.find_element_by_id('wrapElementMain').get_attribute('innerHTML')
        parseGoodsHtml(Item,goods_html)
        i = i+1
        # driver.close()
        driver.back()

def parseGoodsHtml(goods,goodsHtml):

    # element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, "wrapElementMain")))
    #
    # html = driver.find_element_by_id('wrapElementMain').get_attribute('innerHTML')
    try:
        html = goodsHtml
        doc = pq(html)
        # 商品id和副标题
        goods_detail=doc('div.Product div.Product-ProductName-module')
        goods_name_detail_str=goods_detail.attr('data-eventmore')
        goods_name_detail = json.loads(goods_name_detail_str)
        goods_vice_name=goods_name_detail['spu_des']
        goods_id=goods_name_detail['spu_id']

        goods_reputation_rate = doc('div.Product-module-ProductComment ul.listItems li.items div.leftTittle').text()
        goods_reputation_count = doc('div.Product-module-ProductComment ul.listItems li.scoreAndsalesVolume span:first').text()
        goods_volume = doc('div.Product-module-ProductComment ul.listItems li.scoreAndsalesVolume span:last').text()


        goods['goods_id'] = goods_id
        goods['goods_reputation_rate'] = goods_reputation_rate
        goods['goods_reputation_count'] =goods_reputation_count
        goods['goods_vice_name'] = goods_vice_name
        goods['goods_volume'] = goods_volume

        print(goods)
        print("===================")
        return True

    except Exception:
        print("有错误")
        print("============")
        return False




if __name__ == '__main__':
    parseHtml()