# 프로그램 감시 + 키보드 감시
import os,signal
import keyboard
import time
from threading import Thread
from tkinter import messagebox
import sys
from sys import platform
from datetime import datetime

def mac_killer():
    while True:
        # Ask user for the name of process
        try:
            for n in name:
                # iterating through each instance of the process
                for line in os.popen("ps ax | grep " + n + " | grep -v grep"):
                    fields = line.split()
             
                    # extracting Process ID from the output
                    pid = fields[0]
             
                    # terminating process
                    os.kill(int(pid), signal.SIGKILL)
                #print("Process Successfully terminated")
         
        except:
            print("Error Encountered while running script")


def mac_keyboard_detector():
    while True:
        if keyboard.is_pressed('cmd+c'):
            key='cmd+c'
            make_log(key)

        elif keyboard.is_pressed('cmd+v'):
            key='cmd+v'
            make_log(key)
        
        time.sleep(0.1)
        continue


def win_killer(name):
    while True:
        kill = os.system(f"taskkill /f /im {name}")

        if kill == 0 or kill == 1:
            print(f'{name} Is Running And Is Killed')
        else:
            print(f'{name} is Not Running')

def win_keyboard_detector():
    while True:
        if keyboard.is_pressed('ctrl+c'):
            key='Ctrl+C'
            make_log(key)

        elif keyboard.is_pressed('ctrl+v'):
            key='Ctrl+V'
            make_log(key)

        elif keyboard.is_pressed('alt'):
            key='Alt'
            make_log(key)

        elif keyboard.is_pressed('win'):
            key='Window'
            make_log(key)

        time.sleep(0.1)
        continue

def make_log(key):
    str='부적절한 키보드 입력('+key+') 감지됨'
    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(str+'/'+date)

if __name__ == "__main__":
    #mac
    if platform=="darwin":
        print("this is mac os")
        # 감시할 프로그램 리스트
        name = {"KakaoTalk", "Google","Notes","Skype" } 
    
        # 감시할 프로그램 개수 만큼 thread 생성
        for n in name:
            t = Thread(target=mac_killer)
            t.start()

        # 키보드 감시 thread 생성
        t = Thread(target=mac_keyboard_detector)
        t.start()

    elif platform=="win32":
        print("this is win os")
         # 감시할 프로그램 리스트
        name = {"KakaoTalk.exe", "Microsoft.Notes.exe", "chrome.exe", "notepad.exe", "Powerpnt.exe", "Winword.exe"}

        # 감시할 프로그램 개수 만큼 thread 생성
        for n in name:
            t = Thread(target=win_killer, args=(n,))
            t.start()

        # 키보드 감시 thread 생성
        t = Thread(target=win_keyboard_detector)
        t.start()