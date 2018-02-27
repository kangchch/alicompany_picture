# -*- coding:utf-8 -*-

import scrapy
import re
import json
from copy import copy
import traceback
from scrapy import log
from alicompany_pic.items import AlicompanyPicItem
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


class AlicompanyPicSpider(scrapy.Spider):
    name = "pic"

    def __init__(self, settings, *args, **kwargs):
        super(AlicompanyPicSpider, self).__init__(*args, **kwargs)
        self.settings = settings

        try:
            mongo_info = settings['MONGO_INFO']
            self.mongo_db = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).m1688
            self.oracle_db = cx_Oracle.connect(self.settings.get('ORACLE_DB_STR'))
            self.oracle_cur = self.oracle_db.cursor()
        except Exception, e:
            self.log('connect mongo failed! (%s)' % (str(e)), level=log.CRITICAL)
            raise scrapy.exceptions.CloseSpider('initialization mongo error (%s)' % (str(e)))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def start_requests(self):

        try:
            ## get all search_listpage_state=4 website
            sql_m = self.settings.get('SQL_GET_KEYWORDS')
            oracle_handle = self.oracle_cur.execute(sql_m)
            sites = oracle_handle.fetchall()
            self.oracle_cur.close()

            for index, site in enumerate(sites):

                username = site[0].split('//')[1].split('.')[0]
                flask_url = ''.join(['http://192.168.90.36:8080/GetMemberid?username=', username])
                r = requests.get(flask_url)

                if r.status_code != 200:
                    self.log('[status_code] %d, flask_url: %s, [%s]' % (r.status_code, flask_url, str(e)), level=log.ERROR)
                    continue
                try:
                    json_item = json.loads(r.text)
                except Exception, e:
                    self.log('json flask prase failed! body=%s' % (r.text), level=log.ERROR)
                    continue
                memberid = json_item.get('memberid', 0)
                if memberid == 0:
                    continue
                memberids = list()
                memberids.append(memberid)

                for memberid in memberids:
                    picman_url = ''.join(['https://picman.1688.com/open/ajax/RecommendAlbumDetailList.json?memberId=', memberid, '&hasAlbums=true&1'])

                    ret_item = AlicompanyPicItem()
                    ret_item['update_item'] = {}
                    i = ret_item['update_item']
                    i['memberid'] = memberid
                    i['picman_url'] = picman_url
                    i['website'] = site[0]
                    i['username'] = username
                    i['appid'] = site[1]
                    meta = {'item': ret_item, 'dont_retry': True}
                    self.log('spider flask_url=%s and new picman_url=%s' % (flask_url, picman_url), level=log.INFO)
                    yield scrapy.Request(url = picman_url, meta = meta, callback = self.picman_parse, dont_filter = True)

            ##@__test__
            # memberids = ['langjinsongte']
            # website = 'http://langjinsongte.1688.com'
            # for memberid in memberids:
                # picman_url = ''.join(['https://picman.1688.com/open/ajax/RecommendAlbumDetailList.json?memberId=', memberid, '&hasAlbums=true&1'])
                # ret_item = AlicompanyPicItem()
                # ret_item['update_item'] = {}
                # i = ret_item['update_item']
                # i['memberid'] = memberid
                # i['website'] = website
                # i['username'] = 'langjinsongte'
                # meta = {'item': ret_item, 'dont_retry': True}
                # self.log('spider flask_url= and new picman_url=%s' % (picman_url), level=log.INFO)
                # yield scrapy.Request(url = picman_url, meta = meta, callback = self.picman_parse, dont_filter = True)
        except:
            self.log('start_request error! (%s)' % (str(traceback.format_exc())), level=log.INFO)

    ## 抓picman  json页面
    def picman_parse(self, response):

        ret_item = response.meta['item']
        i = ret_item['update_item']
        picman_url = response.url

        if response.status != 200 or len(response.body) <= 0:
            self.log('fetch failed ! status = %d, picman_url=%s' % (response.status, picman_url), level = log.WARNING)
            if response.status == 302 and response.headers.get('Location', '').find('vcode') > 0:
                return
            else:
                yield ret_item

        ## parse json
        page_source = json.loads(response.body_as_unicode())
        sites = page_source['dataList']['albums']
        i['total'] = page_source['total']
        if page_source['total'] == 0: 
            self.log('total is 0 %s' % (response.url), level=log.WARNING)
            yield ret_item
            # return
        for site in sites:
            i['count'] = site['count']
            if i['count'] == 0:
                self.log('count is 0 %s' % (response.url), level=log.WARNING)
                yield ret_item
            i['albumId'] = site['id']
            i['title'] = site['title']

            self.log('memberid=%s, id=%s, title=%s, count=%s' % (i['memberid'], i['albumId'], i['title'], i['count']), level=log.INFO)
            yield ret_item

