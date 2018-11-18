import ftplib
import os

CONST_HOST = "192.168.0.176"
CONST_USERNAME = "Administrator"
CONST_PWD = "Gut102015"
CONST_BUFFER_SIZE = 8192


class MyFtp(ftplib.FTP):
    def __init__(self, ftp_host, ftp_port, ftp_username, ftp_password):
        super().__init__()
        self.encoding = 'GBK'
        self.ftp_host = ftp_host
        self.ftp_port = ftp_port
        self.ftp_username = ftp_username
        self.ftp_password = ftp_password

    def ftp_login(self):
        try:
            self.connect(self.ftp_host, self.ftp_port, 3)
            print(self.welcome)
        except Exception as e:
            print('连接失败：', e)
        try:
            self.login(self.ftp_username, self.ftp_password)
            print('已登录FTP服务器')
            return 1000
        except Exception as e:
            print('登录失败：', e)

    def ftp_disconnect(self):
        try:
            self.quit()
            print('断开连接')
        except Exception as e:
            print(e)

    def ftp_getfiles(self, path=''):
        try:
            self.dir(path)
            list_file = self.nlst(path)
            return list_file
        except Exception as e:
            print("查看目录失败：", e)

    def upload_file(self, remote_path, local_path):
        try:
            buf_size = 8192
            fp = open(local_path, 'rb')
            self.storbinary('STOR ' + remote_path, fp, buf_size)
            self.set_debuglevel(0)
            fp.close()
            self.quit()
            return 1000
        except Exception as e:
            print('上传失败：', e)
            return 1001

    def download_file(self, remote_path, local_path):
        """
        :param ftp:
        :param remoteRelPath: 服务端文件的相对路径,含文件后缀，如/srcDir/file.txt
        :param localAbsDir: 客户端文件夹的绝对路径，如E:/FTP/downDir/
        :return:
        """
        print("start download file by use FTP...")
        try:
            handle = open(local_path, "wb")
            self.retrbinary("RETR %s" % remote_path, handle.write, 8192)
            handle.close()
            self.quit()
            return 1000
        except Exception as e:
            print('下载失败：', e)
            return 1001


if __name__ == '__main__':
    ftp = MyFtp()
    ftp.ftp_login()
    ftp.dir()
    ftp.upload_file('viewer_md5.json', r'D:\Project\PythonProjects\Py_Uploader\viewer_md5.json')
