from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from tools import ftp_helper

import os
import json


class CheckUpdate(QThread):
    signal_server_empty = pyqtSignal()
    signal_already_down = pyqtSignal()
    signal_server_out = pyqtSignal()
    signal_downpack = pyqtSignal(str)

    def __init__(self, project_name, project_path):  # 项目名/项目路径
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path

    def __del__(self):
        self.wait()

    def run(self):
        self.down_update_pack()

    def down_update_pack(self):
        update_pack_path = os.path.join(self.project_path, 'update')
        update_pack_path = os.path.abspath(update_pack_path)
        while True:
            if not os.listdir(update_pack_path):
                print('empty')
                my_ftp = ftp_helper.MyFtp()
                if my_ftp.ftp_login() == 1000:
                    file_list = my_ftp.ftp_getfiles()
                    for i in file_list:
                        if self.project_name not in i:
                            file_list.remove(i)
                    if len(file_list) == 0:
                        self.signal_server_empty.emit()  # 服务器上没有对应项目的更新包
                        break
                    else:
                        file_list.sort()
                        update_pack = file_list[0]
                        if my_ftp.download_file(update_pack, (os.path.join(update_pack_path, update_pack))) == 1000:
                            self.signal_downpack.emit(update_pack)  # 下载更新包：update_pack 完成
                else:
                    self.signal_server_out.emit()

            else:
                print('not empty')
                pack_list = []
                for a in os.listdir(update_pack_path):
                    pack_list.append(a)
                pack_list.sort()
                pack = pack_list[-1]
                my_ftp = ftp_helper.MyFtp()
                if my_ftp.ftp_login() == 1000:
                    file_list = my_ftp.ftp_getfiles()
                    for j in file_list:
                        if self.project_name not in j:
                            file_list.remove(j)
                    if len(file_list) == 0:
                        self.signal_server_empty.emit()  # 服务器上没有对应项目的更新包
                        break
                    else:
                        file_list.sort()
                        temp = file_list.index(pack)
                        if file_list[temp] == file_list[-1]:
                            self.signal_already_down.emit()  # 服务器上没有新的更新包
                            break
                        else:
                            update_pack = file_list[temp + 1]
                            if my_ftp.download_file(update_pack, (os.path.join(update_pack_path, update_pack))) == 1000:
                                self.signal_downpack.emit(update_pack)  # 下载更新包：update_pack 完成
                else:
                    self.signal_server_out.emit()


class SetupUpdate(QThread):
    signal_uptodate = pyqtSignal()

    def __init__(self, project_name, project_path):  # 项目名/项目路径
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path

    def __del__(self):
        self.wait()

    def run(self):
        version_file = os.path.join(self.project_path, self.project_name)
        version_file = os.path.abspath(version_file)  # 版本信息文件

        update_pack_path = os.path.join(self.project_path, 'update')
        update_pack_path = os.path.abspath(update_pack_path)  # 更新包文件夹

        temp_path = os.path.join(self.project_path, 'temp')
        temp_path = os.path.abspath(temp_path)  # 临时解压地址

        pack_list = []

        if os.path.exists(version_file):
            with open(version_file, 'r') as vf:
                version_json = vf.read()
                version_dic = json.loads(version_json)
            current_version = version_dic['current_version']
            for pack in os.listdir(update_pack_path):
                pack_list.append(pack)
            pack_list.sort()
            if current_version == pack_list[-1]:
                self.signal_uptodate.emit()
            else:
                temp = pack_list.index(current_version)
                pack_list = pack_list[temp+1:]
        else:
            for pack in os.listdir(update_pack_path):
                pack_list.append(pack)
            pack_list.sort()

        while True:
            if len(pack_list) > 0:
                p = pack_list.pop(0)
                pack_zip = os.path.join(update_pack_path, p)
            else:
                self.signal_uptodate.emit()