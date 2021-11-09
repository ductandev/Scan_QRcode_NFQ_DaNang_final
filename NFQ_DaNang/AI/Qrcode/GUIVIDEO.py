from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
import os
class window1(QtWidgets.QMainWindow):
    def __init__(self):
        super(window1,self).__init__()
        self.centralwid=QtWidgets.QWidget(self)
        self.vlayout=QtWidgets.QVBoxLayout()
        self.webview=QtWebEngineWidgets.QWebEngineView()
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)

        self.webview.setUrl(QUrl("http://8ffe5f2c-4fa0-4209-8196-c6a33f6f9333.2splus.com"))
        # self.webview.setUrl(QUrl("https://qrcode.danang.gov.vn/kbyt/site/checkin.php"))
        self.vlayout.addWidget(self.webview)
        self.centralwid.setLayout(self.vlayout)
        self.setCentralWidget(self.centralwid)
        self.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex=window1()
    ex.resize(1080,960)
    sys.exit(app.exec_())
