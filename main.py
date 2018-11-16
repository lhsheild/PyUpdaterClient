import os
import sys
import json
import zipfile

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from tools import ftp_helper, Update_Helper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

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
        self.pushButton.clicked.connect(lambda: self.setup_update())
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

    """检查更新服务器"""
    def check_update(self):
        self.my_check_update = Update_Helper.CheckUpdate(self.project_name, self.project_path)
        self.my_check_update.signal_server_empty.connect(self.check_update_empty)
        self.my_check_update.signal_already_down.connect(self.check_update_already)
        self.my_check_update.signal_server_out.connect(self.check_update_fail)
        self.my_check_update.signal_downpack.connect(self.check_update_down)
        self.my_check_update.start()

    @pyqtSlot()
    def check_update_empty(self):
        self.findChild(QLabel, 'label').setText('服务器没有对应更新包')

    @pyqtSlot()
    def check_update_already(self):
        self.findChild(QLabel, 'label').setText('本地更新包已为最新版本')
        self.findChild(QPushButton, 'pushButton').setEnabled(True)

    @pyqtSlot()
    def check_update_fail(self):
        self.findChild(QLabel, 'label').setText('服务器连接失败')

    @pyqtSlot(str)
    def check_update_down(self, pack):
        self.findChild(QLabel, 'label').setText('更新包：{} 下载完成'.format(pack))

    def setup_update(self):
        self.my_setup_update = Update_Helper.SetupUpdate(self.project_name, self.project_path)
        self.my_setup_update.signal_copyfile.connect(self.update_coping_file)
        self.my_setup_update.signal_uptodate.connect(self.update_finish_copy)
        self.my_setup_update.start()

    @pyqtSlot(str)
    def update_coping_file(self, coping_file):
        self.findChild(QLabel, 'label').setText('正在更新文件：{}'.format(coping_file))

    @pyqtSlot()
    def update_finish_copy(self):
        self.findChild(QLabel, 'label').setText('已为最新版本，可以打开三维平台')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.setWindowTitle('客户端启动器')
    main_window.setFixedSize(480, 465)
    main_window.show()

    sys.exit(app.exec_())

    # update_pack_path = r'C:\WX_Project\update'
    # temp_path = r'C:\WX_Project\temp'
    # project = 'Qt_UI_25'
    # project_path = r'C:\WX_Project'
    # zf = zipfile.ZipFile(r'C:\WX_Project\update\Qt_UI_25_1542159836.3973486.zip', 'r')
    # zf.extractall(r'C:\WX_Project\temp')

    # file = r'C:\WX_Project\temp\Qt_UI_25_update.json'
    # with open(file, 'r') as f:
    #     j = f.read()
    #     d = json.loads(j)
    #
    # for i in d:
    #     index1 = i.find(project)
    #     print(i)
    #     origin = i[index1:]
    #     print(os.path.join(temp_path, origin))
    #     index2 = i.find(project)
    #     destination = i[index2:]
    #     print(os.path.join(project_path, destination))

    # test = 'Qt_UI_25_1542159836.3973486.zip'
    # print(test.split('Qt_UI_25_')[-1])