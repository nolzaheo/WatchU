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
from tkinter import messagebox
from PIL import Image
import requests
from datetime import datetime
import io
import face_recog_without_http as fr
import base64


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
    
        
        if sn=='1' and en=='1':
            print("Sucessfully logged in with ",sn,"(test : ",en,")")
            self.statusBar().showMessage('Success')
            #knowns 폴더에 저장
            #  decode
            '''
            imgbyte = base64.b64decode(student_image)
            img=Image.open(io.BytesIO(imgbyte))
            save_path=os.path.abspath(os.getcwd())
            save_path+='/knowns/'+sn+'.jpg'
            #os.path.join(save_path,'/knowns/'+sn+'.jpg')
            print(save_path)
            img.save(save_path,'JPEG')
            print('2')'''

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
        cam=cv2.flip(cam,1)
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
        #print(CameraWindow.get_sn)
        #print(CameraWindow.get_en)
        startexam=StartExam(CameraWindow.get_sn,CameraWindow.get_en,self.face_auth.known_face_names,self.face_auth.known_face_encodings)
        widget.addWidget(startexam)
        widget.setCurrentIndex(widget.currentIndex()+1)


class StartExam(QMainWindow):
    def __init__(self, sn, en,known_face_names,known_face_encodings):
        super(StartExam,self).__init__()
        loadUi("ui/ExamWindow.ui",self)
        self.__running=True
        self.label_sn_set.setText(sn)
        self.label_en_set.setText(en)
        self.known_face_names=known_face_names
        self.known_face_encodings=known_face_encodings
        self.end_hour=24
        self.end_min=0
        self.worker_fr=FaceRecognition(self)
        self.worker_fr.start()
        self.finishButton.clicked.connect(self.finishExam)
         
        #------------------DB-----------------------#
        #시험 종료시간에 프로그램 자동 종료 download
        #감시 프로그램 리스트 download
        #부정행위(대리시험 및 부재, 부적절한 키보드) 로그 upload


        #여기서 얼굴인식기능 함수랑 화면공유기능 함수 호출하면 됨
        
        self.program_keyboard()
        #t = Thread(target=self.getScreen, args=(sn,en,),daemon=True)
        #t.start()


    def program_keyboard(self):
        #mac
        plf=sys.platform
        if plf=="darwin":
            print("this is mac os")
            # 감시할 프로그램 리스트
            
            #name = self.process_program_list(plf)
            name={'KakaoTalk','Google',}
            self.program_cnt=len(name)
            
            # 감시할 프로그램 개수 만큼 thread 생성
            i=0
            self.worker_program=[]
            for n in name:
                self.worker_program.append(MacKiller(n,self))
                self.worker_program[i].start()
                i+=1

            # 키보드 감시 thread 생성
            self.worker_keyboard=MacKeyboardDetector(self)
            self.worker_keyboard.start()

        elif plf=="win32":
            print("this is win os")
            # 감시할 프로그램 리스트
            #name=self.process_program_list(plf)
            name={'KakaoTalk.exe','chrome.exe'}
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


    def getScreen(self,sn,en):
        clientSocket = socket.socket()
        clientSocket.connect(('172.30.1.53', 8888))

        student_id=int(sn)

        with mss() as sct:
            mon = sct.monitors[1]
            rect = {
                "top": mon["top"],
                "left": mon["left"],
                "width": mon["width"],
                "height": mon["height"],
                "mon": 1
            }

            clientSocket.send(student_id.to_bytes(1024, 'big'))

            while self.__running:
                # Capture the screen
                im = sct.grab(rect)
                pixels = tools.to_png(im.rgb, im.size)

                # Send the size of the pixels length
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                clientSocket.send(bytes([size_len]))

                # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')
                clientSocket.send(size_bytes)

                # Send pixels
                clientSocket.sendall(pixels)

    
    def finishExam(self):
        print('came back-finish')
        #감시 쓰레드 종료
        #clientSocket.close()
        self.__running=False
        qsignal.run()
        self.worker_fr.wait(5000)
        self.worker_keyboard.wait(5000)

        for i in range(self.program_cnt):
            self.worker_program[i].wait(5000)

        qApp.exit(0)
    

    def send_keyboard_log(self,key):
        data = dict()
        data["type"]="부적절한 키보드 입력("+key+")감지됨"
        data["date"]=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data["image"]="None"
        res=requests.post("http://172.30.1.2:5000/test_room/log/" + "fZKBi-0Y2bfSrPY" + "/" +"20150113",data=data)
        print('sent')

