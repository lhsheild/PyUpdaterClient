from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)

        self.setWindowIcon(QIcon(r'E:\Projects\Python_Projects\PyUpdaterUpload\resource\小鸟妮妮.png'))
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
        self.center_widget.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(0, 0, 1280, 720, QPixmap(r"E:\Projects\Python_Projects\PyUpdaterClient\resource\世界地图.jpg"))
        painter.end()

    def update_button_init(self):
        update_button = QPushButton(self)
        update_icon = QIcon(r'E:\Projects\Python_Projects\PyUpdaterClient\resource\00007BF3.png')
        update_button.setIcon(update_icon)
        update_button.setIconSize(QSize(256, 256))
        update_button.setFixedSize(256, 256)
        update_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        update_button.setEnabled(True)
        update_button.clicked.connect(lambda: self.select_ckeck_folder())
        update_button.setObjectName('check_button')
        return update_button

    def lauch_button_init(self):
        lauch_button = QPushButton(self)
        lauch_icon = QIcon(r'E:\Projects\Python_Projects\PyUpdaterClient\resource\00007BF3.png')
        lauch_button.setIcon(lauch_icon)
        lauch_button.setIconSize(QSize(256, 256))
        lauch_button.setFixedSize(256, 256)
        lauch_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        lauch_button.setEnabled(True)
        lauch_button.clicked.connect(lambda: self.select_ckeck_folder())
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
        tips_label.setText('三维平台已为最新版本')
        tips_label.setFixedSize(1000, 30)
        tips_label.setObjectName('tips_label')
        return tips_label

    '''检查服务器是否有新的更新包'''
    def check_update(self):
