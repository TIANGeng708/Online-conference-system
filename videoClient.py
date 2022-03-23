import pickle
import socket
import struct
import zlib
from socket import *
import threading
import cv2
import time
import canshu


class Video_Client(threading.Thread):
    def __init__(self, ip, port, level, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.listener = socket(AF_INET, SOCK_STREAM)#开启监听的socket
        self.ADDR = (ip, port)
        if level <= 3:
            self.interval = level
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:  # 限制最大帧间隔为3帧
            self.fx = 0.3
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)##使用网络协议
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)

        self.videoSock = None#建立视频链接变量

        self.windowNames = []#存放所有窗口信息的列表

        self.connections = []#存放所有连接的列表

        self.cap = None#建立摄像头变量
    def __del__(self):
        self.sock.close()#关闭连接
        if self.videoSock != None:
            self.videoSock.close()

        if self.cap != None:
            self.cap.release()#释放摄像头

        try:
            cv2.destroyAllWindows()#关闭窗口
        except:
            pass#异常捕获

    def run(self):
        print("VIDEO client starts...\n", end="")
        while True:
            try:####异常捕获
                self.sock.connect(self.ADDR)#建立连接
                print(self.sock.getsockname())
                threading.Thread(target=self.accept_connections, args=(),name='7777').start()
                print("VIDEO client connected...", end="\n")##打印连接信息
                break
            except:
                time.sleep(3)
                continue
        while True:
            try:
                self.sock.recv(1024)
            except:
                pass



    def video_stop(self):
        if self.videoSock == None:
            return
        else:
            self.videoSock.close()
            self.videoSock = None

    def video_start(self):
        if self.videoSock != None:
            return
        while True:
            try:
                self.videoSock = socket(AF_INET, SOCK_STREAM)
                self.videoSock.connect(self.ADDR)
                # print(self.videoSock.getsockname())
                threading.Thread(target=self.video_post, args=(self.videoSock,),name='6666').start()
                print("Post video to other users.By %s" %(str(self.videoSock.getsockname())))
                break
            except:
                time.sleep(3)
                continue


    def video_post(self, videoSock : socket):
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            sframe = cv2.resize(frame, (0, 0), fx=self.fx, fy=self.fx)
            data = pickle.dumps(sframe)
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                videoSock.sendall(struct.pack("L", len(zdata)) + zdata)
            except:
                self.cap.release()
                videoSock.close()
                break
            for i in range(self.interval):
                self.cap.read()

    def accept_connections(self):
        print("Begin listening!\n", end="")
        self.listener.bind(self.sock.getsockname())
        self.listener.listen(5)

        while True:
            conn, addr = self.listener.accept()
            conn.settimeout(1)
            self.connections.append(conn)

            threading.Thread(target=self.receive_server_data, args=(conn,),name='5555').start()
            print("New a video~!")

    def receive_server_data(self, conn):
        data = "".encode("utf-8")
        payload_size = struct.calcsize("L")  # 结果为4
        windowName = 'Remote'+str(conn)
        self.windowNames.append(windowName)
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        while True:
            try:
                while len(data) < payload_size:
                    if getattr(conn, '_closed'):
                        conn.close()
                        cv2.destroyWindow(windowName)
                        return

                    data += conn.recv(81920)
                packed_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L", packed_size)[0]
                while len(data) < msg_size:
                    # see the picture whether valid
                    # print(len(data), msg_size)
                    if getattr(conn, '_closed'):
                        conn.close()
                        cv2.destroyWindow(windowName)
                        return
                    data += conn.recv(81920)
                zframe_data = data[:msg_size]
                data = data[msg_size:]
                frame_data = zlib.decompress(zframe_data)
                frame = pickle.loads(frame_data)
                cv2.imshow(windowName, frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            except:
                conn.close()
                print("Connection time limits")
                cv2.destroyWindow(windowName)
                return

if __name__ == '__main__':
    pass
    # client = Video_Client("127.0.0.1", 9999, 3, 4)
    # client.start()

    while True:
        pass
        # ins = input("1 to share video, 0 to stop video!")
        # if ins == "1":
        #     client.video_start()
        # if ins == "0":
        #     client.video_stop()

