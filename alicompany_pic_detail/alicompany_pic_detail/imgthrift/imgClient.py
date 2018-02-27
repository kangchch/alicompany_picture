#!/bin/env python
#encoding=utf-8
#-*- coding:utf-8-*-

from Img.pic import FileStorageServiceThrift
from Img.pic.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import requests
import pdb
import logging


class ImgClient():
    def __init__(self, ip, port):
        self.ip =ip
        self.port = port
        # self.logger = logging.getLogger('pic_detail')
    def download_img(self, url):
        #pdb.set_trace()
        response = requests.get(url, stream=True)
        return response.content
    def getHcImgUrl(self, url):
        #pdb.set_trace()
        try:
            socket = TSocket.TSocket(self.ip, self.port) 
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = FileStorageServiceThrift.Client(protocol)
            socket.setTimeout(7000);
            #pdb.set_trace()
            transport.open()
            fileInfo = FileInfo()
            fileInfo.fileName = url.split('/')[-1:][0]
            fileInfo.fileContext = self.download_img(url)
            result = client.createFile([fileInfo])
            transport.close()
            # self.logger.info("get hc url : %s  From url: %s Done" % (result[0].fileUrl, url))
            # return result[0].fileUrl.split('/')[-1:][0]
            return result[0].fileUrl
        except Exception, e:
            # self.logger.error("get hc url error From url: %s, errmsg: %s" % (url, e,))
            return ""

if __name__ == "__main__":

    client = ImgClient("192.168.245.31", 8899)
    result = client.getHcImgUrl('http://bimg.c.aliimg.com/img/ibank/2013/709/982/999289907_1436807694.jpg')
    print(result)
