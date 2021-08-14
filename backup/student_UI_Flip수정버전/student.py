# -*- coding: utf-8 -*-
import sys, cv2, numpy, time
import face_auth as auth
import threading 
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import socket
from mss import mss, tools
from sys import platform
import os,signal
import keyboard
#from tkinter import messagebox
from PIL import Image
import requests
from datetime import datetime
import io
import face_recog as fr
import base64

server='10.27.0.13:5000'

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("ui/MainWindow.ui",self)
        #응시하기 버튼 누르면 화면 전환
        self.enterButton.clicked.connect(self.checkAccount)
        self.loginSuccess=False
        #self.title.setFont(QFont('NanumSquare_0',16))

    def checkAccount(self):
        sn=self.lineEdit_sn.text()
        en=self.lineEdit_en.text()
        
        #------------------DB-----------------------#
        #로그인 성공 여부,이미지, 시험 시작시간, 종료시간, 감시 프로그램 리스트

        res=requests.post("http://"+server+"/test_room/student_login/" + en + "/" +sn)
        print('1')
        global student_image
        global start_date
        global end_date
        global block_list
        global title

        student_image=res.json()["student_image"]
        start_date=res.json()["start_date"]
        end_date=res.json()["end_date"]
        block_list=res.json()["block_list"]
        title=res.json()["title"]
        
        print(block_list)

        print('start:',start_date,'end:',end_date)
        
        if res.json()["test_room"]=='yes' and res.json()["student"]=='yes':
            print("Sucessfully logged in with ",sn,"(test : ",en,")")
            self.statusBar().showMessage('Success')
            #knowns 폴더에 저장
            #  decode
            
            imgbyte = base64.b64decode(student_image)
            img=Image.open(io.BytesIO(imgbyte))
            save_path=os.path.abspath(os.getcwd())
            save_path+='/knowns/'+sn+'.jpg'
            #os.path.join(save_path,'/knowns/'+sn+'.jpg')
            print(save_path)
            img.save(save_path,'JPEG')
            print('2')

            camerawindow=CameraWindow(sn,en)
            widget.addWidget(camerawindow)
            widget.setCurrentIndex(widget.currentIndex()+1)
        else:
            self.statusBar().showMessage(' Failed. Try Again.',2000)
            self.lineEdit_sn.clear()
            self.lineEdit_en.clear()
            

class CameraWindow(QMainWindow):
    get_sn=0
    get_en=0

    def __init__(self,sn,en):
        super(CameraWindow,self).__init__()
        loadUi("ui/CameraWindow.ui",self)
        self.startButton.hide()
        self.warning_msg.hide()
        self.match_true.hide()
        self.match_false.hide()
        self.startButton.clicked.connect(self.gotoStartExam)
        CameraWindow.get_sn=sn
        CameraWindow.get_en=en

        self.face_auth = auth.FaceRecog()

        #카메라 뿌리기
        self.fps=24
        self.img_frame.setScaledContents(True)
        self.start()


    def start(self) :
        self.timer=QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(int(1000./self.fps))

    def nextFrameSlot(self):
        #_,cam=self.cpt.read()
        frame = self.face_auth.get_frame()
        cam=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        #cam=cv2.flip(cam,1)
        set_img=QImage(cam,cam.shape[1],cam.shape[0],QImage.Format_RGB888)
        pix=QPixmap.fromImage(set_img)
        self.img_frame.setPixmap(pix)
        self.startButton.show()
        #print(self.face_auth.face_names)
        if len(self.face_auth.face_names) == 1:                                 #Detected 되는 사람이 한명일때
            if self.face_auth.face_names[0] in self.face_auth.known_face_names:     #입력된 정보 리스트에서  일치하는 사람이 있을 때
                self.startButton.show()
                self.match_true.show()
                self.warning_msg.hide()
                self.match_false.hide()
        else:
            self.warning_msg.show()
            self.match_false.show()
            self.startButton.hide()
            self.match_true.hide()

    def gotoStartExam(self) :
        print('3')
        self.timer.stop()
        self.face_auth.stop()
        startexam=StartExam(CameraWindow.get_sn,CameraWindow.get_en,self.face_auth.known_face_names,self.face_auth.known_face_encodings)
        widget.addWidget(startexam)
        widget.setCurrentIndex(widget.currentIndex()+1)


