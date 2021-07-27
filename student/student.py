# -*- coding: utf-8 -*-
import sys, cv2, numpy, time
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("MainWindow.ui",self)
        #응시하기 버튼 누르면 화면 전환
        
        self.enterButton.clicked.connect(self.checkAccount)
        #self.title.setFont(QFont('NanumSquare_0',16))

    def checkAccount(self):
        sn=self.lineEdit_sn.text()
        en=self.lineEdit_en.text()

        #1.db 상에 존재하는지 확인 2.시험 start_time 확인
        #조건1,2 모두 충족하면 loginSuccess=True
        #그렇지 않으면 loginSuccess=False

        #if self.loginSuccess==True:
        print("Sucessfully logged in with ",sn,"(test : ",en,")")
        camerawindow=CameraWindow(sn,en)
        widget.addWidget(camerawindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        #else:
        #    print("Login failed! try again.")
            #mainwindow  재호출

class CameraWindow(QMainWindow):
    get_sn=0
    get_en=0

    def __init__(self,sn,en):
        super(CameraWindow,self).__init__()
        loadUi("CameraWindow.ui",self)
        self.startButton.hide()
        self.warning_msg.hide()
        self.match_true.hide()
        self.match_false.hide()
        CameraWindow.get_sn=sn
        CameraWindow.get_en=en

        #카메라 뿌리기
        self.cpt=cv2.VideoCapture(0)
        self.fps=24
        self.img_frame.setScaledContents(True)
        self.start()

        tmp=True # 테스트용. 본인 일치 시 true, 아닐 시 false
        if tmp==True:
            self.startButton.show()
            self.match_true.show()
            self.startButton.clicked.connect(self.gotoStartExam)
        else :
            self.warning_msg.show()
            self.match_false.show()

    def start(self) :
        self.timer=QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000./self.fps)

    def nextFrameSlot(self):
        _,cam=self.cpt.read()
        cam=cv2.cvtColor(cam,cv2.COLOR_BGR2RGB)
        cam=cv2.flip(cam,1)
        set_img=QImage(cam,cam.shape[1],cam.shape[0],QImage.Format_RGB888)
        pix=QPixmap.fromImage(set_img)
        self.img_frame.setPixmap(pix)

    def gotoStartExam(self) :
        self.timer.stop()
        print(CameraWindow.get_sn)
        print(CameraWindow.get_en)
        startexam=StartExam(CameraWindow.get_sn,CameraWindow.get_en)
        widget.addWidget(startexam)
        widget.setCurrentIndex(widget.currentIndex()+1)



class StartExam(QMainWindow):
    def __init__(self, sn, en):
        super(StartExam,self).__init__()
        loadUi("ExamWindow.ui",self)
        self.label_sn_set.setText(sn)
        self.label_en_set.setText(en)
        self.finishButton.clicked.connect(qApp.exit)
        #여기서 얼굴인식기능 함수랑 화면공유기능 함수 호출하면 됨
       
        
app=QApplication(sys.argv)
fontDB=QFontDatabase()
fontDB.addApplicationFont('./NanumSquare.ttf')
fontDB.addApplicationFont('./NanumSquareRoundB.ttf')
fontDB.addApplicationFont('./NanumSquareL.ttf')
fontDB.addApplicationFont('./NanumSquareR.ttf')
fontDB.addApplicationFont('./NanumSquare_0.ttf')
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(360)
widget.setFixedHeight(480)
widget.show()
app.exec_()