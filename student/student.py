# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *

#path=os.path.dirname(os.path.realpath(__file__))
#print(path)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("MainWindow.ui",self)
        #응시하기 버튼 누르면 화면 전환
        self.startButton.clicked.connect(self.checkAccount)
    
    def checkAccount(self):
        sn=self.lineEdit_sn.text()
        en=self.lineEdit_en.text()
        #올바르면 loginSuccess=True
        #올바르지 않으면 loginSuccess=False

        #if self.loginSuccess==True:
        print("Sucessfully logged in with ",sn,"(test : ",en,")")
        startexam=startExam(sn,en)
        widget.addWidget(startexam)
        widget.setCurrentIndex(widget.currentIndex()+1)
        #else:
        #    print("Login failed! try again.")
            #mainwindow  재호출


class startExam(QMainWindow):
    def __init__(self, sn, en):
        super(startExam,self).__init__()
        loadUi("ExamWindow.ui",self)
        self.label_sn_set.setText(sn)
        self.label_en_set.setText(en)
        self.finishButton.clicked.connect(qApp.exit)

    def monitoring(self):
        #print("모니터링 작동 중")
        self.finishButton.clicked.connect(qApp.exit)

    


app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(360)
widget.setFixedHeight(480)
widget.show()
app.exec_()

        


