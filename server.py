from CONSTANTS import *
from server_sockets import *
import socket
import threading
import real.meeting as meeting
import real.videoServer
import time
meeting_id=0
audio_port=9808
vedio_port=9999
meeting_list=[]
def control(control_socket,control_address):
    global meeting_id
    global audio_port
    global meeting_list
    global vedio_port
    while True:
        control_recive=control_socket.recv(1024)
        if control_recive==b'creat_meetingdmx':
            new_meeting= meeting.meet(meeting_id,audio_port,vedio_port)
            meeting_list.append(new_meeting)
            audio_port+=1
            meeting_id+=1
            str_id=str(meeting_id)
            print('abc')
            control_socket.send(b'success_creatdmx')
            control_socket.send(str_id.encode())
            print('创建会议')
        elif control_recive==b'join_meetingdmx':
            receive_id=control_socket.recv(1024).decode()
            name = control_socket.recv(1024).decode()
            if int(receive_id)>len(meeting_list):
                control_socket.send(b'fail_joindmx')
                continue
            re_meeting=meeting_list[int(receive_id)-1]
            re_meeting.instruction_connection.append(control_socket)
            re_meeting.people.append(name)
            control_socket.send(b'success_joindmx')
            # control_socket.send(meeting_list[int(receive_id)-1])
            meet_audio_port=meeting_list[int(receive_id)-1].audio_port
            meet_audio_port=str(meet_audio_port)
            time.sleep(1)
            control_socket.send(meet_audio_port.encode())
        elif control_recive==b'leave_meetingdmx':
            now_meeting_id=control_socket.recv(1024).decode()
            now_meeting_id=int(now_meeting_id)
            now_meeting=meeting_list[now_meeting_id-1]
            now_name=control_socket.recv(1024).decode()
            # for i in range(0,len(now_meeting.people)):
            #     if now_meeting.people[i]==now_name:
            #         now_meeting.people.remove(now_name)
                    # now_meeting.instruction_connection.remove
            control_socket.send(b'su_leave_medmx')
def socket_listen(port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('127.0.0.1',port))
    while True:
        sock.listen(2)
        conn,address = sock.accept()
        print(address,'连接成功')
        threading.Thread(target=control, args=(conn,address)).start()

if __name__ == "__main__":
    ports = 11262
    threading.Thread(target=socket_listen, args=(11262,)).start()