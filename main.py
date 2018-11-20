import sys

from PyQt5.QtWidgets import *

from ui import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow.MainWindow()
    main_window.setWindowTitle('客户端启动器')
    main_window.setFixedSize(1280, 720)
    main_window.show()

    sys.exit(app.exec_())