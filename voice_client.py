import socket
import threading
import pyaudio
import canshu


class Client:
    def __init__(self,port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('开始连接')
        while 1:
            try:
                self.target_port = port
                self.s.connect(('192.168.137.1', self.target_port))
                break
            except:
                pass

        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        print('size:1024')
        channels = 1
        rate = 20000
        self.single_switch=1
        self.p = pyaudio.PyAudio()
        print(1192)
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        print('创建成功')
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

        # print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data,name='3333').start()
        threading.Thread(target=self.send_data_to_server,name='4444').start()


    def receive_server_data(self):
        a = 0
        while True:
            # print(123123123123)

            # a = a + 1
            # if a % 50000 == 0:
            #     print('a')



            if self.single_switch==0:
                print('断开接收')
                break
            try:
                data = self.s.recv(1024)
                self.playing_stream.write(data)
            except:
                pass

    def send_data_to_server(self):
        a = 0
        while True:



            # a=a+1
            # if a%5000000==0:
            #     print(canshu.in_meeting)




            if canshu.in_meeting==0:
                print('断开发送')
                self.single_switch=0
                break
            if canshu.am==0:
                continue
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except:
                pass


# client = Client()