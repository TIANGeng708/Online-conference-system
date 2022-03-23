import threading

from real.client_sockets import *
import real.voice_client
import canshu
import real.videoClient
import os
import time
import real.screenClient
import real.c2
import real.s2
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *##引入前端组件

vodio_port=0#其实是audio_port，写错了
video_port=0#视频连接端口
screen_port=0#共享屏幕连接端口
vodio_client=None#视频对象
voice_client=None#语音对象
screen_client=None#共享屏幕对象
receive_id=''#当前会议号

# def action(action,client):
#     global voice_client
#     global vodio_client#将变量全局化
#     global screen_client
#     if canshu.in_meeting == 0:
#         if action == '1':
#             client.create_meeting()
#         elif action == '2':
#             client.join_meeting(1)
#     elif canshu.in_meeting == 1:
#         if action == '1':
#             client.open_close_screen()
#         elif action == '2':
#             threading.Thread(target=real.s2.main)
#             # real.s2.main()
#             pass
#         elif action == '3':
#             threading.Thread(target=real.c2.main)
#             # real.c2.main()
#             pass
#
#         elif action == '4':
#             client.open_close_video()
#             pass
#         elif action == '5':
#             client.open_close_audio()
#             pass
#         elif action == '6':
#             client.leave_meeting()
#         elif action == '7':
#             pass
def yuyin(video_port):
    global voice_client#将变量全局化
    voice_client = real.voice_client.Client(video_port)#创建新的语音对象

def shipin(video_port):
    global vodio_client#将变量全局化
    vodio_client=real.videoClient.Video_Client("192.168.137.1", video_port, 3, 4)#创建新的视频对象
    vodio_client.start()
def pingmu(screen_port):
    global screen_client#将变量全局化
    screen_client=real.screenClient.Video_Client('192.168.137.1',screen_port,3,4)#创建新的屏幕共享对象
    screen_client.start()



class Client():

    def __init__(self, addr, sport=None):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#TCP
        self.s.connect(('192.168.137.1', 11262))#TCP建立连接
        self.state = 1#会议状态
        self.name = '田耕'#用户名称
        self.newa = None
        self.meetint_id_number=''#会议号

    # Here we define an action function to change the CIL menu
    # based on different actions


    # All the functions defined bellow are not a must
    # You can define whatever function as you like
    def open_close_screen(self):
        if canshu.screen_switch == 0:
            screen_client.video_start()#当屏幕共享关闭时，打开屏幕共享
            canshu.screen_switch = 1
        else:
            screen_client.video_stop()#当屏幕共享打开时，关闭屏幕共享
            canshu.screen_switch = 0
    def open_close_video(self):
        if canshu.video_swtich == 0:
            vodio_client.video_start()#当摄像头关闭时，打开摄像头
            canshu.video_swtich = 1
        else:
            canshu.video_swtich = 0
            vodio_client.video_stop()#当摄像头打开时，关闭摄像头
    def leave_meeting(self):
        self.s.send('leave_meetingdmx'.encode())
        time.sleep(0.5)
        self.s.send(self.meetint_id_number.encode())
        time.sleep(0.5)
        self.s.send(self.name.encode())
        time.sleep(0.5)#离开会议，防止TCP连接崩溃，每次发送和接收之间都要睡眠0.5s
        print('ddddd')#标识符打印
        okk=self.s.recv(1024).decode()#接收服务端的消息
        print('abcdfdsfdsdf')
        if okk=='su_leave_medmx':
            print('成功离开会议')#消息打印
            self.meetint_id_number=''#会议号归零
            canshu.in_meeting=0#会议状态归零##
        else:
            print('abcd')#离开会议失败
        pass
    def open_close_audio(self):
        if canshu.am==0:
            canshu.am = 1#当麦克风关闭时，打开麦克风
        else:
            canshu.am = 0#当麦克风打开时，关闭麦克风
    def create_meeting(self):
        global receive_id#变量全局化
        yuanwen='creat_meetingdmx'
        miwen=yuanwen[::-1]#消息加密

        self.s.send(miwen.encode())#消息编码
        receive_creat = self.s.recv(1024).decode()#接收服务端消息
        print(receive_creat)#打印消息
        if receive_creat == 'success_creatdmx':
            receive_id = self.s.recv(1024).decode()#接收服务端消息

            print('成功创建会议，会议id:', receive_id)#打印提示信息

    def join_meeting(self,meeting_id):
        global vodio_port
        global video_port
        global screen_port#全局化变量
        # meeting_id = input('请输入会议号')
        self.s.send(b'join_meetingdmx')
        time.sleep(0.5)
        self.s.send(meeting_id.encode())
        time.sleep(0.5)
        self.s.send(self.name.encode())
        time.sleep(0.5)
        join_rec = self.s.recv(1024)#加入会议，防止TCP连接崩溃，每次发送和接收之间都要睡眠0.5s
        if join_rec == b'success_joindmx':
            self.state = 2
            vodio_port = self.s.recv(1024).decode()#接收服务端消息
            video_port=self.s.recv(1024).decode()#接收服务端消息
            screen_port=self.s.recv(1024).decode()#接收服务端消息
            self.newa = threading.Thread(target=yuyin, args=(int(vodio_port),))#开启语音线程
            print('成功加入会议')
            threading.Thread(target=yuyin, args=(int(vodio_port),),name='1111').start()#开启语音线程
            self.meetint_id_number=meeting_id
            canshu.in_meeting = 1
            threading.Thread(target=shipin,args=(int(video_port),),name='2222').start()#开启视频线程
            threading.Thread(target=pingmu,args=(int(screen_port),)).start()#开启屏幕共享线程
        else:
            print('加入会议失败')

