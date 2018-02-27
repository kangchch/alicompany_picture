# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
import pymongo
import datetime
import cx_Oracle
from scrapy import log
import sys
reload(sys)
sys.setdefaultencoding('gbk')


class AlicompanyPicDetailPipeline(object):

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
            self.mongo_db = pymongo.MongoClient('192.168.60.65', 10010).m1688
        else:
            self.mongo_db = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).m1688

        self.oracle_db = cx_Oracle.connect(self.settings.get('ORACLE_DB_STR'))
        self.oracle_db_cur = self.oracle_db.cursor()

    def close_spider(self, spider):
        self.oracle_db_cur.close()

    def process_item(self, item, spider):
        # return item
        i = item['update_item']
        title = i['title']
        i['status'] = 0
        i['insert_time'] = datetime.datetime.now()
        productid = '_'.join([str(i['appid']), i['title']])
        # if self.count_false == True:
            # print 22222
            # self.mongo_db.pic_content_tbl.update_one({'status': 0}, {'$set': {'status': 1}})
            # return
        try:
            self.mongo_db.pic_detail_tbl.insert_one(i)
            self.mongo_db.pic_content_tbl.update_one({'title': title}, {'$set': {'status': 1}})

            sql = u"insert into ali_product_pic (id, picname, picurl, productid, pubdate, title, appid, pim_id \
                    ) values(ali_product_pic_seq.nextval, :1, :2, :3, :4, :5, :6, :7)"
            self.oracle_db_cur.execute(sql, (i['hc_pic_url'], i['picture_src'], productid,datetime.datetime.now(), i['picture_name'], i['appid'], 0))
            self.oracle_db.commit()
            spider.log('insert oracle succeed! appid:%s,)' % (i['appid']),level=log.INFO) 
        except pymongo.errors.DuplicateKeyError:
            pass
        except Exception, e:
            spider.log('insert mongo failed! username:%s, %s)' % (i['username'], str(e)), level=log.ERROR)

        ## update cor_website_move search_listpage_status=1
        sql = "update cor_website_move set SEARCH_LISTPAGE_STATUS=1 where id=:1"
        self.oracle_db_cur.execute(sql, (i['appid'],))
        self.oracle_db.commit()
        spider.log('update oracle succeed! appid:%s,)' % (i['appid']),level=log.INFO) 

        # if self.mongo_db.pic_detail_tbl.find({'picture_src': {'$exists': true}})