class FaceRecognition(QThread):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.end_hour=self.parent.end_hour
        self.end_min=self.parent.end_min
        self.__running=True
        self.timeout=False
        qsignal.quit_signal.connect(self.signal_emitted)
        
    
    def run(self):
        face_recog = fr.FaceRecog(self.parent.known_face_names,self.parent.known_face_encodings)
        while self.__running:
            face_recog.get_frame()

            currentHour = datetime.now().hour
            currentMinute = datetime.now().minute
            if currentHour>self.end_hour or (currentHour==self.end_hour and currentMinute>=self.end_min):
                print('나감~~')
                self.timeout=True
                break

        face_recog.stop()

        if self.timeout==True:
            self.parent.finishExam()

    @pyqtSlot()
    def signal_emitted(self):
        print('종료신호 옴')
        self.__running=False


class MacKeyboardDetector(QThread):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=True
        qsignal.quit_signal.connect(self.signal_emitted)

    def run(self):
        while self.__running:
            if keyboard.is_pressed('cmd+c'):
                #messagebox.showwarning(title="Warning", message="Press Ctrl Key")
                print("Press cmd+c Key")
                #self.send_keyboard_log('cmd+c')

            elif keyboard.is_pressed('cmd+v'):
                #messagebox.showwarning(title="Warning", message="Press Alt Key")
                print("Press cmd+v Key")
                #self.send_keyboard_log('cmd+v')
            
            time.sleep(0.2)

    @pyqtSlot()
    def signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class WinKeyboardDetector(QThread):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=True
        qsignal.quit_signal.connect(self.signal_emitted)
    
    def run(self):
        while self.__running:
            if keyboard.is_pressed('ctrl'):
                messagebox.showwarning(title="Warning", message="Press Ctrl Key")
                print("Press Ctrl Key")

            elif keyboard.is_pressed('alt'):
                messagebox.showwarning(title="Warning", message="Press Alt Key")
                print("Press Alt Key")


            elif keyboard.is_pressed('win'):
                messagebox.showwarning(title="Warning", message="Press Window Key")
                print("Press Window Key")

    @pyqtSlot()
    def signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class MacKiller(QThread):
    def __init__(self,n,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=True
        qsignal.quit_signal.connect(self.signal_emitted)
        self.n=n

    def run(self):
        while self.__running:
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
    def signal_emitted(self):
        print('종료신호 옴')
        self.__running=False

class WinKiller(QThread):
    def __init__(self,name,parent):
        super().__init__(parent)
        self.parent=parent
        self.__running=True
        qsignal.quit_signal.connect(self.signal_emitted)
        self.name=name
    
    def run(self):
        while self.__running :
            kill = os.system(f"taskkill /f /im {self.name}")

            if kill == 0 or kill == 1:
                print(f'{self.name} Is Running And Is Killed')
            else:
                print(f'{self.name} is Not Running')

    @pyqtSlot()
    def signal_emitted(self):
        print('종료신호 옴')

class Controller(QObject):
    quit_signal = pyqtSignal()

    def run(self):
        self.quit_signal.emit()

app=QApplication(sys.argv)
fontDB=QFontDatabase()
fontDB.addApplicationFont('./font/NanumSquare.ttf')
fontDB.addApplicationFont('./font/NanumSquareRoundB.ttf')
fontDB.addApplicationFont('./font/NanumSquareL.ttf')
fontDB.addApplicationFont('./font/NanumSquareR.ttf')
fontDB.addApplicationFont('./font/NanumSquare_0.ttf')
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(360)
widget.setFixedHeight(480)
widget.show()
qsignal=Controller()
app.exec_()