class logindialog(QDialog):#GUI生成
    def __init__(self, client,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('会议系统')#窗口名称设置
        self.resize(500, 500)#窗口大小设置
        self.setFixedSize(self.width(), self.height())#设置高度和宽度
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.client=client#标记client
        self.frame = QFrame(self)
        self.verticalLayout = QVBoxLayout(self.frame)#设置界面控件

        # self.lineEdit_account = QLineEdit()
        # self.lineEdit_account.setPlaceholderText("请输入账号")
        # self.verticalLayout.addWidget(self.lineEdit_account)
        #
        # self.lineEdit_password = QLineEdit()
        # self.lineEdit_password.setPlaceholderText("请输入密码")
        # self.verticalLayout.addWidget(self.lineEdit_password)

        self.button_create_meeting = QPushButton()#设置按钮
        self.button_create_meeting.setText("创建会议")#设置按钮文本
        self.verticalLayout.addWidget(self.button_create_meeting)#激活按钮

        self.label = QLabel(self)#设置标签
        # label.resize(200, 100)
        self.label.setGeometry(200, 150, 210, 160)#设置标签大小
        self.label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.label.setText("当前未加入会议")#设置标签文本
        # self.label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.label2 = QLabel(self)#设置标签
        self.label2.setGeometry(200, 50, 210, 60)#设置标签大小
        self.label2.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.label2.setText("操作提示框")#设置标签文本

        self.meeting_id = QLineEdit()#设置按钮
        self.meeting_id.setPlaceholderText("请输入会议号")#设置按钮文本
        self.verticalLayout.addWidget(self.meeting_id)#激活按钮

        self.button_join_meeting = QPushButton()#设置按钮
        self.button_join_meeting.setText("加入会议")#设置按钮文本
        self.verticalLayout.addWidget(self.button_join_meeting)#激活按钮

        self.button_screen_share = QPushButton()#设置按钮
        self.button_screen_share.setText("开启/关闭屏幕共享")#设置按钮文本
        self.verticalLayout.addWidget(self.button_screen_share)#激活按钮

        self.button_request_control_screen = QPushButton()#设置按钮
        self.button_request_control_screen.setText("请求控制屏幕")#设置按钮文本
        self.verticalLayout.addWidget(self.button_request_control_screen)#激活按钮

        self.button_reply_control_screen=QPushButton()#设置按钮
        self.button_reply_control_screen.setText("请求被控制屏幕")#设置按钮文本
        self.verticalLayout.addWidget(self.button_reply_control_screen)#激活按钮

        self.button_video = QPushButton()#设置按钮
        self.button_video.setText("开启/关闭摄像头")#设置按钮文本
        self.verticalLayout.addWidget(self.button_video)#激活按钮

        self.button_audio = QPushButton()#设置按钮
        self.button_audio.setText("开启/关闭麦克风")#设置按钮文本
        self.verticalLayout.addWidget(self.button_audio)#激活按钮

        self.button_leave_meeting=QPushButton()#设置按钮
        self.button_leave_meeting.setText("离开当前会议")#设置按钮文本
        self.verticalLayout.addWidget(self.button_leave_meeting)#激活按钮

        # self.pushButton_quit = QPushButton()
        # self.pushButton_quit.setText("取消")
        # self.verticalLayout.addWidget(self.pushButton_quit)

        ###### 绑定按钮事件
        self.button_create_meeting.clicked.connect(self.cr_meeting)#为按钮绑定函数
        self.button_join_meeting.clicked.connect(self.jo_meetig)#为按钮绑定函数
        self.button_screen_share.clicked.connect(self.switch_screen)#为按钮绑定函数
        self.button_request_control_screen.clicked.connect(self.request_control_screen)#为按钮绑定函数
        self.button_reply_control_screen.clicked.connect(self.reply_control_screen)#为按钮绑定函数
        self.button_video.clicked.connect(self.switch_video)#为按钮绑定函数
        self.button_audio.clicked.connect(self.switch_audio)#为按钮绑定函数
        self.button_leave_meeting.clicked.connect(self.leave_now_meeting)#为按钮绑定函数
        # self.pushButton_quit.clicked.connect(QCoreApplication.instance().quit)

    def cr_meeting(self):
        try:
            if canshu.in_meeting==0:
                self.client.create_meeting()#当不在会议中时，新建会议
                # action('1',self.client)
                print(123)
                self.label2.setText('成功创建会议，会议id:'+receive_id)
                self.label2.show()#刷新标签文本
                # self.update()
            else:
                print('haha')
        except:
            pass


    def jo_meetig(self):
        try:
            if canshu.in_meeting==0:

                a=self.meeting_id.text()#不在会议中时，加入会议
                self.client.join_meeting(str(a))
                print(canshu.in_meeting)
                self.label.setText("会议号:"+str(self.client.meetint_id_number))
                self.label.show()#刷新标签文本
                self.label2.setText('成功加入会议！！！！')
                self.label2.show()#刷新标签文本
            else:
                print('ahaha')
        except:
            pass
    def switch_screen(self):
        try:
            if canshu.in_meeting==1:#在会议中，则根据是否开启屏幕共享进行相应操作
                self.client.open_close_screen()
                if canshu.screen_switch==1:
                    self.label2.setText('开启屏幕共享')
                    self.label2.show()#刷新标签文本
                else:
                    self.label2.setText('关闭屏幕共享')
                    self.label2.show()#刷新标签文本
            else:
                print('switch_screen')
        except:
            pass
    def request_control_screen(self):
        try:
            if canshu.in_meeting==1:
                threading.Thread(target=real.s2.main).start()#开启多线程，远程控制别人
                self.label2.setText('远程操控其他电脑')
                self.label2.show()#刷新标签文本
            else:
                print('request_control')
        except:
            pass


    def reply_control_screen(self):
        try:
            if canshu.in_meeting==1:#在会议中，根据状态进行操作
                if real.c2.shuju==0:
                    real.c2.shuju = 1
                    threading.Thread(target=real.c2.main).start()#开启多线程，被远程控制

                    self.label2.setText('正在被远程操控')
                    self.label2.show()#刷新标签文本

                else:
                    real.c2.shuju=0
                    self.label2.setText('屏幕控制释放')
                    self.label2.show()#刷新标签文本
            else:
                print('reply_control')
        except:
            pass

    def switch_video(self):
        try:
            if canshu.in_meeting==1:#在会议中，根据状态进行操作
                self.client.open_close_video()#调用摄像头函数
                if canshu.video_swtich==1:
                    self.label2.setText('开启摄像头')
                    self.label2.show()#刷新标签文本
                else:
                    self.label2.setText('关闭摄像头')
                    self.label2.show()#刷新标签文本
            else:
                print('switch_video')
        except:
            pass

    def switch_audio(self):
        try:
            if canshu.in_meeting==1:#在会议中，根据状态进行操作
                self.client.open_close_audio()#开启麦克风
                if canshu.am==1:
                    self.label2.setText('开启麦克风')
                    self.label2.show()#刷新标签文本
                else:
                    self.label2.setText('关闭麦克风')
                    self.label2.show()#刷新标签文本
            else:
                print('switch_audio')
        except:
            pass

    def leave_now_meeting(self):
        try:
            if canshu.in_meeting==1:#在会议中，开启下列操作
                self.client.leave_meeting()
                self.label.setText("当前未加入会议")
                self.label.show()#刷新标签文本
                self.label2.setText('离开会议')
                self.label2.show()#刷新标签文本
            else:
                print('leave_now_meeting')
        except:
            pass



if __name__ == "__main__":
    # The ip address of the server
    ip = '192.168.137.1'#设置ip
    # The example ports of the server
    # You can use one or more than one sockets
    address = 11262#设置端口号
    client = Client(address)#设置用户对象
    # A CIL menu loop

    while True:
        print(canshu.in_meeting)#打印信息
        app = QApplication(sys.argv)
        dialog = logindialog(client)#初始化GUI
        dialog.show()#展示GUI
        dialog.update()#刷新GUI
        # continue
        sys.exit(app.exec_())#GUI关闭引擎
        # if canshu.in_meeting==0:
        #
        #     # Main menu
        #     print("1. Create a meeting")
        #     print("2. Join a meeting")
        #     action_canshu = input("Action:")
        #     action(action_canshu,client)
        # elif canshu.in_meeting==1:
        #     # print("You are in the meeting: %d" % client.sid)
        #     # meeting menu
        #     print("1. (Stop) Share screen")
        #     print("2. (Stop) Control other's screen")
        #     print("3. (Stop) Control my screen")
        #     print("4. (Stop) Share video")
        #     print("5. (Stop) Share audio")
        #     print("6. Leave a meeting")
        #     print("7. Show current meeting members")
        #     action_canshu = input("Action:")
        #     # if action=='8':
        #     #     exit(1)
        #     action(action_canshu,client)