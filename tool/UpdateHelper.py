import json
import os
import shutil
import zipfile

from PyQt5.QtCore import *

from tool import FTPHelper


class CheckUpdate(QThread):
    signal_server_empty = pyqtSignal()
    signal_no_latest_pack = pyqtSignal()
    signal_server_outline = pyqtSignal()
    signal_finish_down = pyqtSignal(str)

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
        if not os.path.exists(update_pack_path):
            os.mkdir(update_pack_path)

        while True:
            if not os.listdir(update_pack_path):
                print('empty')
                my_ftp = FTPHelper.MyFtp('172.16.1.156', 21, 'Administrator', '123456')
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
                            self.signal_finish_down.emit(update_pack)  # 下载更新包：update_pack 完成
                else:
                    self.signal_server_outline.emit()

            else:
                print('not empty')
                local_pack_list = []
                for a in os.listdir(update_pack_path):
                    local_pack_list.append(a)
                local_pack_list.sort()
                local_latest_pack = local_pack_list[-1]
                my_ftp = FTPHelper.MyFtp('172.16.1.156', 21, 'Administrator', '123456')
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
                        if local_latest_pack not in file_list:
                            update_pack = file_list[0]
                            if my_ftp.download_file(update_pack, (os.path.join(update_pack_path, update_pack))) == 1000:
                                self.signal_finish_down.emit(update_pack)  # 下载更新包：update_pack 完成
                        else:
                            temp = file_list.index(local_latest_pack)
                            if file_list[temp] == file_list[-1]:
                                self.signal_no_latest_pack.emit()  # 服务器上没有新的更新包
                                break
                            else:
                                update_pack = file_list[temp + 1]
                                if my_ftp.download_file(update_pack, (os.path.join(update_pack_path, update_pack))) == 1000:
                                    self.signal_finish_down.emit(update_pack)  # 下载更新包：update_pack 完成
                else:
                    self.signal_server_outline.emit()

        if os.path.exists(os.path.join(self.project_path, 'version.json')):
            with open(os.path.join(self.project_path, 'version.json')) as vf:
                version_json = vf.read()
                version_dic = json.loads(version_json)
            current_version = version_dic['current_version']


class SetupUpdate(QThread):
    signal_uptodate = pyqtSignal()
    signal_copyfile = pyqtSignal(str)

    def __init__(self, project_name, project_path):  # 项目名/项目路径
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path

    def __del__(self):
        self.wait()

    def run(self):
        # version_file = os.path.join(self.project_path, self.project_name)
        version_file = os.path.join(self.project_path, 'version.json')
        version_file = os.path.abspath(version_file)  # 版本信息文件

        update_pack_path = os.path.join(self.project_path, 'update')
        update_pack_path = os.path.abspath(update_pack_path)  # 更新包文件夹

        temp_path = os.path.join(self.project_path, 'temp')
        temp_path = os.path.abspath(temp_path)  # 临时解压地址

        pack_list = []
        version_dic = {}

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
                version = p
                shutil.rmtree(temp_path)
                os.mkdir(temp_path)
                pack_zip = os.path.join(update_pack_path, p)
                zp = zipfile.ZipFile(pack_zip, 'r')
                zp.extractall(temp_path)
                zp.close()

                update_file = os.path.join(temp_path, (self.project_name + '_update.json'))
                with open(update_file, 'r') as uf:
                    update_json = uf.read()
                update_dic = json.loads(update_json)

                for f in update_dic:
                    index1 = f.find('Project')  # 'Project'索引, udate_dic: D:\Project\UnigineProjects\Qt_UI_25\bin\log
                    # .html
                    f1 = f[index1:]
                    origin_file = os.path.join(temp_path, f1)
                    index2 = f.find(self.project_name)
                    f2 = f[index2:]
                    destination_file = os.path.join(self.project_path, f2)
                    destination_folder = os.path.dirname(destination_file)
                    if not os.path.exists(destination_folder):
                        os.mkdir(destination_folder)
                    shutil.copyfile(origin_file, destination_file)
                    self.signal_copyfile.emit(os.path.basename(destination_file))  # 复制文件

                version_dic['current_version'] = version
                save_version_json = json.dumps(version_dic)
                with open(version_file, 'w') as wvf:
                    wvf.write(save_version_json)
            else:
                self.signal_uptodate.emit()  # 已为最新版本
                break


