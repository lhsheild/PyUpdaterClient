import hashlib
import os
import os.path
import sys
from PyQt5.QtCore import *
import time
import json

folder_size_dic = {}
file_md5_dic = {}

"""装饰器"""


# 计算函数运行时间
def get_func_runtime(f):
    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %s' % (f.__name__, time.time() - s))
        return res

    return fi


class MyMD5(object):
    def __init__(self, dirpath='', filepath=''):
        super().__init__()
        self.dir_path = dirpath
        self.file_name = filepath

    def generate_md5_hash_for_dir(self, dir_path, block_size=2 ** 20, progress_blocks=128):
        """This function generates an md5 hash for a given floder."""

        file_md5_dic = {}
        for parent, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                file = os.path.join(parent, filename)  # 文件绝对路径
                file_relative_path = file.lstrip(os.path.join(dir_path, '\\')).rstrip(filename)  # 文件相对路径
                md5 = self.generate_md5_hash_for_file(file)  # 文件MD5
                file_md5_dic[filename] = [file_relative_path, md5]
        return file_md5_dic

    def generate_md5_hash_for_file(self, file_name, block_size=2 ** 20, progress_blocks=128):
        """This function generates an md5 hash for a given file."""

        md5 = hashlib.md5()
        global blocks, total_blocks
        blocks = 0
        total_blocks = 1 + (os.path.getsize(file_name) / block_size)
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(block_size)
                if not data:
                    break
                md5.update(data)
                # Display progress in the command line
                if (blocks % progress_blocks) == 0:
                    percentage_string = "{0}%".format(100 * blocks / total_blocks)
                    return str(100 * blocks / total_blocks)
                    sys.stdout.write("\r{1:<10}{0}".format(file_name, percentage_string))
                    sys.stdout.flush()
                blocks += 1
        return md5.hexdigest()


class Cal_Md5_QThread(QThread):
    signal = pyqtSignal()

    def __init__(self, filename):
        super().__init__()
        self.working = True
        self.file_name = filename

    def __del__(self):
        self.working = False

    def run(self):
        self.trigger.emit()


class Get_Folder_Size_Helper(object):
    def __init__(self):
        super().__init__()
        self.sizelist = []

    def get_size(self, path):
        filelist = os.listdir(path)
        for filename in filelist:
            temp_path = os.path.join(path, filename)
            if os.path.isdir(temp_path):
                self.get_size(temp_path)
            elif os.path.isfile(temp_path):
                filesize = os.path.getsize(temp_path)
                self.sizelist.append(filesize)
        return sum(self.sizelist)


"""测试"""


@get_func_runtime
def test_runtime():
    my_get_size = Get_Folder_Size_Helper()
    target_dir = r'D:\Project\UnigineProjects\wx_project'
    project_name = target_dir.split('\\')[-1]

    for root, dirs, files in os.walk(target_dir):
        #  初始记录所有文件夹大小
        for dir_name in dirs:
            folder = os.path.join(root, dir_name)
            folder = os.path.abspath(folder)
            folder_relative_path = folder.split(project_name)[-1]
            print(folder_relative_path)
            size = my_get_size.get_size(folder)
            folder_size_dic[folder_relative_path] = size
        #  初始记录所有文件MD5
        for file_name in files:
            file = os.path.join(root, file_name)
            file = os.path.abspath(file)
            file_relative_path = file.split(project_name)[-1]
            print(file_relative_path)
            md5 = hashlib.md5()
            block_size = 2 ** 20
            with open(file, 'rb') as f:
                while True:
                    data = f.read(block_size)
                    if not data:
                        break
                    md5.update(data)
            md5_value = md5.hexdigest()
            file_md5_dic[file_relative_path] = md5_value

    # for i in folder_size_dic:
    #     print(i,':',folder_size_dic[i])

    size_json = json.dumps(folder_size_dic)
    md5_json = json.dumps(file_md5_dic)
    with open('test_size.json', 'w') as size_file:
        size_file.write(size_json)
    with open('test_md5.json', 'w') as md5_file:
        md5_file.write(md5_json)


@get_func_runtime
def test_get_change_files():
    with open('test_size.json', 'r') as size_file:
        size_json = size_file.read()
    size_dic = json.loads(size_json)

    with open('test_md5.json', 'r') as md5_file:
        md5_json = md5_file.read()
    md5_dic = json.loads(md5_json)

    my_get_size = Get_Folder_Size_Helper()

    changed_folder_list = []

    update_info_dic = {}

    target_dir = r'D:\Project\UnigineProjects\wx_project - 副本'
    project_name = target_dir.split('\\')[-1]

    for root, dirs, files in os.walk(target_dir):
        for dir_name in dirs:
            folder = os.path.join(root, dir_name)
            folder = os.path.abspath(folder)
            folder_relative_path = folder.split(project_name)[-1]
            size = my_get_size.get_size(folder)
            if folder_relative_path not in size_dic.keys():
                changed_folder_list.append(folder_relative_path)
            elif size_dic[folder_relative_path] != size:
                changed_folder_list.append(folder)

    for i in changed_folder_list:
        file_list = os.listdir(i)
        for file in file_list:
            file = os.path.join(i, file)
            if os.path.isfile(file):
                file = os.path.abspath(file)
                file_relative_path = file.split(project_name)[-1]
                md5 = hashlib.md5()
                block_size = 2 ** 20
                with open(file, 'rb') as f:
                    while True:
                        data = f.read(block_size)
                        if not data:
                            break
                        md5.update(data)
                md5_value = md5.hexdigest()
                if file_relative_path not in md5_dic.keys():
                    update_info_dic[file_relative_path] = md5_value
                elif md5_dic[file_relative_path] != md5_value:
                    update_info_dic[file_relative_path] = md5_value
    update_info_json = json.dumps(update_info_dic)
    with open('update.json', 'w') as update_file:
        update_file.write(update_info_json)


if __name__ == '__main__':
    # test_runtime()
    test_get_change_files()