class StartExam(QMainWindow):
    def __init__(self, sn, en,known_face_names,known_face_encodings):
        super(StartExam,self).__init__()
        loadUi("ui/ExamWindow.ui",self)
        self.__running=False
        self.label_sn_set.setText(sn)
        self.label_en_set.setText(en)
        self.label_title_set.setText(title)
        self.label_time_set.setText(start_date[:16]+' - '+end_date[11:16])
        self.exam_ongoing_alert.setText("시험 대기 중")
        self.finishButton.clicked.connect(self.finishExam)
        self.known_face_names=known_face_names
        self.known_face_encodings=known_face_encodings
        self.sn=sn
        self.en=en
        global ss
        global ee
        ss=sn
        ee=en 

        self.end_time=end_date.split(' ')[1]
        self.end_hour=self.end_time.split(':')[0]
        self.end_min=self.end_time.split(':')[1]
        print("종료 :",self.end_hour+"시 ",self.end_min+"분")

        #-----------------얼굴인식 기능 주석----------------------#
        self.worker_fr=FaceRecognition(sn,en,self)
        self.worker_fr.start()
        #-----------------------------------------------------#
        
        self.program_keyboard()
        self.worker_screen=GetScreen(sn,en,self)
        self.worker_screen.start()
        


    def program_keyboard(self):
        #mac
        plf=sys.platform
        if plf=="darwin":
            print("this is mac os")
            # 감시할 프로그램 리스트
            
            name = self.process_program_list(plf)
            self.program_cnt=len(name)
            
            
            # 프로그램 차단 기능: 감시할 프로그램 개수 만큼 thread 생성
            i=0
            self.worker_program=[]
            for n in name:
                self.worker_program.append(MacKiller(n,self))
                self.worker_program[i].start()
                i+=1

            # 키보드 감시 기능: thread 생성
            self.worker_keyboard=MacKeyboardDetector(self)
            self.worker_keyboard.start()

        elif plf=="win32":
            print("this is win os")
            # 감시할 프로그램 리스트
            name=self.process_program_list(plf)
            self.program_cnt=len(name)

            # 감시할 프로그램 개수 만큼 thread 생성
            i=0
            self.worker_program=[]
            for n in name:
                self.worker_program.append(WinKiller(n,self))
                self.worker_program[i].start()
                i+=1

            # 키보드 감시 thread 생성
            self.worker_keyboard=WinKeyboardDetector(self)
            self.worker_keyboard.start()


    def process_program_list(self,plf):
        tmp=block_list.split(';')[:-1]

        list_arr=[]
        if plf=="darwin":
            if "카카오톡" in tmp:
                list_arr.append("KakaoTalk")
            if "크롬" in tmp:
                list_arr.append("Google")
            if "파이어폭스" in tmp:
                list_arr.append("Firefox")
            if "사파리" in tmp:
                list_arr.append("Safari")
            if "메모장" in tmp:
                list_arr.append("Notes")
            if "계산기" in tmp:
                list_arr.append("Calculator")
        elif plf=="win32":
            if "카카오톡" in tmp:
                list_arr.append("KakaoTalk.exe")
            if "크롬" in tmp:
                list_arr.append("chrome.exe")
            if "마이크로소프트 엣지" in tmp:
                list_arr.append("msedge.exe")
            if "파이어폭스" in tmp:
                list_arr.append("firefox.exe")
            if "메모장" in tmp:
                list_arr.append("notepad.exe")
            if "계산기" in tmp:
                list_arr.append("calc.exe")
        return list_arr
    
    def finishExam(self):
        print('came back-finish')
        self.__running=False
        qsignal.quit()

        #얼굴 인식 기능
        self.worker_fr.wait(5000)
        #키보드 감지 기능
        self.worker_keyboard.wait(5000)
        #프로그램 차단 기능
        for i in range(self.program_cnt):
            self.worker_program[i].wait(5000)
        #화면 공유 기능
        self.worker_screen.wait(5000)

        qApp.exit(0)
    

    def send_keyboard_log(self,sn,en,key):
        data = dict()
        data["type"]="부적절한 키보드 입력("+str(key)+")감지됨"
        data["date"]=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data["image"]="None"
        res=requests.post("http://"+server+"/test_room/log/" + en + "/" +sn,data=data)
        self.log_list.append(data["type"]+'\n'+data["date"]+'\n')
        print('sent')

class FaceRecognition(QThread):
    def __init__(self,sn,en,parent):
        super().__init__(parent)
        self.parent=parent
        self.end_hour=self.parent.end_hour
        self.end_min=self.parent.end_min
        self.sn=sn
        self.en=en
        self.__running=False
        self.timeout=False
        qsignal.quit_signal.connect(self.quit_signal_emitted)
        qsignal.start_signal.connect(self.start_signal_emitted)
        
    
    def run(self):
        face_recog = fr.FaceRecog(self.parent,self.sn,self.en)

        while self.__running==False:
            pass

        while self.__running:
            face_recog.get_frame()
            time.sleep(2)

        face_recog.stop()


    @pyqtSlot()
    def start_signal_emitted(self):
        print('시작신호 옴')
        self.__running=True

    def quit_signal_emitted(self):
        print('종료신호 옴')
        self.__running=False


