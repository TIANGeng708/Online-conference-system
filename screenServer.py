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
        self.controlCons.remove(controlSocket) # ??? control list ??? remove ??????socket
        ip = controlSocket.getpeername()[0]
        del self.hasCtrlCons[ip] # ??? ip ??????????????? cotrol socket ?????? ????????????????????????ip???????????? ??????????????????????????????
        for videoSocket in self.connections[:]: # ????????????controlSocket ??????IP ??? ??????socket ?????????????????????
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

    # ???????????????????????????socket ??????????????????shareSocket
    def videoClose(self, videoSocket: socket):
        # ??????????????????socket ??????????????? ?????????????????????
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

    # ???????????? ??????socket ??? share socket ??? ???????????? ip???????????????
    def videoCloseSpecificShareSocket(self, ip):
        for videoSocket in self.connections:
            notifyDic = self.notifyAll[videoSocket]
            self.specificShareClose(ip, notifyDic)

    def specificShareClose(self, ip, notifyDic : dict):
        notifyDic[ip].close()
        del notifyDic[ip]

    def broadcast(self, sock, data):
        # server ????????? ??????socket
        server = sock

        # ?????????????????????socket ?????????
        # ???????????? socket ?????????????????? ???????????????????????????socket???ip???port???
        if getattr(server, '_closed'):
            print("One user close the video share")
            self.videoClose(server)

        # ?????????????????????????????????????????????
        if server not in self.notifyAll:
            print("Add a new server into notifyDictionary.\n", end="")
            self.notifyAll[server] = {}

        notifyDic = self.notifyAll[server]

        # ???????????????????????????????????? ??????socket ???????????????????????????share, ????????????socket?????? ?????? self.notifyAll[server]
        for client in self.controlCons[:]:
            # ???????????? ?????????control?????????????????? ???????????? ?????????????????????????????????
            # ?????? control ???????????????????????? videoSocket ?????? videoSocket ??????  shareSocket
            # ???????????? ???????????? ??????server???videoSocket??????????????? shareSocket
            # ?????? ????????? videoSocket ??????????????? shareSocket??????
            ip = client.getpeername()[0]  # ('10.25.226.174', 7308) [0] = '10.25.226.174'
            port = client.getpeername()[1]
            if not self.testControl(client):
                self.controlClose(client)
                continue

            # if client == self.sock:
            #     print("continue")
            #     continue

            # ?????????????????????????????????videoSocket shareVideo ??????????????? ShareSocket
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