class Update(QThread):
    signal_server_outline = pyqtSignal()
    signal_server_empty = pyqtSignal()
    signal_already_uptodate = pyqtSignal()
    signal_update_detected = pyqtSignal(list)

    def __init__(self, project_name, project_path):  # 项目名/项目路径
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path

    def __del__(self):
        self.wait()

    def run(self):
        version_file = os.path.join(self.project_path, 'version.json')
        version_file = os.path.abspath(version_file)  # 版本信息文件
        if os.path.exists(version_file):
            with open(version_file, 'r') as vf:
                version_json = vf.read()
                version_dic = json.loads(version_json)
            current_version = version_dic['current_version']
        else:
            current_version = None

        update_pack_path = os.path.join(self.project_path, 'update')
        update_pack_path = os.path.abspath(update_pack_path)  # 更新包文件夹
        if not os.path.exists(update_pack_path):
            os.mkdir(update_pack_path)

        temp_path = os.path.join(self.project_path, 'temp')
        temp_path = os.path.abspath(temp_path)  # 临时解压地址
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        my_ftp = FTPHelper.MyFtp('172.16.1.156', 21, 'Administrator', '123456')
        version_list = []
        while True:
            if my_ftp.ftp_login() == 1000:
                pack_list = my_ftp.ftp_getfiles()
                for i in pack_list:
                    if i.startswith(self.project_name):
                        version_list.append(i)
                if len(version_list) > 0:
                    version_list.sort()
                else:
                    self.signal_server_empty.emit()  # 服务器为空，联系管理员
                    break
            else:
                self.signal_server_outline.emit()  # 服务器连接失败
                break

            if current_version is not None:
                if current_version in version_list:
                    if current_version != version_list[-1]:
                        index1 = version_list.index(current_version)
                        target_list = version_list[index1 + 1:]
                        self.signal_update_detected.emit(target_list)
                        break
                    else:
                        self.signal_already_uptodate.emit()  # 已为最新版本
                        break
                else:
                    target_list = version_list
                    self.signal_update_detected.emit(target_list)  # 检测到更新
                    break
            else:
                target_list = version_list
                self.signal_update_detected.emit(target_list)  # 检测到更新
                break


class Setup(QThread):
    signal_server_outline = pyqtSignal()
    signal_uptodate = pyqtSignal()
    signal_down_fail = pyqtSignal(str)
    signal_copy_file = pyqtSignal(str)
    signal_finish_pack = pyqtSignal(str)

    def __init__(self, project_name, project_path, target_list):  # 项目名/项目路径/更新列表
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path
        self.target_list = target_list

    def __del__(self):
        self.wait()

    def run(self):
        version_file = os.path.join(self.project_path, 'version.json')
        version_file = os.path.abspath(version_file)  # 版本信息文件

        update_pack_path = os.path.join(self.project_path, 'update')
        update_pack_path = os.path.abspath(update_pack_path)  # 更新包文件夹
        if not os.path.exists(update_pack_path):
            os.mkdir(update_pack_path)

        temp_path = os.path.join(self.project_path, 'temp')
        temp_path = os.path.abspath(temp_path)  # 临时解压地址
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        my_ftp = FTPHelper.MyFtp('172.16.1.156', 21, 'Administrator', '123456')
        while True:
            if my_ftp.ftp_login() == 1000:
                if len(self.target_list) == 0 or self.target_list is None:
                    self.signal_uptodate.emit()  # 已更新至最新版本
                    break
                else:
                    update_pack = self.target_list.pop(0)
                    if my_ftp.download_file(update_pack, os.path.join(update_pack_path, update_pack)) == 1000:
                        shutil.rmtree(temp_path)
                        os.mkdir(temp_path)
                        pack_zip = os.path.join(update_pack_path, update_pack)
                        zp = zipfile.ZipFile(pack_zip, 'r')
                        zp.extractall(temp_path)
                        zp.close()
                        with open(os.path.join(temp_path, (self.project_name + '_update.json')), 'r') as uf:
                            update_json = uf.read()
                            update_dic = json.loads(update_json)
                        for update_file in update_dic:
                            source_file = os.path.join(temp_path, update_file)
                            destination_file = os.path.join(self.project_path, update_file)
                            if not os.path.exists(os.path.dirname(destination_file)):
                                os.mkdir(os.path.dirname(destination_file))
                            shutil.copyfile(source_file, destination_file)
                            self.signal_copy_file.emit(os.path.basename(destination_file))  # 复制文件
                        version_dic = {'current_version': update_pack}
                        version_json = json.dumps(version_dic)
                        with open(os.path.join(self.project_path, 'version.json'), 'w') as vf:
                            vf.write(version_json)
                        self.signal_finish_pack.emit(update_pack)
                    else:
                        self.signal_down_fail.emit(update_pack)
                        break
            else:
                self.signal_server_outline.emit()
                break
