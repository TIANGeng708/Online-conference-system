import time
from socket import *
import threading

class Video_Server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = ('192.168.137.38', port)


        self.controlCons = []
        self.connections = []

        self.sock = socket(AF_INET, SOCK_STREAM)

        self.notifyAll = {}
        self.hasCtrlCons = {}

        self.length = 0

    def __del__(self):
        self.sock.close()
        # try:
        #     cv2.destroyAllWindows()
        # except:
        #     pass

    def runs(self):
        print("VIDEO server starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(5)
        while True:
            time.sleep(1)
            # for ip in self.hasCtrlCons.keys():
            #     print(self.hasCtrlCons[ip])
            #     if getattr(self.hasCtrlCons[ip], '_closed'):
            #         print("Delete socket %s" % (self.hasCtrlCons[ip]))
            #         self.controlCons.remove(self.hasCtrlCons[ip])
            #         del self.hasCtrlCons[ip]

            conn, addr = self.sock.accept()
            # print(conn)
            # print(addr)
            conn.settimeout(5)

            print("remote VIDEO client success connected... Addr is%s" % str(conn.getpeername()))

            ip = conn.getpeername()[0]
            port = conn.getpeername()[1]
            if ip in self.hasCtrlCons:

                contrlSocket = self.hasCtrlCons[ip]
                if not self.testControl(contrlSocket) :
                    self.controlClose(contrlSocket)
                    print("The old control socket is valid")
                    print("This is a control connect")

                    # add a new control socket
                    self.hasCtrlCons[ip] = conn
                    self.controlCons.append(conn)

                    continue
                # except:
                #     print("The old control socket is valid")
                #     print("This is a control connect")
                #     if self.hasCtrlCons[ipTarget] in self.controlCons:
                #         self.controlCons.remove(self.hasCtrlCons[ipTarget])
                #     self.hasCtrlCons[ipTarget] = conn
                #     self.controlCons.append(conn)
                #     continue
                if self.length != 0:
                    conn.close()
                    continue

                self.length = self.length + 1
                self.connections.append(conn)
                threading.Thread(target=self.handle_client, args=(conn, addr,)).start()
                print("This is a video connect.")
            else:
                self.hasCtrlCons[ip] = conn
                self.controlCons.append(conn)
                print("This is a control connect")

            # for client in self.connections:
            #     print(client)
            #     print(getattr(client, '_closed'))


    def controlClose(self, controlSocket : socket):
        if controlSocket not in self.controlCons:
            return
        #print(self.controlCons)
        print("Delete controlSocket %s\n" %str(controlSocket), end="")
        print("The number of controlSocket before delete: %s\n" %(str(len(self.controlCons))), end="")
        #print(self.controlCons)
        print("The number of videoSocket before delete: %s\n" %(str(len(self.connections))), end="")
        #print(self.connections)
        self.controlCons.remove(controlSocket) # 从 control list 里 remove 这个socket
        ip = controlSocket.getpeername()[0]
        del self.hasCtrlCons[ip] # 把 ip 对应的这个 cotrol socket 删除 从此就没有从这个ip地址来的 这个用户就断开了连接
        for videoSocket in self.connections[:]: # 把从这个controlSocket 对应IP 的 视频socket 给关了并且删了
            if videoSocket.getpeername()[0] == ip:
                self.videoClose(videoSocket)
                videoSocket.close()
        self.videoCloseSpecificShareSocket(controlSocket.getpeername()[0])
        print("The number of controlSocket after delete: %s\n" %(str(len(self.controlCons))), end="")
        controlSocket.close()

    def testControl(self, contrlSocket : socket):
        try:
            if getattr(contrlSocket, '_closed'):
                raise error

            contrlSocket.send("Test".encode("utf8"))
            return True
        except:
            print(contrlSocket)
            return False

    # 完整的删除一个视频socket 以及它拥有的shareSocket
    def videoClose(self, videoSocket: socket):
        # 获得该视频流socket 对应的字典 里面的所有链接
        # notifyDic {(ip1, addr1) : socket1, (ip2, addr2) : socket2}
        if getattr(videoSocket, '_closed'):
            raise error

        print("Delete videoSocket %s\n" %str(videoSocket), end="")
        notifyDic = self.notifyAll[videoSocket]
        for ipAndAddr in notifyDic:
            shareConnection = notifyDic[ipAndAddr]
            shareConnection.close()
        if server in self.notifyAll:
            del self.notifyAll[server]
        self.connections.remove(videoSocket)
        print("The number of videoSocket after delete: %s\n" %(str(len(self.connections))), end="")
        self.length = self.length - 1
        return

    # 关闭所有 视频socket 的 share socket 中 对于某个 ip地址的链接
    def videoCloseSpecificShareSocket(self, ip):
        for videoSocket in self.connections:
            notifyDic = self.notifyAll[videoSocket]
            self.specificShareClose(ip, notifyDic)

    def specificShareClose(self, ip, notifyDic : dict):
        notifyDic[ip].close()
        del notifyDic[ip]

    def broadcast(self, sock, data):
        # server 是一个 视频socket
        server = sock

        # 如果某个视频流socket 被关了
        # 一个视频 socket 对应一个字典 里面存着需要分发的socket（ip，port）
        if getattr(server, '_closed'):
            print("One user close the video share")
            self.videoClose(server)

        # 如果这个视频流是第一次分发图片
        if server not in self.notifyAll:
            print("Add a new server into notifyDictionary.\n", end="")
            self.notifyAll[server] = {}

        notifyDic = self.notifyAll[server]

        # 对于每个连上服务器的用户 视频socket 都需要对其进行视频share, 分别建立socket链接 存进 self.notifyAll[server]
        for client in self.controlCons[:]:
            # 如果某个 用户的control连接已经失效 需要删去 所有与该用户有关的东西
            # 包括 control 连接下的视频连接 videoSocket 以及 videoSocket 下的  shareSocket
            # 同时删去 该用户在 当前server（videoSocket）下建立的 shareSocket
            # 删除 在任意 videoSocket 下被建立的 shareSocket链接
            ip = client.getpeername()[0]  # ('10.25.226.174', 7308) [0] = '10.25.226.174'
            port = client.getpeername()[1]
            if not self.testControl(client):
                self.controlClose(client)
                continue

            # if client == self.sock:
            #     print("continue")
            #     continue

            # 如果该用户第一次被当前videoSocket shareVideo 则新建一个 ShareSocket
            if ip not in notifyDic:
                print("Add a newSock into notifyDictionary.\n", end="")
                newShareSock = socket(AF_INET, SOCK_STREAM)
                try:
                    newShareSock.connect((ip, port)) # throw error cant find
                    notifyDic[ip] = newShareSock
                    self.sendData(server, newShareSock, data)
                except:
                    print("Can not find the client %s", ip)
                    pass
            else:
                # print("Read a oldSock from notifyDictionary.\n", end="")
                oldShareSock = notifyDic[ip]
                self.sendData(server, oldShareSock, data)

    def sendData(self, server, shareSocket, data):
        # print("Send data!\n", end="")
        try:
            if getattr(shareSocket, '_closed'):
                raise error
            # print("target is %s\n" %(str(sock.getpeername())), end="")
            shareSocket.sendall(data) # throw error because some one exit when be shared video
        except:
            print("Error: Some shareSocket closed throw error")
            ip = shareSocket.getpeername()[0]
            if ip in self.hasCtrlCons:
                controlSocket = self.hasCtrlCons[ip]
                self.controlClose(controlSocket)


    def handle_client(self, videoSocket, addr):
        print("Starting threading %s\n" %str(threading.currentThread().ident), end="")
        while True:
            try:
                # print("try")
                if getattr(videoSocket, '_closed'):
                    raise error
                data = videoSocket.recv(1024)
                # print(len(data))
                # print(data)
                if len(data) == 0:
                    raise error
                self.broadcast(videoSocket, data)

            except:
                self.videoClose(videoSocket)

                print("One video sender leave.")
                print("The video connections is " + str(len(self.connections)) + "\n", end="")
                print("The users connections is " + str(len(self.controlCons)) + "\n", end="")
                break
        print("END the threading %s\n" %str(threading.currentThread().ident), end="")


server = Video_Server(10000)
server.runs()
