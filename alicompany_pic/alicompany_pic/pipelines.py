# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import pymongo
import datetime
from scrapy import log


class AlicompanyPicPipeline(object):

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=crawler.settings
        )

    def open_spider(self, spider):
        mongo_info = settings.get('MONGO_INFO', {})
        if not mongo_info:
            self.mongo_db = pymongo.MongoClient('192.168.60.64', 10010).m1688
        else:
            self.mongo_db = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).m1688

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        # return item
        i = item['update_item']
        i['status'] = 0
        i['insert_time'] = datetime.datetime.now()
        # print i

        try:
            if i['total'] == 0 or i['count'] == 0:
                return
            if '_id' in i:
                del i['_id']
            self.mongo_db.pic_content_tbl.insert_one(i)
            spider.log('piplines insert mongo succed. memberid:%s' % (i['memberid']), level=log.INFO)
        except Exception, e:
            spider.log('insert mongo failed! memberid=%s (%s)' % (i['memberid'], str(e)), level=log.ERROR)

        ## update cor_website_move search_listpage_status=1
        # sql = "update cor_website_move set SEARCH_LISTPAGE_STATUS=1 where id=:1"
        # self.oracle_db_cur.execute(sql, (i['appid'],))
        # self.oracle_db.commit()
        # spider.log('update oracle succeed! appid:%s,)' % (i['appid']),level=log.INFO) 
