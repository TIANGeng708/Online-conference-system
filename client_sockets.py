import socket
import threading

'''
    We provide a base class here.
    You can create new sub classes based on it.
'''

class ClientSocket():
    '''
        The main process of the ClientSocket is:
        Receive: receive data -> analyze the data -> take actions (send data or others)
        Send: construct data -> send data -> (optional) wait for reply (i.e., receive data)  
    '''
    def __init__(self,addr,client,sport = None):
        '''
            @Parameters
                addr: server address
                client: the registed client
                sport: the binded port of this socket
        '''
        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = addr
        # You can bind the certain port with the client
        if sport is not None:
            self.sock.bind(('',sport))
        # The registered client
        self.client = client
        # Protocol related - Header
        # If they are with the same format, you can use
        # self.header_format = None
        # self.header_size = 0  
        # Instead
        self.rheader_format = None  # The receiving header format
        self.rheader_size = 0       # The size of the receiving header
        self.sheader_format = None  # The sending header format
        self.sheader_size = 0       # The size of the sending header

        # If you want to connect to the server right now
        while True:
            try:
                self.sock.connect(self.addr)
                print("Connected")
                break
            except:
                print("Could not connect to the server"+str(self.addr))
        # Create a receive_server_data threading
        self.receive_thread = threading.Thread(target=self.receive_server_data)
        # If you want to start to receive data right now
        self.receive_thread.start()

    def receive_server_data(self):
        '''
            Receive the data from the sever
            It should be a threading function
        '''
        pass

    def analyze_receive_data(self,header,data):
        '''
            Analyze the received data
            You can also combine this function within 
            the "receive_server_data", so you can ignore this function
        '''
        pass

    def send_data(self,header,data):
        '''
            This function is used to send data to the server
            It can be a threading or a normal function depent
            on different purpose
        '''
        pass

    def construct_sending_data(self,*args):
        '''
            Construct the sending data
            @Returns
                header: The header of the msg
                data: The data of the msg
        '''
        pass