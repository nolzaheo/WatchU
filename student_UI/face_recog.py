# face_recog.py
import face_recognition
import cv2
import camera
import os
import numpy as np
import time
from datetime import datetime
from threading import Thread

class FaceRecog():
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.absence = False
        self.timerStart = False
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        
    def __del__(self):
        del self.camera        
    def get_frame(self):
        # Grab a single frame of video
        frame = self.camera.get_frame()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            display = False
            
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)

                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_value = min(distances)
                #print('사람 얼굴 감지됨')
                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
                name = "Unknown"
                if min_value < 0.6:
                    index = np.argmin(distances)
                    name = self.known_face_names[index]
                else:                                           #모르는 사람이 감지되었을 때
                    print("모르는 사람 감지")
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                    #------------------DB-----------------------#
                    display = True
                # if name == "Unknown":
                #     print("모르는 사람 감지")
                self.face_names.append(name)
                if len(self.face_names) > 1:                                #2명이상 감지 되었을 때
                    print(str(len(self.face_names)) + '명이 감지 되었습니다')
                    #------------------DB-----------------------#
                    display = True
            
            if len(self.face_names) == 0:   #아무도 감지 안되면
                self.absence = True
                if self.timerStart:
                    self.end_time = datetime.now()
                    self.timerStart = False

                if self.absence:
                    self.start_time = datetime.now()
                    if (self.start_time - self.end_time).seconds > 10:          #10초 이상 부재 일때
                        print('이새끼 어디감')
                    #------------------DB-----------------------#
                    else:
                        print (str((self.start_time - self.end_time).seconds) + '초 동안 감지 되지 않음')
            else:
                print(self.face_names)
                self.absence = False
                self.timerStart = True

        # Display the results
        if display == True:
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (153, 230, 255), 2)
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (153, 230, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 2)
                #cv2.imshow("Frame", frame)
            display = False

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()


if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)
    # t = Thread(target=FaceRecog.timer)
    while True:
        frame = face_recog.get_frame()
        print(type(frame))
        # if face_recog.absence == True:
        #     print('true',face_recog.start_time)
            
        # else:
        #     print('false')
        #     try:
        #         t.raise_exception()
        #         t.join()
        #     except:
        #         print('except')
        # show the frame
        #cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')
