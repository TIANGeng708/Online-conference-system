import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *




################################################
#######对话框
################################################
class logindialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('登录界面')
        self.resize(200, 200)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        ###### 设置界面控件
        self.frame = QFrame(self)
        self.verticalLayout = QVBoxLayout(self.frame)

        # self.lineEdit_account = QLineEdit()
        # self.lineEdit_account.setPlaceholderText("请输入账号")
        # self.verticalLayout.addWidget(self.lineEdit_account)
        #
        # self.lineEdit_password = QLineEdit()
        # self.lineEdit_password.setPlaceholderText("请输入密码")
        # self.verticalLayout.addWidget(self.lineEdit_password)

        self.pushButton_enter = QPushButton()
        self.pushButton_enter.setText("确定")
        self.verticalLayout.addWidget(self.pushButton_enter)

        # self.pushButton_quit = QPushButton()
        # self.pushButton_quit.setText("取消")
        # self.verticalLayout.addWidget(self.pushButton_quit)

        ###### 绑定按钮事件
        self.pushButton_enter.clicked.connect(self.on_pushButton_enter_clicked)
        # self.pushButton_quit.clicked.connect(QCoreApplication.instance().quit)

    def on_pushButton_enter_clicked(self):
        print(123)
        # 账号判断



if __name__ == "__main__":
    while True:
        app = QApplication(sys.argv)
        dialog = logindialog()
        dialog.show()
        sys.exit(app.exec_())