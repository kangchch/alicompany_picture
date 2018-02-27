namespace java com.hc360.rsf.imgup.thrift
struct FileInfo{
1: string fileUrl,                     // 存储后图片的URL或路径，由isReturnUrl属性决定是否带有图片存储的域名（即http://img008.hc360.cn等）
2: string fileName,                // 图片的名字（如a.jpg）
3: binary fileContext,            // 图片字节流
4: list<string> gmFormat,      // 暂时还未被使用
5: i32 operateResult,             // 此次操作是否成功，0表示文件操作结果成功  -1表示文件操作结果异常
6: string businTyp,                // 调用系统的名称（如detail、my等），没有限制
7: string isReturnUrl,             // 标示fileUrl是否为URL（即是否携带域名）   NOT_URL  表示fileUrl不带域名（如g8/M03/62/2A/wKhQtVOIZF-EK8twAAAAAFAGf4Q397.jpg）；其他值 表示fileUrl带域名（即http://img008.hc360.cn/g8/M03/62/2A/wKhQtVOIZF-EK8twAAAAAFAGf4Q397.jpg）
}

service FileStorageServiceThrift {

/**

* 上传图片

*@param fileList  图片信息集合，每个图片对象（FileInfo）只使用了类的四个属性（fileContext、fileName、businTyp、isReturnUrl）

*@return 返回图片集合，每个图片对象（FileInfo，重新声明的）只包含了类的三个属性（fileUrl、fileName、operateResult），fileName为传入的图片名称（如a.jpg）

**/
list<FileInfo> createFile(1:list<FileInfo> fileList),

/**

* 删除图片

*@param fileList  图片信息集合，每个图片对象（FileInfo）只使用了类的一个属性（fileUrl 需要带域名，图片的绝对URL）

*@return 返回图片集合，每个图片对象（FileInfo，重新声明的）只包含了类的两个属性（fileUrl、operateResult），fileUrl 为传入的图片URL

**/

list<FileInfo> removeFile(1:list<FileInfo> fileList),

/**

* 下载图片

*@param fileList  图片信息集合，每个图片对象（FileInfo）只使用了类的一个属性（fileUrl 带不带域名都可）

*@return 返回图片集合，每个图片对象（FileInfo，重新声明的）只包含了类的三个属性（fileUrl、fileContext、operateResult），fileUrl 为传入的图片URL

**/

list<FileInfo> findFile(1:list<FileInfo> fileList),

 }
