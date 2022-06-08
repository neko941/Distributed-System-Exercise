import requests
import json
from requests_toolbelt.multipart import decoder
import cv2
import numpy as np
import socket
content_type = 'image/jpeg'
headers = {'Content-Type': content_type}
url = f"http://{socket.gethostbyname(socket.gethostname())}:9941"
print(url)
cam=cv2.VideoCapture(0, cv2.CAP_DSHOW);
global frame
while True:
    ret, frame=cam.read()
    if not ret:
        break   
    cv2.imshow('frame',frame)
    k=cv2.waitKey(1);
    if k==27:
        break
    if k==32:
        cv2.imwrite('test.jpg',frame)
        img = {'file': open('./test.jpg', 'rb')}
        response = requests.post(url, files=img)
        frame=cv2.imread('test.jpg')
        content=response.content
        content= content.decode('utf8').replace("'", '"')
        res=json.loads(content)
        for i in range(len(res['xmin'])):
            xmin=int(res['xmin'][str(i)])
            ymin=int(res['ymin'][str(i)])
            xmax=int(res['xmax'][str(i)])
            ymax=int(res['ymax'][str(i)])
            frame=cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(0,255,0),2)
            frame=cv2.putText(frame,str(res['name'][str(i)])+' '+str(res['confidence'][str(i)]),(xmin,ymin),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
        cv2.imwrite('res.jpg',frame)
        cv2.imshow('res2',frame)
        cv2.waitKey(0)
        break
cv2.destroyAllWindows()