#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__author__ = 'Kandy.Ye'
__mtime__ = '2017/4/12'
"""

import re
import logging
import json
import requests
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from items import *
from elasticsearch import Elasticsearch
import datetime

from elasticsearch import helpers

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


key_word = ['book', 'e', 'channel', 'mvd', 'list']
Base_url = 'https://list.jd.com'
price_url = 'https://p.3.cn/prices/mgets?skuIds=J_'
comment_url = 'https://club.jd.com/comment/productPageComments.action?productId=%s&score=0&sortType=5&page=%s&pageSize=10'
favourable_url = 'https://cd.jd.com/promotion/v2?skuId=%s&area=1_72_2799_0&shopId=%s&venderId=%s&cat=%s'


allNum = 0


actions  = []
blukSize = 10

indexName = "test-index7"
indexType = "event"


wantList = [
            "手机", 
            "家用电器", 
            "数码", 
            "电脑办公", 
            #"钟表"
            ]

smallNotWantList = [
                    "选号中心",
                    "装宽带",
                    "办套餐",
                    "手机贴膜",
                    "数据线",
                    "手机保护套",
                    "创意配件",
                    "手机饰品",
                    "酒柜",
                    "冲印服务",
                    "手机电池",
                    "延保服务",
                    "杀毒软件",
                    "积分商品",
                    
                    "组装电脑",
                    "纸类",
                    "办公文具",
                    "学生文具",
                    "财会用品",
                    "文件管理",
                    "本册/便签",
                    "笔类",
                    "画具画材",
                    "刻录碟片/附件",
                    "上门安装",
                    "延保服务",
                    "维修保养",
                    "电脑软件",
                    "京东服务",
                    ]


smallWantList = ["洗衣机",
                 "平板电视",
                "空调",
                "冰箱",]


#es = Elasticsearch()

class JDSpider(Spider):
    name = "JDSpider"
    allowed_domains = ["jd.com"]
    start_urls = [
        'https://www.jd.com/allSort.aspx'
    ]
    logging.getLogger("requests").setLevel(logging.ERROR)  # 将requests的日志级别设成WARNING


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        """获取分类页"""
        selector = Selector(response)
        try:
            #
            #texts = selector.xpath('//div[@class="category-item m"]/div[@class="mc"]/div[@class="items"]/dl/dd/a').extract()
            texts = selector.xpath('//div[@class="category-item m"]').extract()
            
            for text in texts: 
                #productType1[0] 大分类  手机  图书等。。。。
                productType1 = re.findall(r'<span>(.*?)</span>', text)
                
                if productType1[0] not in wantList:
                    continue
                
                items = re.findall(r'<a href="(.*?)" target="_blank">(.*?)</a>', text)
            
                for item in items:
                    #productType2 小分类  羊毛衫 衬衫等。。。。
                    productType2 = item[1]
                    
                    #if productType2 in smallNotWantList:
                    #    continue
                    
                    if productType2 not in smallWantList:
                        continue
                    
                    #item[0]是各个分类的链接 如  //list.jd.com/list.html?cat=1316,1383,11928
                    if item[0].split('.')[0][2:] in key_word:
                        if item[0].split('.')[0][2:] != 'list':
                            #除去list的    其他频道页面  见key_word  channel.jd.com/1316-1384.html
                            yield Request(url='https:' + item[0], callback=self.parse_category)
                        else:
                            #产品列表的页面
                            categoriesItem = CategoriesItem()
                            categoriesItem['name'] = item[1]
                            categoriesItem['url'] = 'https:' + item[0]
                            categoriesItem['_id'] = item[0].split('=')[1].split('&')[0]
                            

                            #print "#################################"
                            #print categoriesItem['name']
                            #print categoriesItem['url']
                            #print categoriesItem['_id']
                            #print "#################################"
                            
                            yield categoriesItem
                            
                            #迭代这句
                            yield Request(url='https:' + item[0], meta={"bigType": productType1[0], "smallType": productType2}, callback=self.parse_list)
                            
                                        
            '''
            for selectorChildren in selectorList:
                
                 #print selectorChildren
                 productTypes = selectorChildren.xpath('//div[@class="mt"]/h2[@class="item-title"]/span')
                 #texts = selectorChildren.xpath('//div[@class="mc"]/div[@class="items"]/dl/dd/a').extract()
                 
                 print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                 
                 for productType in productTypes:
                     print productType
                 
                 #print productTypes

                 for productTypeAll in productTypes:
                     productType = re.findall(r'<span>(.*?)</span>', productTypeAll)
                     
                     
                     #productTypeStr = productType[0].decode('unicode_escape')
                     print '########################'
                     print productType[0]
                     print '########################'

                 print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                 
            '''
            '''
            for text in texts:
                productType = re.findall(r'<span>(.*?)</span>', text)
                
                print '########################'
                print productType
                print '########################'
                

                items = re.findall(r'<a href="(.*?)" target="_blank">(.*?)</a>', text)
                for item in items:
                    if item[0].split('.')[0][2:] in key_word:
                        if item[0].split('.')[0][2:] != 'list':
                            yield Request(url='https:' + item[0], callback=self.parse_category)
                        else:
                            categoriesItem = CategoriesItem()
                            categoriesItem['name'] = item[1]
                            categoriesItem['url'] = 'https:' + item[0]
                            categoriesItem['_id'] = item[0].split('=')[1].split('&')[0]
                            yield categoriesItem
                            yield Request(url='https:' + item[0], callback=self.parse_list)
                '''

        except Exception as e:
            print('error:', e)

        # 测试
        # yield Request(url='https://list.jd.com/list.html?cat=1315,1343,9720', callback=self.parse_list)

    def parse_list(self, response):
        """分别获得商品的地址和下一页地址"""
        
        bigType = response.meta["bigType"]
        smallType = response.meta["smallType"]
        
        
        meta = dict()
        meta['category'] = response.url.split('=')[1].split('&')[0]
        meta['bigType'] = bigType
        meta['smallType'] = smallType
        
        #print response.url.split('=')[1].split('&')[0]

        selector = Selector(response)
        texts = selector.xpath('//*[@id="plist"]/ul/li/div/div[@class="p-img"]/a').extract()
        for text in texts:
            #items https://item.jd.com/11882312022.html  产品详情页
            items = re.findall(r'<a target="_blank" href="(.*?)">', text)
            #print items[0]
            productUrl = 'https:' + items[0]
            meta['productUrl'] = productUrl
            yield Request(url=productUrl, callback=self.parse_product, meta=meta)

        # 测试
        # print('2')
        # yield Request(url='https://item.jd.hk/3460655.html', callback=self.parse_product, meta=meta)

        # next page
        next_list = response.xpath('//a[@class="pn-next"]/@href').extract()
        if next_list:
            # print('next page:', Base_url + next_list[0])
            yield Request(url=Base_url + next_list[0], callback=self.parse_list, meta={"bigType": bigType, "smallType": smallType })


    # 解析产品详情页
    def parse_product(self, response):
        """商品页获取title,price,product_id"""
        
        esSaveItem = {}
        
        global allNum
        
        bigType = response.meta["bigType"]
        smallType = response.meta["smallType"]
        productUrl = response.meta['productUrl']
        
        esSaveItem["firstType"] = bigType
        esSaveItem["secondType"] = smallType
        esSaveItem["productUrl"] = productUrl
        
        
        category = response.meta['category']
        ids = re.findall(r"venderId:(.*?),\s.*?shopId:'(.*?)'", response.text)
        if not ids:
            ids = re.findall(r"venderId:(.*?),\s.*?shopId:(.*?),", response.text)
        vender_id = ids[0][0]
        shop_id = ids[0][1]
        
        
        
        brands = response.xpath('//*[@id="parameter-brand"]/li/a//text()').extract()
        

        
        if len(brands) > 0:
        #brand = response.xpath('//div[@class="detail"]/div[@class="ETab"]/div[@class="tab-con"]/div/div[@class="p-parameter"]/div[@class="p-parameter-list"]/li/a').extract()
           #print "#### %s ### %s ### %s ###"%(bigType, smallType, brands[0])
           esSaveItem["brand"] = brands[0]
        
        #print productUrl
        
        fullName = response.xpath('//div[@class="product-intro clearfix"]/div[@class="itemInfo-wrap"]/div[@class="sku-name"]//text()').extract()[0]
        
        esSaveItem["fullName"] = fullName.strip()
        #commentCount = response.xpath('//*[@id="comment-count"]/a').extract()[0]
        
        #print "#### %s ###"%(fullName)
        
        
        details1 = response.xpath('//div[@class="detail"]/div[@class="ETab"]/div[@class="tab-con"]/div[@class="hide"]/div[@class="Ptable"]/div[@class="Ptable-item"]/dl').extract()
        
        allNum = allNum + 1
        #print details
        
        flag = False
        
        for detail in details1:
            #print detail
            ptableItems = re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', detail)
            
            for ptableItem in ptableItems:
                flag = True
                #print">>>>>>> [%s] ----------- [%s]" % (ptableItem[0], ptableItem[1])
                
                if "品牌" in ptableItem[0]:
                    esSaveItem["brand"] = ptableItem[1]
                    
                if "型号" in ptableItem[0] and "适用" not in ptableItem[0]:
                    esSaveItem["model"] = ptableItem[1]
                
            
        #没有详情  从介绍里面拿    
        #if flag == False:
        details2 = response.xpath('//div[@class="detail"]/div[@class="ETab"]/div[@class="tab-con"]/div/div[@class="p-parameter"]/ul[@class="parameter2 p-parameter-list"]').extract()
        for detail in details2:
            ptableItems = re.findall(r'<li title="(.*?)">(.*?)</li>', detail)
            for ptableItem in ptableItems:
                #print">>>>>>> [%s]" % (ptableItem[1])
                
                if flag == False:
                    if "品牌" in ptableItem[1]:
                       esSaveItem["brand"] = ptableItem[1].split('：')[1]
                    
                    if "型号" in ptableItem[1] and "适用" not in ptableItem[0]:
                       esSaveItem["model"] = ptableItem[1].split('：')[1]
                       
                if "商品名称" in ptableItem[1]:
                    esSaveItem["name"] = ptableItem[1].split('：')[1]
                       
        
        
        if esSaveItem.has_key("brand") != True:
            esSaveItem["brand"] = 'unknown'
        
        if esSaveItem.has_key("model") != True:
            #esSaveItem["model"] = 'unknown' 
            for detail in details1:
                #print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                #print detail
                #print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                ptableItems = re.findall(r'<dt>(.*?)</dt>([\s]*?)<dd class="Ptable-tips">([\s\S]*?)</dd>([\s]*?)<dd>(.*?)</dd>', detail)
                
                for ptableItem in ptableItems:
                    #print">>>>>>> [%s] ----------- [%s]----------- [%s]----------- [%s]----------- [%s]" % (ptableItem[0], ptableItem[1], ptableItem[2], ptableItem[3], ptableItem[4])
                    '''
                    if "品牌" in ptableItem[0]:
                        esSaveItem["brand"] = ptableItem[1]
                    '''    
                    if "型号" in ptableItem[0] and "适用" not in ptableItem[0]:
                        esSaveItem["model"] = ptableItem[4]
                        
        
        if esSaveItem.has_key("model") != True:
            esSaveItem["model"] = 'unknown'        
                                
                  
            
        if esSaveItem.has_key("name") != True:
            esSaveItem["name"] = esSaveItem["fullName"]   
                    
            #if ptableItems:
               #print ">>>>>>> %s"%ptableItems[0]
        print "#################   %s   #################  %s" % (allNum, productUrl)
        #print details
        #print "#################################"
        # shop
        shopItem = ShopItem()
        shopItem['shopId'] = shop_id
        shopItem['venderId'] = vender_id
        shopItem['url1'] = 'http://mall.jd.com/index-%s.html' % (shop_id)
        try:
            shopItem['url2'] = 'https:' + response.xpath('//ul[@class="parameter2 p-parameter-list"]/li/a/@href').extract()[0]
        except:
            shopItem['url2'] = shopItem['url1']

        name = ''
        if shop_id == '0':
            name = '京东自营'
        else:
            try:
                name = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li/a//text()').extract()[0]
            except:
                try:
                    name = response.xpath('//div[@class="name"]/a//text()').extract()[0].strip()
                except:
                    try:
                        name = response.xpath('//div[@class="shopName"]/strong/span/a//text()').extract()[0].strip()
                    except:
                        try:
                            name = response.xpath('//div[@class="seller-infor"]/a//text()').extract()[0].strip()
                        except:
                            name = u'京东自营'
        shopItem['name'] = name
        shopItem['_id'] = name
        yield shopItem

        productsItem = ProductsItem()
        productsItem['shopId'] = shop_id
        productsItem['category'] = category
        try:
            title = response.xpath('//div[@class="sku-name"]/text()').extract()[0].replace(u"\xa0", "").strip()
        except Exception as e:
            title = response.xpath('//div[@id="name"]/h1/text()').extract()[0]
        productsItem['name'] = title
        product_id = response.url.split('/')[-1][:-5]
        productsItem['_id'] = product_id
        productsItem['url'] = response.url

        # description
        desc = response.xpath('//ul[@class="parameter2 p-parameter-list"]//text()').extract()
        productsItem['description'] = ';'.join(i.strip() for i in desc)

        # price
        response = requests.get(url=price_url + product_id)
        price_json = response.json()
        #productsItem['reallyPrice'] = price_json[0]['p']
        #productsItem['originalPrice'] = price_json[0]['m']

        #esSaveItem['reallyPrice'] = productsItem['reallyPrice']

        # 优惠
        res_url = favourable_url % (product_id, shop_id, vender_id, category.replace(',', '%2c'))
        # print(res_url)
        response = requests.get(res_url)
        fav_data = response.json()
        if fav_data['skuCoupon']:
            desc1 = []
            for item in fav_data['skuCoupon']:
                start_time = item['beginTime']
                end_time = item['endTime']
                time_dec = item['timeDesc']
                fav_price = item['quota']
                fav_count = item['discount']
                fav_time = item['addDays']
                desc1.append(u'有效期%s至%s,满%s减%s' % (start_time, end_time, fav_price, fav_count))
            productsItem['favourableDesc1'] = ';'.join(desc1)

        if fav_data['prom'] and fav_data['prom']['pickOneTag']:
            desc2 = []
            for item in fav_data['prom']['pickOneTag']:
                desc2.append(item['content'])
            productsItem['favourableDesc1'] = ';'.join(desc2)

        data = dict()
        data['product_id'] = product_id
        
        data['esSaveItem'] = esSaveItem
        
        
        commentUrl = comment_url % (product_id, '0')
        
        
        yield productsItem
        
        

        yield Request(url=comment_url % (product_id, '0'), callback=self.parse_comments, meta=data)
        
        

    def parse_comments(self, response):
        """获取商品comment"""
        
        global actions
        global blukSize
        global indexName
        global indexType
        
        try:
            data = json.loads(response.text)
        except Exception as e:
            print('get comment failed:', e)
            return

        product_id = response.meta['product_id']
        
        esSaveItem = response.meta['esSaveItem']

        
        commentSummaryItem = CommentSummaryItem()
        commentSummary = data.get('productCommentSummary')
        commentSummaryItem['commentCount'] = commentSummary.get('commentCount')
        
        
        if esSaveItem.has_key("commentCount") != True:
            esSaveItem["commentCount"] = commentSummaryItem['commentCount']
            #esSaveItemJsonStr = json.dumps(esSaveItem).decode('unicode-escape')
            esSaveItem["timestamp"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000+0800')
            
            esId = esSaveItem['firstType']+'|'+esSaveItem['secondType']+'|'+esSaveItem['brand']+'|'+esSaveItem['name']+'|'+esSaveItem['model']
            #esSaveItemObject = json.loads(esSaveItemJsonStr)
            
            print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            print esId
            print esSaveItem
            print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            
            action = {
                "_index": indexName,
                "_type": indexType,
                "_id": esId,
                "_source": esSaveItem
                }
            
            actions.append(action)
            
            if len(actions) >= blukSize:
                #helpers.bulk(es, actions)
                actions = []
            
            #$es.index(index="test-index2",doc_type="event",id=esId,body=esSaveItem)
        
        #print "&&&&&&&&&&&&&& %s" % commentSummaryItem['commentCount']
        
        #print "################################################"
        
        yield commentSummaryItem
        
        '''
        commentSummaryItem['goodRateShow'] = commentSummary.get('goodRateShow')
        commentSummaryItem['poorRateShow'] = commentSummary.get('poorRateShow')
        commentSummaryItem['poorCountStr'] = commentSummary.get('poorCountStr')
        commentSummaryItem['averageScore'] = commentSummary.get('averageScore')
        commentSummaryItem['generalCountStr'] = commentSummary.get('generalCountStr')
        commentSummaryItem['showCount'] = commentSummary.get('showCount')
        commentSummaryItem['showCountStr'] = commentSummary.get('showCountStr')
        commentSummaryItem['goodCount'] = commentSummary.get('goodCount')
        commentSummaryItem['generalRate'] = commentSummary.get('generalRate')
        commentSummaryItem['generalCount'] = commentSummary.get('generalCount')
        commentSummaryItem['skuId'] = commentSummary.get('skuId')
        commentSummaryItem['goodCountStr'] = commentSummary.get('goodCountStr')
        commentSummaryItem['poorRate'] = commentSummary.get('poorRate')
        commentSummaryItem['afterCount'] = commentSummary.get('afterCount')
        commentSummaryItem['goodRateStyle'] = commentSummary.get('goodRateStyle')
        commentSummaryItem['poorCount'] = commentSummary.get('poorCount')
        commentSummaryItem['skuIds'] = commentSummary.get('skuIds')
        commentSummaryItem['poorRateStyle'] = commentSummary.get('poorRateStyle')
        commentSummaryItem['generalRateStyle'] = commentSummary.get('generalRateStyle')
        commentSummaryItem['commentCountStr'] = commentSummary.get('commentCountStr')
        commentSummaryItem['commentCount'] = commentSummary.get('commentCount')
        commentSummaryItem['productId'] = commentSummary.get('productId')  # 同ProductsItem的id相同
        commentSummaryItem['_id'] = commentSummary.get('productId')
        commentSummaryItem['afterCountStr'] = commentSummary.get('afterCountStr')
        commentSummaryItem['goodRate'] = commentSummary.get('goodRate')
        commentSummaryItem['generalRateShow'] = commentSummary.get('generalRateShow')
        commentSummaryItem['jwotestProduct'] = data.get('jwotestProduct')
        commentSummaryItem['maxPage'] = data.get('maxPage')
        commentSummaryItem['score'] = data.get('score')
        commentSummaryItem['soType'] = data.get('soType')
        commentSummaryItem['imageListCount'] = data.get('imageListCount')
        yield commentSummaryItem

        for hotComment in data['hotCommentTagStatistics']:
            hotCommentTagItem = HotCommentTagItem()
            hotCommentTagItem['_id'] = hotComment.get('id')
            hotCommentTagItem['name'] = hotComment.get('name')
            hotCommentTagItem['status'] = hotComment.get('status')
            hotCommentTagItem['rid'] = hotComment.get('rid')
            hotCommentTagItem['productId'] = hotComment.get('productId')
            hotCommentTagItem['count'] = hotComment.get('count')
            hotCommentTagItem['created'] = hotComment.get('created')
            hotCommentTagItem['modified'] = hotComment.get('modified')
            hotCommentTagItem['type'] = hotComment.get('type')
            hotCommentTagItem['canBeFiltered'] = hotComment.get('canBeFiltered')
            yield hotCommentTagItem

        for comment_item in data['comments']:
            comment = CommentItem()

            comment['_id'] = comment_item.get('id')
            comment['productId'] = product_id
            comment['guid'] = comment_item.get('guid')
            comment['content'] = comment_item.get('content')
            comment['creationTime'] = comment_item.get('creationTime')
            comment['isTop'] = comment_item.get('isTop')
            comment['referenceId'] = comment_item.get('referenceId')
            comment['referenceName'] = comment_item.get('referenceName')
            comment['referenceType'] = comment_item.get('referenceType')
            comment['referenceTypeId'] = comment_item.get('referenceTypeId')
            comment['firstCategory'] = comment_item.get('firstCategory')
            comment['secondCategory'] = comment_item.get('secondCategory')
            comment['thirdCategory'] = comment_item.get('thirdCategory')
            comment['replyCount'] = comment_item.get('replyCount')
            comment['score'] = comment_item.get('score')
            comment['status'] = comment_item.get('status')
            comment['title'] = comment_item.get('title')
            comment['usefulVoteCount'] = comment_item.get('usefulVoteCount')
            comment['uselessVoteCount'] = comment_item.get('uselessVoteCount')
            comment['userImage'] = 'http://' + comment_item.get('userImage')
            comment['userImageUrl'] = 'http://' + comment_item.get('userImageUrl')
            comment['userLevelId'] = comment_item.get('userLevelId')
            comment['userProvince'] = comment_item.get('userProvince')
            comment['viewCount'] = comment_item.get('viewCount')
            comment['orderId'] = comment_item.get('orderId')
            comment['isReplyGrade'] = comment_item.get('isReplyGrade')
            comment['nickname'] = comment_item.get('nickname')
            comment['userClient'] = comment_item.get('userClient')
            comment['mergeOrderStatus'] = comment_item.get('mergeOrderStatus')
            comment['discussionId'] = comment_item.get('discussionId')
            comment['productColor'] = comment_item.get('productColor')
            comment['productSize'] = comment_item.get('productSize')
            comment['imageCount'] = comment_item.get('imageCount')
            comment['integral'] = comment_item.get('integral')
            comment['userImgFlag'] = comment_item.get('userImgFlag')
            comment['anonymousFlag'] = comment_item.get('anonymousFlag')
            comment['userLevelName'] = comment_item.get('userLevelName')
            comment['plusAvailable'] = comment_item.get('plusAvailable')
            comment['recommend'] = comment_item.get('recommend')
            comment['userLevelColor'] = comment_item.get('userLevelColor')
            comment['userClientShow'] = comment_item.get('userClientShow')
            comment['isMobile'] = comment_item.get('isMobile')
            comment['days'] = comment_item.get('days')
            comment['afterDays'] = comment_item.get('afterDays')
            yield comment

            if 'images' in comment_item:
                for image in comment_item['images']:
                    commentImageItem = CommentImageItem()
                    commentImageItem['_id'] = image.get('id')
                    commentImageItem['associateId'] = image.get('associateId')  # 和CommentItem的discussionId相同
                    commentImageItem['productId'] = image.get('productId')  # 不是ProductsItem的id，这个值为0
                    commentImageItem['imgUrl'] = 'http:' + image.get('imgUrl')
                    commentImageItem['available'] = image.get('available')
                    commentImageItem['pin'] = image.get('pin')
                    commentImageItem['dealt'] = image.get('dealt')
                    commentImageItem['imgTitle'] = image.get('imgTitle')
                    commentImageItem['isMain'] = image.get('isMain')
                    yield commentImageItem

        # next page
        max_page = int(data.get('maxPage', '1'))
        if max_page > 60:
            max_page = 60
        for i in range(1, max_page):
            url = comment_url % (product_id, str(i))
            meta = dict()
            meta['product_id'] = product_id
            yield Request(url=url, callback=self.parse_comments2, meta=meta)
        '''

    def parse_comments2(self, response):
        """获取商品comment"""
        try:
            data = json.loads(response.text)
        except Exception as e:
            print('get comment failed:', e)
            return

        product_id = response.meta['product_id']

        commentSummaryItem = CommentSummaryItem()
        commentSummary = data.get('productCommentSummary')
        commentSummaryItem['goodRateShow'] = commentSummary.get('goodRateShow')
        commentSummaryItem['poorRateShow'] = commentSummary.get('poorRateShow')
        commentSummaryItem['poorCountStr'] = commentSummary.get('poorCountStr')
        commentSummaryItem['averageScore'] = commentSummary.get('averageScore')
        commentSummaryItem['generalCountStr'] = commentSummary.get('generalCountStr')
        commentSummaryItem['showCount'] = commentSummary.get('showCount')
        commentSummaryItem['showCountStr'] = commentSummary.get('showCountStr')
        commentSummaryItem['goodCount'] = commentSummary.get('goodCount')
        commentSummaryItem['generalRate'] = commentSummary.get('generalRate')
        commentSummaryItem['generalCount'] = commentSummary.get('generalCount')
        commentSummaryItem['skuId'] = commentSummary.get('skuId')
        commentSummaryItem['goodCountStr'] = commentSummary.get('goodCountStr')
        commentSummaryItem['poorRate'] = commentSummary.get('poorRate')
        commentSummaryItem['afterCount'] = commentSummary.get('afterCount')
        commentSummaryItem['goodRateStyle'] = commentSummary.get('goodRateStyle')
        commentSummaryItem['poorCount'] = commentSummary.get('poorCount')
        commentSummaryItem['skuIds'] = commentSummary.get('skuIds')
        commentSummaryItem['poorRateStyle'] = commentSummary.get('poorRateStyle')
        commentSummaryItem['generalRateStyle'] = commentSummary.get('generalRateStyle')
        commentSummaryItem['commentCountStr'] = commentSummary.get('commentCountStr')
        commentSummaryItem['commentCount'] = commentSummary.get('commentCount')
        commentSummaryItem['productId'] = commentSummary.get('productId')  # 同ProductsItem的id相同
        commentSummaryItem['_id'] = commentSummary.get('productId')
        commentSummaryItem['afterCountStr'] = commentSummary.get('afterCountStr')
        commentSummaryItem['goodRate'] = commentSummary.get('goodRate')
        commentSummaryItem['generalRateShow'] = commentSummary.get('generalRateShow')
        commentSummaryItem['jwotestProduct'] = data.get('jwotestProduct')
        commentSummaryItem['maxPage'] = data.get('maxPage')
        commentSummaryItem['score'] = data.get('score')
        commentSummaryItem['soType'] = data.get('soType')
        commentSummaryItem['imageListCount'] = data.get('imageListCount')
        yield commentSummaryItem

        for hotComment in data['hotCommentTagStatistics']:
            hotCommentTagItem = HotCommentTagItem()
            hotCommentTagItem['_id'] = hotComment.get('id')
            hotCommentTagItem['name'] = hotComment.get('name')
            hotCommentTagItem['status'] = hotComment.get('status')
            hotCommentTagItem['rid'] = hotComment.get('rid')
            hotCommentTagItem['productId'] = hotComment.get('productId')
            hotCommentTagItem['count'] = hotComment.get('count')
            hotCommentTagItem['created'] = hotComment.get('created')
            hotCommentTagItem['modified'] = hotComment.get('modified')
            hotCommentTagItem['type'] = hotComment.get('type')
            hotCommentTagItem['canBeFiltered'] = hotComment.get('canBeFiltered')
            yield hotCommentTagItem

        for comment_item in data['comments']:
            comment = CommentItem()
            comment['_id'] = comment_item.get('id')
            comment['productId'] = product_id
            comment['guid'] = comment_item.get('guid')
            comment['content'] = comment_item.get('content')
            comment['creationTime'] = comment_item.get('creationTime')
            comment['isTop'] = comment_item.get('isTop')
            comment['referenceId'] = comment_item.get('referenceId')
            comment['referenceName'] = comment_item.get('referenceName')
            comment['referenceType'] = comment_item.get('referenceType')
            comment['referenceTypeId'] = comment_item.get('referenceTypeId')
            comment['firstCategory'] = comment_item.get('firstCategory')
            comment['secondCategory'] = comment_item.get('secondCategory')
            comment['thirdCategory'] = comment_item.get('thirdCategory')
            comment['replyCount'] = comment_item.get('replyCount')
            comment['score'] = comment_item.get('score')
            comment['status'] = comment_item.get('status')
            comment['title'] = comment_item.get('title')
            comment['usefulVoteCount'] = comment_item.get('usefulVoteCount')
            comment['uselessVoteCount'] = comment_item.get('uselessVoteCount')
            comment['userImage'] = 'http://' + comment_item.get('userImage')
            comment['userImageUrl'] = 'http://' + comment_item.get('userImageUrl')
            comment['userLevelId'] = comment_item.get('userLevelId')
            comment['userProvince'] = comment_item.get('userProvince')
            comment['viewCount'] = comment_item.get('viewCount')
            comment['orderId'] = comment_item.get('orderId')
            comment['isReplyGrade'] = comment_item.get('isReplyGrade')
            comment['nickname'] = comment_item.get('nickname')
            comment['userClient'] = comment_item.get('userClient')
            comment['mergeOrderStatus'] = comment_item.get('mergeOrderStatus')
            comment['discussionId'] = comment_item.get('discussionId')
            comment['productColor'] = comment_item.get('productColor')
            comment['productSize'] = comment_item.get('productSize')
            comment['imageCount'] = comment_item.get('imageCount')
            comment['integral'] = comment_item.get('integral')
            comment['userImgFlag'] = comment_item.get('userImgFlag')
            comment['anonymousFlag'] = comment_item.get('anonymousFlag')
            comment['userLevelName'] = comment_item.get('userLevelName')
            comment['plusAvailable'] = comment_item.get('plusAvailable')
            comment['recommend'] = comment_item.get('recommend')
            comment['userLevelColor'] = comment_item.get('userLevelColor')
            comment['userClientShow'] = comment_item.get('userClientShow')
            comment['isMobile'] = comment_item.get('isMobile')
            comment['days'] = comment_item.get('days')
            comment['afterDays'] = comment_item.get('afterDays')
            yield comment

            if 'images' in comment_item:
                for image in comment_item['images']:
                    commentImageItem = CommentImageItem()
                    commentImageItem['_id'] = image.get('id')
                    commentImageItem['associateId'] = image.get('associateId')  # 和CommentItem的discussionId相同
                    commentImageItem['productId'] = image.get('productId')  # 不是ProductsItem的id，这个值为0
                    commentImageItem['imgUrl'] = 'http:' + image.get('imgUrl')
                    commentImageItem['available'] = image.get('available')
                    commentImageItem['pin'] = image.get('pin')
                    commentImageItem['dealt'] = image.get('dealt')
                    commentImageItem['imgTitle'] = image.get('imgTitle')
                    commentImageItem['isMain'] = image.get('isMain')
                    yield commentImageItem

