
分为两个抓取程序
oracle：cor_website_move , ali_product_pic, 
mongo: m1688-> pic_content_tbl, m1688-> pic_detail_tbl
一、抓取json页面：
    从oracle库（cor_website_move）查找 search_listpage_state状态为4的 website 拼接json页面url进行抓取，保存到mongo库pic_content_tbl
二、抓取相册相片：
    从mongo库pic_content_tbl取status为0的信息拼接图片url进行抓取，获取到图片地址后
        上传thrift服务器换成hc360域名，下载下来
        保存到mongo pic_detail_tbl,
        更新mongo-> pic_content_tbl status = 1
        插入oracle-> ali_product_pic
        更新oracle-> cor_website_move 中 search_listpage_state状态为1 表示相册抓取完毕

    注意：更新保存时的状态控制
        
