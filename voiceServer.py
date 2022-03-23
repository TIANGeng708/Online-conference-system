# -*- coding: utf-8 -*-
# create time    : 2020-12-30 15:37
# author  : CY
# file    : voice_server.py
# modify time:
import socket
import threading


class Server:
    def __init__(self,port):
        self.ip = '127.0.0.1'
        while True:
            try:

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.port = port
                self.s.bind((self.ip, self.port))
                break
            except:
                pass
        print('初始化')
        self.connections = []
        self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)

        while True:
            c, addr = self.s.accept()
            print('go9')
            self.connections.append(c)
            threading.Thread(target=self.handle_client, args=(c, addr,)).start()
        print('出循环')
    def broadcast(self, sock, data):
        for client in self.connections:
            print('广播分发1')
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    print('捕获异常')
                    pass

    def handle_client(self, c, addr):
        while 1:
            if True:
                data = c.recv(1024)
                self.broadcast(c, data)


