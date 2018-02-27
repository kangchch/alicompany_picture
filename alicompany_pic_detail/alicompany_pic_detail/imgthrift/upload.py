#!/usr/bin/env python
#encoding=gb18030
import sys
sys.path.append('Img')
from pic.FileStorageServiceThrift import *
from pic.ttypes import *
from pic.constants import *
# thrift module
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import requests

try:
    str = ''
    r = requests.get('http://bimg.c.aliimg.com/img/ibank/2013/709/982/999289907_1436807694.jpg', stream=True)
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            str += chunk
except Exception, e:
    print str(e)
    exit(1)

try:
    fileinfo = FileInfo()
    fileinfo.fileName = '0.jpg'
    fileinfo.fileContext = str
    fileinfo.businTyp = '3y'

    # transport = TSocket.TSocket('192.168.45.117', 8333)
    # transport = TSocket.TSocket('192.168.44.74', 8332)
    transport = TSocket.TSocket('192.168.245.31', 8899)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Client(protocol)
    transport.open()
    result = client.createFile([fileinfo])
    transport.close()
    print result[0].fileUrl
except Thrift.TException, tx:
    print '%s' %(tx.message)