class MacKeyboardDetector(QThread):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=False
        qsignal.quit_signal.connect(self.quit_signal_emitted)
        qsignal.start_signal.connect(self.start_signal_emitted)

    def run(self):
        while self.__running==False:
            pass

        while self.__running:
            if keyboard.is_pressed('cmd+c'):
                print("Press cmd+c Key")
                self.parent.send_keyboard_log(self.parent.sn,self.parent.en,'cmd+c')

            elif keyboard.is_pressed('cmd+v'):
                print("Press cmd+v Key")
                self.parent.send_keyboard_log(self.parent.sn,self.parent.en,'cmd+v')
            
            time.sleep(0.2)

    @pyqtSlot()
    def start_signal_emitted(self):
        print('시작신호 옴')
        self.__running=True

    def quit_signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class WinKeyboardDetector(QThread):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=False
        qsignal.quit_signal.connect(self.quit_signal_emitted)
        qsignal.start_signal.connect(self.start_signal_emitted)
    
    def run(self):
        while self.__running==False:
            pass

        while self.__running:
            if keyboard.is_pressed('ctrl'):
                print("Press Ctrl Key")
                self.parent.send_keyboard_log(self.parent.sn,self.parent.en,'Ctrl')

            elif keyboard.is_pressed('alt'):
                print("Press Alt Key")
                self.parent.send_keyboard_log(self.parent.sn,self.parent.en,'alt')

            elif keyboard.is_pressed('win'):
                print("Press Window Key")
                self.parent.send_keyboard_log(self.parent.sn,self.parent.en,'win')

    @pyqtSlot()
    def start_signal_emitted(self):
        print('시작신호 옴')
        self.__running=True

    def quit_signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class MacKiller(QThread):
    def __init__(self,n,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=False
        qsignal.start_signal.connect(self.start_signal_emitted)
        qsignal.quit_signal.connect(self.quit_signal_emitted)
        self.n=n

    def run(self):
        while self.__running==False:
            pass

        while self.__running:
            time.sleep(5) #segmentation fault 11 방지
            line= os.popen("ps ax | grep " + self.n + " | grep -v grep")
            result=line.read()
            
            if len(result)>0:
                fields = result.split()

                # extracting Process ID from the output
                pid = fields[0]
                    
                # terminating process
                os.kill(int(pid), signal.SIGKILL)
                time.sleep(1)

        print('finish killer thread')

    @pyqtSlot()
    def start_signal_emitted(self):
        print('시작신호 옴')
        self.__running=True

    def quit_signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class WinKiller(QThread):
    def __init__(self,name,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=False
        qsignal.quit_signal.connect(self.quit_signal_emitted)
        qsignal.start_signal.connect(self.start_signal_emitted)
        self.name=name
    
    def run(self):
        while self.__running==False:
            pass

        while self.__running :
            time.sleep(3)
            kill = os.system(f"taskkill /f /im {self.name}")

            if kill == 0 or kill == 1:
                print(f'{self.name} Is Running And Is Killed')
            else:
                print(f'{self.name} is Not Running')

    @pyqtSlot()
    def start_signal_emitted(self):
        print('시작신호 옴')
        self.__running=True

    def quit_signal_emitted(self):
        print('종료신호 옴')
        self.__running=False
    
class GetScreen(QThread):
    def __init__(self,sn,en,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=False
        qsignal.quit_signal.connect(self.quit_signal_emitted)
        qsignal.start_signal.connect(self.start_signal_emitted)
        self.sn=sn
        self.en=en
    
    def run(self):
        time.sleep(1)
        with mss() as sct:
            # 화면 사이즈 받아옴
            mon = sct.monitors[1]
            rect = {
                "top": mon["top"],
                "left": mon["left"],
                "width": mon["width"],
                "height": mon["height"],
                "mon": 1
            }

            im = sct.grab(rect)
            image_byte = tools.to_png(im.rgb, im.size)

            data = {
                "image": base64.b64encode(image_byte).decode()
            }
            
            while self.__running==False:
                time.sleep(0.5)
                res = requests.post('http://'+server+f'/test_room/share_screen/{self.en}/{self.sn}', data=data)
                print(res.json()["state"])
                if(res.json()["state"]=='watching') :#시작신호가 온 경우
                    self.__running=True
            
            qsignal.start()

            while self.__running:
                # 화면 캡쳐
                im = sct.grab(rect)
                image_byte = tools.to_png(im.rgb, im.size)

                data = {
                    "image": base64.b64encode(image_byte).decode()
                }

                # HTTP로 화면 이미지 전송
                res = requests.post('http://'+server+f'/test_room/share_screen/{self.en}/{self.sn}', data=data)
                if(self.__running==True and res.json()["state"]=='result') :#종료신호가 온 경우
                    self.parent.finishExam()
                else:
                    time.sleep(1)

    @pyqtSlot()
    def start_signal_emitted(self):
        print('시작신호 옴')
        self.__running=True

    def quit_signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class Controller(QObject):
    start_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def start(self):
        self.start_signal.emit()

    def quit(self):
        self.quit_signal.emit()

app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(360)
widget.setFixedHeight(530)
widget.setWindowTitle('WatchU')
widget.setWindowIcon(QIcon('./static/logo.png'))
widget.show()
qsignal=Controller()
exit=app.exec_()

if exit==0:
    print('프로그램 종료')
    image_byte = open('./static/exit.png', 'rb').read()
    data = {
                "image": base64.b64encode(image_byte).decode()
            }

    # HTTP로 화면 이미지 전송
    r = requests.post('http://'+server+'/test_room/share_screen/'+ee+'/'+ss, data=data)
    