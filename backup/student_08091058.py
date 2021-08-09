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
import face_recog as fr
import base64

def face_authorization(name):
    return name

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
        res=requests.post("http://172.30.1.2:5000/test_room/student_login/" + "fZKBi-0Y2bfSrPY" + "/" +"20150113")
        print('1')
        global student_image
        global start_date
        global end_date
        global block_list

        student_image=res.json()["student_image"]
        start_date=res.json()["start_date"]
        end_date=res.json()["end_date"]
        block_list=res.json()["block_list"]
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
            self.lineEdit_sn.clear
            self.lineEdit_en.clear
            

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
        startexam=StartExam(CameraWindow.get_sn,CameraWindow.get_en)
        widget.addWidget(startexam)
        widget.setCurrentIndex(widget.currentIndex()+1)


class StartExam(QMainWindow):
    def __init__(self, sn, en):
        super(StartExam,self).__init__()
        loadUi("ui/ExamWindow.ui",self)
        self.__running=True
        self.label_sn_set.setText(sn)
        self.label_en_set.setText(en)
        self.finishButton.clicked.connect(self.finishExam)
         
        #------------------DB-----------------------#
        #시험 종료시간에 프로그램 자동 종료 download
        #감시 프로그램 리스트 download
        #부정행위(대리시험 및 부재, 부적절한 키보드) 로그 upload


        #여기서 얼굴인식기능 함수랑 화면공유기능 함수 호출하면 됨
        
        self.program_keyboard()
        #t = Thread(target=self.getScreen, args=(sn,en,),daemon=True)
        #t.start()
        print("여기 ",end_date)
        
        end_time=end_date.split(' ')[1]
        end_hour=end_time.split(':')[0]
        end_min=end_time.split(':')[1]
        print("종료 :",end_hour+"시 ",end_min+"분")
        #face_thread = Thread(target=self.face_recognition,args=(end_hour,end_min,))
        #face_thread.start()

    def face_recognition(self, end_hour, end_min):
        face_recog = fr.FaceRecog()
        print(face_recog.known_face_names)
        while self.__running:
            face_recog.get_frame()

            currentHour = datetime.now().hour
            currentMinute = datetime.now().minute
            #if currentHour==end_hour and currentMinute==end_min:
            if currentHour==15 and currentMinute==57:
                print('나감~~')
                break
        self.finishExam()  

    def program_keyboard(self):
        #mac
        plf=sys.platform
        if plf=="darwin":
            print("this is mac os")
            # 감시할 프로그램 리스트
            
            name = self.process_program_list(plf)
            print('차단 리스트')
            print(name)
            
            # 감시할 프로그램 개수 만큼 thread 생성
            for n in name:
                t = Thread(target=self.mac_killer, args=(n,))
                t.start()

            # 키보드 감시 thread 생성
            t = Thread(target=self.mac_keyboard_detector)
            t.start()

        elif plf=="win32":
            print("this is win os")
            # 감시할 프로그램 리스트
            name=self.process_program_list(plf)

            # 감시할 프로그램 개수 만큼 thread 생성
            for n in name:
                t = Thread(target=self.win_killer, args=(n,))
                t.start()

            # 키보드 감시 thread 생성
            t = Thread(target=self.win_keyboard_detector)
            t.start()
    

    def mac_killer(self,n):
        while self.__running:

            line= os.popen("ps ax | grep " + n + " | grep -v grep")
            result=line.read()
            if len(result)>0:
                fields = result.split()

                # extracting Process ID from the output
                pid = fields[0]
                    
                # terminating process
                os.kill(int(pid), signal.SIGKILL)
                time.sleep(1)
            
    
        print('finish killer thread')

    def mac_keyboard_detector(self):
        while self.__running:
            if keyboard.is_pressed('cmd+c'):
                #messagebox.showwarning(title="Warning", message="Press Ctrl Key")
                print("Press cmd+c Key")
                self.send_keyboard_log('cmd+c')

            elif keyboard.is_pressed('cmd+v'):
                #messagebox.showwarning(title="Warning", message="Press Alt Key")
                print("Press cmd+v Key")
                self.send_keyboard_log('cmd+v')
            
            time.sleep(0.1)


    def win_killer(self,name):
        while self.__running :
            kill = os.system(f"taskkill /f /im {name}")

            if kill == 0 or kill == 1:
                print(f'{name} Is Running And Is Killed')
            else:
                print(f'{name} is Not Running')

    def win_keyboard_detector(self):
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

    def process_program_list(self,plf):
        tmp=block_list.split(';')[:-1]

        list_arr=[]
        if plf=="darwin":
            return tmp
        elif plf=="win32":
            if "KakaoTalk" in tmp:
                list_arr.append("KakaoTalk.exe")
            if "Google" in tmp:
                list_arr.append("chrome.exe")
            return list_arr

    
    def finishExam(self):
        print('came back-finish')
        #감시 쓰레드 종료
        #clientSocket.close()
        self.__running=False

        qApp.exit(0)

    def send_keyboard_log(self,key):
        data = dict()
        data["type"]="부적절한 키보드 입력("+key+")감지됨"
        data["date"]=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data["image"]="None"
        res=requests.post("http://172.30.1.2:5000/test_room/log/" + "fZKBi-0Y2bfSrPY" + "/" +"20150113",data=data)
        print('sent')


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
mainThread=threading.currentThread()
app.exec_()
