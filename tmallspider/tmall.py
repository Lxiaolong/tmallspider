import requests
from lxml import etree
from selenium import webdriver
import re,os
import threading
import csv
import time
import urllib
header1={
'Host': 'list.tmall.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
'Accept-Encoding': 'gzip, deflate, br',
'Referer': 'https://www.tmall.com/?ali_trackid=2:mm_26632258_3504122_55934697:1507798806_276_954577146&upsid=ca99738efd0c39f566a3b5e3b1ae72ad&clk1=ca99738efd0c39f566a3b5e3b1ae72ad',
'Cookie': 'cna=T+5OEaIx0WcCAXcnlAEXmS7A; isg=ApKSSZsQH_LXNmONFTTL2phY4lu0C5dZX3lU4lzrvsUwbzJpRDPmTZiNqfAt; _med=dw:1366&dh:768&pw:1366&ph:768&ist:0; pnm_cku822=098%23E1hvAQvUvbpvU9CkvvvvvjiPP2SwtjnbP2LvtjYHPmPvAjDPP2591jE2Pssp6ji2P2u5vpvhvvmv9FyCvvpvvvvvvphvC9vhvvCvpvyCvhQhpBUvCsfpaNoxdBQaWXxr1WkK5kx%2F1nCl%2Bb8rwZxlYVllHdUfUzc60f06WeCp%2BExrA8TJwx0xfw1l53igxExr1j7Jh7ERD7zvaXT1Kphv8vvvvvCvpvvvvvmm86CvmUIvvUUdphvWvvvv9krvpvQvvvmmW6Cv2hmivpvUvvmvd6%2Fv0goEvpvV2vvC9jxC2QhvCvvvvvv%3D; cq=ccp%3D1; tk_trace=1; t=05f7f639fb3dc6a11282222513ad24c0; _tb_token_=e7b8855ee8833; cookie2=18dc793b00f1e2b3acc4938d4afd395d; tt=tmall-main; res=scroll%3A1349*6144-client%3A1349*674-offset%3A1349*6144-screen%3A1366*768',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'Cache-Control': 'max-ag=0'
}
if not os.path.exists('tmall.csv'):
    with open('tmall.csv', 'w', encoding='utf-8',newline='') as f:
        ins = csv.writer(f)
        ins.writerow(('标题', '店铺名称', '月成交量', '评价数','商品详情','图片地址','评论图片地址','价格','累计评论','收藏人气'))
lock= threading.Lock()
def tmallspider(key):
    base_url='https://list.tmall.com/search_product.htm?spm=a220m.1000858.0.0.74a9057fnNGjl4&s={0}&q={1}&sort=s&style=g&from=mallfp..pc_1_searchbutton&active=2&type=pc#J_Filter'
    driver=webdriver.Firefox()
    for s in range(100):#天猫搜索只能出现100页
        url=base_url.format(s*60,urllib.parse.quote(key))
        page=requests.get(url,headers=header1).text
        tree=etree.HTML(str(page))
        a=tree.xpath('//div[@class="product  "]/@data-id')
        for i in a:#以此爬取商品
            image_urls = ''
            product_detail=''
            comments_image_url=''
            base_comments_url='https://rate.tmall.com/list_detail_rate.htm?itemId={0}&sellerId={1}&order=3&currentPage={2}&picture=1'
            image=tree.xpath('//div[@data-id="{0}"]//img[@data-ks-lazyload]/@data-ks-lazyload'.format(i))
            if tree.xpath('//div[@data-id="{0}"]//p[@class="productStatus"]//em/text()'.format(i)):
                product_Monthly_sales=tree.xpath('//div[@data-id="{0}"]//p[@class="productStatus"]//em/text()'.format(i))[0].rstrip('笔')
            else:
                product_Monthly_sales=0
            if tree.xpath('//div[@data-id="{0}"]//p[@class="productStatus"]//a/text()'.format(i)):
                product_comments=tree.xpath('//div[@data-id="{0}"]//p[@class="productStatus"]//a/text()'.format(i))[0]
            else:
                product_comments=0
            productShop_name=tree.xpath('//div[@data-id="{0}"]//a[@class="productShop-name"]/text()'.format(i))[0].strip('\\n\', \'')
            title=tree.xpath('//div[@data-id="{0}"]//p[@class="productTitle"]/a/@title'.format(i))[0]
            item_url='https:'+tree.xpath('//div[@data-id="{0}"]//p[@class="productTitle"]/a/@href'.format(i))[0]
            price=tree.xpath('//div[@data-id="{0}"]//p[@class="productPrice"]/em/text()'.format(i))[0]
            for i in image:
                image_urls=image_urls+'https:'+i.rstrip('.jpg').rstrip('_30x30')+','
            driver.get(item_url)
            page = etree.HTML(driver.page_source)
            if not page.xpath('//table[@class="tm-tableAttr"]//td/text()|//th/text()'):
                time.sleep(20)
                driver.get(item_url)
                page = etree.HTML(driver.page_source)
            detail = page.xpath('//table[@class="tm-tableAttr"]//td/text()|//th/text()')
            product_accumulatecomments = page.xpath('//span[@class="tm-count"]/text()')[1]
            product_popularity = page.xpath('//span[@id="J_CollectCount"]/text()')[0].lstrip('（').rstrip('人气）')
            supid=re.search(r'spuId=(.*?)&',driver.page_source).group(1)
            for i in detail:
                product_detail=product_detail+i
            km=re.search(r'id=(.*?)&.*?user_id=(.*?)&',item_url)
            comments_url=base_comments_url.format(km.group(1),km.group(2),1)
            comjs=requests.get(comments_url)
            print(comjs.status_code)
            while True:
                if re.search(r'"lastPage":(.*?),',comjs.text):
                    counts=re.search(r'"lastPage":(.*?),',comjs.text).group(1)
                    break
                else:
                    comjs = requests.get(comments_url)
                    print('300')

            i = re.findall(r'pics":\[(.*?)]', comjs.text)
            for j in i:
                j = j.split(',')
                for k in j:
                    comments_image_url=comments_image_url+'https'+k.strip('"')+','
            for count in range(2,int(counts)):#爬取评论图片
                comments_url = base_comments_url.format(km.group(1), km.group(2), count)
                comjs = requests.get(comments_url)
                print(comjs.status_code)
                i = re.findall(r'pics":\[(.*?)]', comjs.text)
                for j in i:
                    j = j.split(',')
                    for k in j:
                        comments_image_url = comments_image_url + 'https:' + k.strip('"') + ','
            if lock.acquire(True):
                with open('tmall.csv','a',encoding='utf-8',newline='') as file:
                    writer=csv.writer(file)
                    writer.writerow((title,productShop_name,product_Monthly_sales,product_comments,
                                      product_detail,image_urls,comments_image_url,price
                                      ,product_accumulatecomments,product_popularity))
                lock.release()


if __name__=='__main__':
    thread=[]
    for key in ['男装','男鞋','女装', '女鞋']:
        thread.append(threading.Thread(target=tmallspider,args=[key,]))
    for t in thread:
        t.setDaemon(True)
        t.start()
    for t in thread:
        t.join()