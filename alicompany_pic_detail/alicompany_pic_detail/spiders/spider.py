# -*- coding:utf-8 -*-
from scrapy.selector import Selector
import scrapy
import re
import json
from copy import copy
import traceback
from scrapy import log
from alicompany_pic_detail.items import AlicompanyPicDetailItem
import time
import datetime
import sys
import logging
import random
from scrapy.conf import settings
import cx_Oracle
import pymongo
import json
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

import os
# os.system('export LANG=zh_CN.GB18030')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'


class AlicompanyPicDetailSpider(scrapy.Spider):
    name = "pic_detail"

    def __init__(self, settings, *args, **kwargs):
        super(AlicompanyPicDetailSpider, self).__init__(*args, **kwargs)
        self.settings = settings

        try:
            mongo_info = settings['MONGO_INFO']
            self.mongo_db = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).m1688
        except Exception, e:
            self.log('connect mongo failed! (%s)' % (str(e)), level=log.CRITICAL)
            raise scrapy.exceptions.CloseSpider('initialization mongo error (%s)' % (str(e)))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def start_requests(self):

        try:
            exists = self.mongo_db.pic_content_tbl.find({'count': {'$exists':False}})
            if exists.count() > 0:
                self.mongo_db.pic_content_tbl.remove({'count': {'$exists':False}})

            sites = self.mongo_db.pic_content_tbl.find({'status': 0},{'website': 1, 'albumId': 1, 'count': 1, 'title': 1, 'username': 1, 'appid': 1})
            if sites.count() == 0:
                self.log('no need spider', level=log.INFO)
                return
            for index, site in enumerate(sites):
                website = site['website']
                server_name = website.split('//')[1]
                title = site['title']
                count = site['count']
                username = site['username']
                appid = site['appid']
                albumId = site['albumId']
                for c in range(1,count+1):

                    picture_url = ''.join([website + '/page/albumdetail.htm?tbpm=3&_server_name=' + server_name + '&albumId=' + str(albumId) + '&imageNum=' + str(c)])
                    meta = {'website': website, 'appid': appid, 'server_name': server_name, 'albumId': albumId, 'count': count, 'title': title, 'username': username, 'dont_retry': True}
                    self.log('spider new picture_url=%s' % (picture_url), level=log.INFO)
                    yield scrapy.Request(url = picture_url, meta = meta, callback = self.picture_parse, dont_filter = True)
        except:
            self.log('start_request error! (%s)' % (str(traceback.format_exc())), level=log.INFO)

    ## picture_detail  页面
    def picture_parse(self, response):

        sel = Selector(response)
        ret_item = AlicompanyPicDetailItem()
        ret_item['update_item'] = {}
        # ret_item = response.meta['item']
        i = ret_item['update_item']
        picture_url = response.url
        server_name = response.meta['server_name']
        albumId = response.meta['albumId']
        count = response.meta['count']

        i['title'] = response.meta['title']
        i['website'] = response.meta['website']
        i['albumId'] = response.meta['albumId']
        i['username'] = response.meta['username']
        i['picture_url'] = response.url
        i['appid'] = response.meta['appid']
        i['count'] = response.meta['count']

        if response.status != 200 or len(response.body) <= 0:
            self.log('fetch failed ! status = %d, picture_url=%s' % (response.status, picture_url), level = log.WARNING)
            if response.status == 302 and response.headers.get('Location', '').find('vcode') > 0:
                self.log('spider failed status = %d' % (response.status), level=log.WARNING)
                return
            else:
                self.log('else failed status = %d' % (response.status), level=log.WARNING)
                yield ret_item

        ## parse 
        page_source = response.body_as_unicode()
        pictures = sel.xpath("//div[@class='img-wrapper']")
        for picture in pictures:
            picture_src = picture.xpath("./img/@src").extract()
            i['picture_src'] = picture_src[0] if picture_src else ''
            ## picture_name -> oracle ali_product_pic title
            picture_name = picture.xpath("./img/@alt").extract()
            picture_name = picture_name[0] if picture_name else ''
            i['picture_name'] = picture_name.split(" ")[1]
            # print i['appid'], ' ', i['title'], ' ', i['picture_src'], '  ', i['picture_name']

            # self.log('picture_url=%s, server_name=%s, albumId=%s, count=%s, picture_name=%s' % (picture_url, server_name, albumId, count, i['picture_name']), level=log.INFO)
            meta = {'item': ret_item, 'dont_retry': True}
            yield scrapy.Request(url = i['picture_src'], meta = meta, callback = self.pic_thrift, dont_filter = True)

    ## 上传图片
    def pic_thrift(self, response):

        ret_item = response.meta['item']
        i = ret_item['update_item']

        import sys
        from alicompany_pic_detail.imgthrift.imgClient import ImgClient

        # client = ImgClient("192.168.120.47", 8332)
        client = ImgClient("192.168.245.31", 8899)
        result = client.getHcImgUrl(i['picture_src'])
        i['hc_pic_url'] = result.split('.cn/')[1]
        print 'hc_url', ' ', i['hc_pic_url']
        self.log('appid=%s, picture_url=%s, username=%s, albumId=%s, count=%s, picture_name=%s, hc_pic_url=%s' % (
            i['appid'], i['picture_url'], i['username'], i['albumId'], i['count'], i['picture_name'], i['hc_pic_url']), level=log.INFO)
        yield ret_item



