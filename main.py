import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from tools import ftp_helper, Update_Helper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.my_ftp = ftp_helper.MyFtp()

        self.project_name = 'Qt_UI_25'
        self.project_path = 'C:/WX_Project'

        """功能函数"""
        self.check_update()

    def init_ui(self):
        icon = QIcon()
        icon.addPixmap(QPixmap("resources/00007BF3.png"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QRect(10, 50, 460, 100))
        font = QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setStyleSheet('QLabel{color:white}')
        self.label.setFont(font)
        self.label.setCursor(QCursor(Qt.IBeamCursor))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QRect(40, 220, 400, 35))
        self.progressBar.setFixedSize(400, 35)
        font = QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QRect(180, 360, 100, 40))
        self.pushButton.setFixedSize(100,40)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setEnabled(False)
        self.pushButton.setVisible(True)

        self.update_button = QPushButton(self.centralwidget)
        self.update_button.setGeometry(QRect(180, 360, 100, 40))
        self.update_button.setFixedSize(100,40)
        self.update_button.setFont(font)
        self.update_button.setObjectName("update_Button")
        self.update_button.setEnabled(False)
        self.update_button.setVisible(True)

        self.progressBar.raise_()
        self.label.raise_()
        self.pushButton.raise_()

        _translate = QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "客户端应用更新"))
        self.pushButton.setText(_translate("MainWindow", "更新"))

        vertex_layout = QVBoxLayout(self.centralwidget)
        vertex_layout.addWidget(self.label, 0, Qt.AlignCenter)
        vertex_layout.addWidget(self.progressBar, 0, Qt.AlignCenter)
        vertex_layout.addWidget(self.pushButton, 0, Qt.AlignCenter)
        vertex_layout.addWidget(self.update_button, 0, Qt.AlignCenter)

        self.centralwidget.setLayout(vertex_layout)
        self.setCentralWidget(self.centralwidget)

        self.setWindowOpacity(0.8)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(0, 0, 1280, 720, QPixmap("resources\世界地图.jpg"))
        painter.end()

    def check_update(self):
        update_pack_path = os.path.join(project_path, 'update')
        update_pack_path = os.path.abspath(update_pack_path)

        if self.my_ftp.ftp_login() == 1000:
            self.findChild(QLabel, 'label').setText('已连接服务器，正在查询更新信息')
            file_list = self.my_ftp.ftp_getfiles()
            for i in file_list:
                if self.project_name not in i:
                    file_list.remove(i)
            file_list.sort()
            file_list.append('Qt_UI_25_1542159836.3973486.zip')
            file_list.sort()
            print(file_list.index('Qt_UI_25_1542159836.3973486.zip'))
            print('list:', file_list)
        else:
            self.findChild(QLabel, 'label').setText('无法连接服务器，请连续管理员')


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    #
    # main_window = MainWindow()
    # main_window.setWindowTitle('客户端启动器')
    # main_window.setFixedSize(480, 465)
    # main_window.show()
    #
    # sys.exit(app.exec_())

    project_name = 'Qt_UI_25'
    project_path = 'C:/WX_Project'
    temp_path = os.path.join(project_path, 'temp')
    update_pack_path = os.path.join(project_path, 'update')
    update_pack_path = os.path.abspath(update_pack_path)
    if not os.listdir(update_pack_path):
        print('empty')
        my_ftp = ftp_helper.MyFtp()
        if my_ftp.ftp_login() == 1000:
            file_list = my_ftp.ftp_getfiles()
            for i in file_list:
                if project_name not in i:
                    file_list.remove(i)
            file_list.sort()
            update_pack = file_list[0]
            my_ftp.download_file(update_pack, (os.path.join(update_pack_path, update_pack)))
    else:
        print('not empty')
        version_list = []
        for i in os.listdir(update_pack_path):
            version_list.append(i)

        version = version_list[-1]

        my_ftp = ftp_helper.MyFtp()
        if my_ftp.ftp_login() == 1000:
            file_list = my_ftp.ftp_getfiles()
            for i in file_list:
                if project_name not in i:
                    file_list.remove(i)
            file_list.sort()
            temp = file_list.index(version)
            if file_list[temp] == file_list[-1]:
                print('没有新的更新包')
            else:
                update_pack = file_list[temp + 1]
                if my_ftp.download_file(update_pack, (os.path.join(update_pack_path, update_pack))) == 1000:
                    print('更新包已下载')