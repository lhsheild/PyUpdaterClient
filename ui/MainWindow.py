from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from tool import UpdateHelper

import win32api
import sys
import os
import json

from image import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        '''临时变量'''
        self.target_list = None

        self.setting_dic = {}
        self.project_name = None
        self.project_path = None
        self.exe_path = None

        self.init_setting()

        # self.project_name = 'wxDEMO'
        # self.project_path = r'C:\WX_Project'
        # self.exe_path = r'C:\WX_Project\wxDEMO\launch_debug.bat'

        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)

        self.setWindowIcon(QIcon(':/resource/a.png'))
        self.setWindowTitle('三维平台启动器')

        self.update_button = self.update_button_init()
        self.lauch_button = self.lauch_button_init()
        self.tips_label = self.tips_label_init()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button, 0, Qt.AlignCenter)
        button_layout.addWidget(self.lauch_button, 0, Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tips_label, 1, Qt.AlignCenter)
        main_layout.addLayout(button_layout, 1)
        self.center_widget.setLayout(main_layout)
        self.check_update()

        self.center_widget.show()

    def init_setting(self):
        if os.path.exists('setting.json'):
            with open('setting.json', 'r') as sf:
                setting_json = sf.read()
            self.setting_dic = json.loads(setting_json)
            self.project_name = self.setting_dic['project_name']
            self.project_path = self.setting_dic['project_path']
            self.exe_path = self.setting_dic['exe_path']
        else:
            project_folder = QFileDialog.getExistingDirectory(self, '选择项目所在路径')
            if os.path.exists(project_folder):
                self.setting_dic['project_name'] = os.path.basename(project_folder)
                self.setting_dic['project_path'] = os.path.abspath(os.path.dirname(project_folder))
                self.setting_dic['exe_path'] = os.path.abspath(os.path.join(project_folder, r'EXE\unigineQBased_x64.exe'))
                self.project_name = self.setting_dic['project_name']
                self.project_path = self.setting_dic['project_path']
                self.exe_path = self.setting_dic['exe_path']
            else:
                sys.exit(1)
            if len(self.setting_dic) > 0:
                setting_json = json.dumps(self.setting_dic)
                with open('setting.json', 'w') as sf:
                    sf.write(setting_json)
            else:
                sys.exit(1)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(0, 0, 1280, 720, QPixmap(':/resource/c.jpg'))
        painter.end()

    def update_button_init(self):
        update_button = QPushButton(self)
        update_icon = QIcon(':/resource/b.png')
        update_button.setIcon(update_icon)
        update_button.setIconSize(QSize(256, 256))
        update_button.setFixedSize(256, 256)
        update_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        update_button.setEnabled(False)
        update_button.clicked.connect(lambda: self.setup_update())
        update_button.setObjectName('check_button')
        return update_button

    def lauch_button_init(self):
        lauch_button = QPushButton(self)
        lauch_icon = QIcon(':/resource/a.png')
        lauch_button.setIcon(lauch_icon)
        lauch_button.setIconSize(QSize(256, 256))
        lauch_button.setFixedSize(256, 256)
        lauch_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        lauch_button.setEnabled(False)
        lauch_button.clicked.connect(lambda: self.lauch_app())
        lauch_button.setObjectName('check_button')
        return lauch_button

    def tips_label_init(self):
        tips_label = QLabel(self)
        tips_label.setAlignment(Qt.AlignCenter)
        tips_label.setStyleSheet('QLabel{color:white}')
        tips_font = QFont()
        tips_font.setFamily("微软雅黑")
        tips_font.setPointSize(18)
        tips_font.setBold(False)
        tips_font.setItalic(False)
        tips_font.setWeight(50)
        tips_label.setFont(tips_font)
        tips_label.setStyleSheet('QLabel{color:white}')
        tips_label.setText('正在检测更新信息...')
        tips_label.setFixedSize(1000, 30)
        tips_label.setObjectName('tips_label')
        return tips_label

    '''检查服务器是否有新的更新包'''
    def check_update(self):
        self.my_check_update_helper = UpdateHelper.Update(self.project_name, self.project_path)
        self.my_check_update_helper.signal_server_outline.connect(self.check_server_outline)
        self.my_check_update_helper.signal_server_empty.connect(self.check_server_empty)
        self.my_check_update_helper.signal_already_uptodate.connect(self.check_server_no_latest)
        self.my_check_update_helper.signal_update_detected.connect(self.check_server_detected)
        self.my_check_update_helper.start()

    @pyqtSlot()
    def check_server_empty(self):
        self.tips_label.setText('服务器没有任何更新文件')
        self.update_button.setEnabled(False)
        self.lauch_button.setEnabled(True)
        self.target_list = None

    @pyqtSlot()
    def check_server_no_latest(self):
        self.tips_label.setText('服务器没有最新更新')
        self.update_button.setEnabled(False)
        self.lauch_button.setEnabled(True)
        self.target_list = None

    @pyqtSlot()
    def check_server_outline(self):
        self.tips_label.setText('服务器连接失败，请连续管理员')
        self.update_button.setEnabled(False)
        self.lauch_button.setEnabled(True)
        self.target_list = None

    @pyqtSlot(list)
    def check_server_detected(self, target_list):
        self.tips_label.setText('检测到更新文件')
        self.target_list = target_list
        button = QMessageBox.question(self, "Question",
                                      self.tr("查询到更新版本，是否更新?"),
                                      QMessageBox.Ok | QMessageBox.Cancel,
                                      QMessageBox.Ok)
        if button == QMessageBox.Ok:
            self.update_button.setEnabled(True)
            self.lauch_button.setEnabled(False)
        else:
            self.lauch_button.setEnabled(True)
            self.update_button.setEnabled(False)

    '''选择是否安装更新包'''
    def setup_update(self):
        self.my_setup_update_helper = UpdateHelper.Setup(self.project_name, self.project_path, self.target_list)
        self.update_button.setEnabled(False)
        self.tips_label.setText('开始更新...')
        self.my_setup_update_helper.signal_server_outline.connect(self.setup_server_outline)
        self.my_setup_update_helper.signal_uptodate.connect(self.setup_uptodate)
        self.my_setup_update_helper.signal_down_fail.connect(self.setup_down_fail)
        self.my_setup_update_helper.signal_copy_file.connect(self.setup_copy_file)
        self.my_setup_update_helper.signal_finish_pack.connect(self.setup_finish_pack)
        self.my_setup_update_helper.start()

    @pyqtSlot()
    def setup_server_outline(self):
        self.tips_label.setText('服务器连接失败，请连续管理员')
        self.lauch_button.setEnabled(True)
        self.update_button.setEnabled(False)

    @pyqtSlot()
    def setup_uptodate(self):
        self.tips_label.setText('已更新至最新版本，请运行三维平台')
        self.lauch_button.setEnabled(True)
        self.update_button.setEnabled(False)

    @pyqtSlot(str)
    def setup_down_fail(self, pack):
        self.tips_label.setText('下载更新包失败：{}，请联系管理员'.format(pack))
        self.lauch_button.setEnabled(True)
        self.update_button.setEnabled(False)

    @pyqtSlot(str)
    def setup_copy_file(self, file):
        self.tips_label.setText('更新文件：{}'.format(file))

    @pyqtSlot(str)
    def setup_finish_pack(self, pack):
        self.tips_label.setText('更新版本：{}'.format(pack))

    '''启动按钮'''
    def lauch_app(self):
        os.chdir(os.path.join(os.path.join(self.project_path, self.project_name), 'data'))
        # os.chdir(os.path.join(self.project_path, self.project_name))
        os.popen(self.exe_path)
        # subprocess.getstatusoutput(self.exe_path)
        # win32api.ShellExecute(0, 'open', self.exe_path, '', '', 1)
        # os.system(self.exe_path)
        # sys.exit(0)
