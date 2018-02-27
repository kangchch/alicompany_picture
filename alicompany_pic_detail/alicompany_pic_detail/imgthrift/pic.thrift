namespace java com.hc360.rsf.imgup.thrift
struct FileInfo{
1: string fileUrl,                     // �洢��ͼƬ��URL��·������isReturnUrl���Ծ����Ƿ����ͼƬ�洢����������http://img008.hc360.cn�ȣ�
2: string fileName,                // ͼƬ�����֣���a.jpg��
3: binary fileContext,            // ͼƬ�ֽ���
4: list<string> gmFormat,      // ��ʱ��δ��ʹ��
5: i32 operateResult,             // �˴β����Ƿ�ɹ���0��ʾ�ļ���������ɹ�  -1��ʾ�ļ���������쳣
6: string businTyp,                // ����ϵͳ�����ƣ���detail��my�ȣ���û������
7: string isReturnUrl,             // ��ʾfileUrl�Ƿ�ΪURL�����Ƿ�Я��������   NOT_URL  ��ʾfileUrl������������g8/M03/62/2A/wKhQtVOIZF-EK8twAAAAAFAGf4Q397.jpg��������ֵ ��ʾfileUrl����������http://img008.hc360.cn/g8/M03/62/2A/wKhQtVOIZF-EK8twAAAAAFAGf4Q397.jpg��
}

service FileStorageServiceThrift {

/**

* �ϴ�ͼƬ

*@param fileList  ͼƬ��Ϣ���ϣ�ÿ��ͼƬ����FileInfo��ֻʹ��������ĸ����ԣ�fileContext��fileName��businTyp��isReturnUrl��

*@return ����ͼƬ���ϣ�ÿ��ͼƬ����FileInfo�����������ģ�ֻ����������������ԣ�fileUrl��fileName��operateResult����fileNameΪ�����ͼƬ���ƣ���a.jpg��

**/
list<FileInfo> createFile(1:list<FileInfo> fileList),

/**

* ɾ��ͼƬ

*@param fileList  ͼƬ��Ϣ���ϣ�ÿ��ͼƬ����FileInfo��ֻʹ�������һ�����ԣ�fileUrl ��Ҫ��������ͼƬ�ľ���URL��

*@return ����ͼƬ���ϣ�ÿ��ͼƬ����FileInfo�����������ģ�ֻ����������������ԣ�fileUrl��operateResult����fileUrl Ϊ�����ͼƬURL

**/

list<FileInfo> removeFile(1:list<FileInfo> fileList),

/**

* ����ͼƬ

*@param fileList  ͼƬ��Ϣ���ϣ�ÿ��ͼƬ����FileInfo��ֻʹ�������һ�����ԣ�fileUrl �������������ɣ�

*@return ����ͼƬ���ϣ�ÿ��ͼƬ����FileInfo�����������ģ�ֻ����������������ԣ�fileUrl��fileContext��operateResult����fileUrl Ϊ�����ͼƬURL

**/

list<FileInfo> findFile(1:list<FileInfo> fileList),

 }
