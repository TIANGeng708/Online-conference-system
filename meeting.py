import real.voiceServer as AS
import threading
import real.videoServer
class meet():
    def __init__(self,id,audio_port,video_port):
        self.id=id
        self.people=[]
        self.instruction_connection=[]
        self.state=0
        self.audio_server=None
        self.audio_port=audio_port
        self.video_port=video_port
        self.video_server=None
        threading.Thread(target=self.new_audio,args=(audio_port,)).start()
        threading.Thread(target=self.new_video).start()
        '''
        0: nothing
        1: video
        2: audio
        3: audio and video
        '''
    def new_audio(self,audio_port):
        self.audio_server=AS.Server(audio_port)

    def new_video(self):
        real.videoServer.new_server(9999)
        self.video_port=self.video_port+1
        # self.video_server=real.videoServer.Video_Server(9999)
        # self.video_server.runs()
