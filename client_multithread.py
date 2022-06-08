import requests
import sys
import json
import cv2
import os
import threading
from datetime import datetime
import time
import random

threads=[]
data = []
if not os.path.exists('temp'):
    os.mkdir('temp')

def delete_temp(all=True):
    if os.path.exists('temp'):
        for i in os.listdir('temp'):
            if not all:
                if i.endswith('.jpg'):
                    os.remove('temp/'+i)
            else:
                os.remove('temp/'+i)
delete_temp(True)


content_type = 'image/jpeg'
headers = {'Content-Type': content_type}
cam=cv2.VideoCapture(0, cv2.CAP_DSHOW)
width= int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_path = './temp/video.mp4'
writer= cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'DIVX'), 20, (width,height))

global frame
info = []
def predict(url, frame_paths):
    for frame_path in frame_paths:
        print(url, frame_path)
        
        img = {'file': open(f"./temp/{frame_path}", 'rb')}
        t = datetime.now().strftime('%H:%M:%S')
        response = requests.post(url, files=img)
        
        res = json.loads(response.content.decode('utf8').replace("'", '"'))
        frame = cv2.imread(f"./temp/{frame_path}")

        for i in range(len(res['xmin'])):
            
            i = str(i)
            xmin=int(res['xmin'][i])
            ymin=int(res['ymin'][i])
            xmax=int(res['xmax'][i])
            ymax=int(res['ymax'][i])
            confidence=float(res['confidence'][i])
            aclass=int(res['class'][i])
            name=str(res['name'][i])

            data.append([url.replace("http://", ""),str(t),f"./temp/{frame_path}",str(aclass),name,str(confidence),str(xmin),str(ymin),str(xmax),str(ymax)])
            
            frame=cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(0,255,0),2)
            frame=cv2.putText(frame,str(name)+' '+str(confidence),(xmin,ymin),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv2.imwrite(f"./temp/{frame_path}", frame)
        cv2.destroyAllWindows()
    
""" Record Videos"""
while True:
    ret,frame= cam.read()
    writer.write(frame)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break
    
    if cv2.waitKey(1) & 0xFF == 32:
        break
cam.release()
writer.release()    
cv2.destroyAllWindows()

""" Split into images """
cap = cv2.VideoCapture(video_path)
count = 0
while cap.isOpened():
    ret,frame = cap.read()
    if ret:
        frame_path = f"./temp/frame{count}.jpg"
        cv2.imwrite(frame_path, frame)
        count = count + 1
        
        if cv2.waitKey(10) & 0xFF == 27:
            break
        if cv2.waitKey(10) & 0xFF == 32:
            break
        
    else:
        break
cap.release()
cv2.destroyAllWindows()

resVid=[None]*count
frames = [i for i in os.listdir('temp') if i.endswith('.jpg')]
random.shuffle(frames)

threads.append(threading.Thread(target=predict, args=('http://172.16.69.233:9941', frames[:(count // 2)], )))
threads.append(threading.Thread(target=predict, args=('http://172.16.69.233:9942', frames[(count // 2) :], )))
for i in threads:
    i.start()
for j in threads:
    j.join()

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('./temp/output.mp4',fourcc, 12.0, (640,480))

thething = []
for i in range(len(frames)):
    thething.append(f"./temp/frame{i}.jpg")

for img in thething:
    frame = cv2.imread(img)
    out.write(frame)
        

out.release()
delete_temp(False)
from rich.table import Table
from rich.console import Console
console = Console()

table = Table(show_header=True, header_style="bold magenta")
for name in ["Server", "Time", "ImgPath", "Class", "Name", "Confidence", "Xmin", "Ymin", "Xmax", "Ymax"]:
    table.add_column(name, justify="center")

for item in data:
    table.add_row(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9])
console.print(table)

cap = cv2.VideoCapture("./temp/output.mp4")
ret, frame = cap.read()
while(1):
    try:
        time.sleep(0.1)
        ret, frame = cap.read()
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or ret==False or 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            break
        cv2.imshow('frame',frame)
    except:
        break
