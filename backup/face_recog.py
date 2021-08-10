# face_recog.py
from typing import Counter
import face_recognition
import cv2
import camera
import os
import numpy as np
import time
from datetime import datetime
import base64
import requests

class FaceRecog():
    def __init__(self,grand,sn,en):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera()

        print('카메라 켜짐')
        time.sleep(1)
        print(grand.known_face_names)
        #face_auth에서 값을 받아옴. 잘 받아왔는지, 이걸로 충분한지 확인 필요

        # Initialize some variables
        self.face_encodings = []
        self.face_names = []
        self.absence = False
        self.start_time = ""
        self.end_time = ""
        self.known_face_names=grand.known_face_names
        self.known_face_encodings=grand.known_face_encodings
        self.sn=sn
        self.en=en

    def get_frame(self):
        # Grab a single frame of video
        frame = self.camera.get_frame()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        # Find all the faces and face encodings in the current frame of video        
        self.face_locations = face_recognition.face_locations(rgb_small_frame)
        self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

        self.face_names = []
        log=""

        #labeling one by one(지금 카메라에 잡힌 사람)
        for face_encoding in self.face_encodings:
            # See if the face is a match for the known face(s)
            distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            min_value = min(distances)
            # tolerance: How much distance between faces to consider it a match. Lower is more strict.
            # 0.6 is typical best performance.
            name = "Unknown"
            if min_value < 0.6:
                index = np.argmin(distances)
                name = self.known_face_names[index]
                #print('본인 맞음: ',name)
            else:                                           #모르는 사람이 감지되었을 때
                print("응시 대상자가 아닌 타인 감지")
                log = "응시 대상자가 아닌 타인 감지됨"
                self.send_recog_log(frame,log)

            self.face_names.append(name)

        #face_names 배열 생성 완료
        
        if len(self.face_names) > 1:                                #2명이상 감지 되었을 때
            print(str(len(self.face_names)) + '명이 감지 되었습니다')
            log = str(len(self.face_names)) + '명이 감지 되었습니다'
            #------------------DB-----------------------#
            self.send_recog_log(frame,log)
        elif len(self.face_names) == 0:   #아무도 감지 안되면
            log="아무도 없음"
            print("아무도 없음")
            
            if self.absence==False: #처음으로 세기 시작
                self.absence = True
                self.end_time = datetime.now()

            self.start_time = datetime.now()
            diff=(self.start_time - self.end_time).seconds
            if diff > 5 and diff%5 == 0:          #10초 이상 부재 일때
                log = str((self.start_time - self.end_time).seconds) + '초 동안 감지 되지 않음' 
                self.send_recog_log(frame,log)
        else:
            self.absence = False #아 왔다
            

    
    def send_recog_log(self,frame,log):
        ret, jpg = cv2.imencode('.jpg', frame)
        frame_byte = jpg.tobytes()
        
        data = dict()
        data["type"] = log
        data["date"] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data["image"]= base64.b64encode(frame_byte).decode()
        print('7')
        print('시험번호:',self.en,'학번:',self.sn)
        res = requests.post("http://172.30.1.2:5000/test_room/log/" + self.en + "/" +self.sn,data=data)
        print('sent log:',log)
        self.grand.log_list.append(log+'\n'+data["date"]+'\n')
        time.sleep(1)
        print('8')

    def stop(self):
        self.camera.stop()

