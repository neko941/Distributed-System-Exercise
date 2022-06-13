import os
import re
import cv2
import time
import json
import random
import argparse
import requests
import threading
from progress.bar import Bar
from rich.table import Table
from datetime import datetime
from rich.console import Console

data = []
threads = []
file_extension = '.jpg'
col_names=["Server", "Time", "ImgPath", "Class", "Name", "Confidence", "Xmin", "Ymin", "Xmax", "Ymax"]

def mkdir(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

def delete_temp(folder, all=True, file_extension='.jpg'):
    if os.path.exists(folder):
        for i in os.listdir(folder):
            if not all:
                if i.endswith(file_extension):
                    os.remove(f'{folder}/'+i)
            else:
                os.remove(f'{folder}/'+i)

def record_video(video_path, fps):
    cam=cv2.VideoCapture(0, cv2.CAP_DSHOW)
    width= int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height= int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer= cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MPEG'), fps, (width, height))

    while True:
        ret,frame= cam.read()
        writer.write(frame)

        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)

        if  key == 27:
            break
        
        if key == 32:
            break
    cam.release()
    writer.release()    
    cv2.destroyAllWindows()
    return width, height

def video_to_images(video_path, dir_out, fram_name='frame', file_extension='.jpg'):
    count = 0
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret,frame = cap.read()
        if ret:
            frame_path = os.path.join(dir_out, f'{fram_name}{count}{file_extension}')
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
    
    return count

def get_sublists(lst, n): 
  subListLength = len(lst) // n 
  list_of_sublists = [] 
  for i in range(0, len(lst), subListLength): 
    list_of_sublists.append(lst[i:i+subListLength]) 
  if len(list_of_sublists) > n:
    for index in range(len(list_of_sublists[-1])):
      list_of_sublists[index].append(list_of_sublists[-1][index])
    del list_of_sublists[-1]
  return list_of_sublists

def print_table(data, col_names):
    print()

    console = Console()
    
    table = Table(show_header=True, header_style="bold magenta")
    for name in col_names:
        table.add_column(name, justify="center")

    for item in data:
        table.add_row(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9])
    console.print(table)

def natural_keys(text):
  def atoi(text):
    return int(text) if text.isdigit() else text
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def show_output(video_path, frame_delay):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    while(1):
        try:
            time.sleep(frame_delay)
            ret, frame = cap.read()
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q') or ret==False or 0xFF == 27:
                cap.release()
                cv2.destroyAllWindows()
                break
            cv2.imshow('frame',frame)
        except:
            break

def predict(url, frame_paths, data, bar):
    for frame_path in frame_paths:
        bar.next()
        img = {'file': open(frame_path, 'rb')}
        t = datetime.now().strftime('%H:%M:%S')
        response = requests.post(url, files=img)
        
        res = json.loads(response.content.decode('utf8').replace("'", '"'))
        frame = cv2.imread(frame_path)

        for i in range(len(res['xmin'])):
            
            i = str(i)
            xmin=int(res['xmin'][i])
            ymin=int(res['ymin'][i])
            xmax=int(res['xmax'][i])
            ymax=int(res['ymax'][i])
            confidence=float(res['confidence'][i])
            aclass=int(res['class'][i])
            name=str(res['name'][i])

            data.append([url.replace("http://", ""),str(t),frame_path,str(aclass),name,str(confidence),str(xmin),str(ymin),str(xmax),str(ymax)])
            
            frame=cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(0,255,0),2)
            frame=cv2.putText(frame,str(name)+' '+str(confidence),(xmin,ymin),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv2.imwrite(frame_path, frame)
        cv2.destroyAllWindows()

def images_to_video(video_output_path, frames, width, height, fps):
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    out = cv2.VideoWriter(video_output_path,fourcc, fps, (width, height))

    
    for img in frames:
        frame = cv2.imread(img)
        out.write(frame)
    out.release()

def fix_url(urls):
    new_urls = []
    for url in urls:
        if not url.startswith('http://'):
            new_urls.append(f"http://{url}")
        else:
            new_urls.append(url)
    
    return new_urls

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='input.avi', help='name of the recorded video')
    parser.add_argument('-o', '--output', type=str, default='output.avi', help='name of the processed video')
    parser.add_argument('-f', '--folder', type=str, default='temp', help='name of the folder used for processing')
    parser.add_argument('-t', '--show_table', action='store_true', help='show result table')
    parser.add_argument('-d', '--frame_delay', type=float, default=0.2, help='frame delay when showing output video')
    parser.add_argument('-s', '--servers', help='list of servers', type=str, required=True)

    return parser.parse_args()

if __name__ == '__main__':
    opt = parse_opt()
    folder_name = opt.folder
    video_path = os.path.join(folder_name, opt.input)
    video_output_path = os.path.join(folder_name, opt.output)
    servers = fix_url(opt.servers.split(','))

    """ Display used servers """
    print("\nServers: ")
    for i, server in enumerate(servers):
        print(f"\t{i}. {server}")
    print()
    
    """ Make temp folder """
    mkdir(folder_name)

    """ Delete all files """
    delete_temp(folder=folder_name, all=True, file_extension=file_extension)

    """ Record Videos"""
    width, height = record_video(video_path=video_path, fps=20)

    """ Split into images """
    count = video_to_images(video_path=video_path, dir_out=folder_name, fram_name='frame', file_extension=file_extension)
    bar = Bar('Processing', max=count)

    """ Process images """
    frames = [os.path.join(folder_name, i) for i in os.listdir(folder_name) if i.endswith(file_extension)]
    random.shuffle(frames)
    sublists = get_sublists(frames, len(servers))
    for i in range(len(servers)):
        threads.append(threading.Thread(target=predict, args=(servers[i], sublists[i], data, bar)))
    for i in threads:
        i.start()
    for j in threads:
        j.join()

    """ Write to video """
    frames.sort(key=natural_keys)
    images_to_video(video_output_path=video_output_path, frames=frames, width=width, height=height, fps=20)

    """ Delete temp images """
    delete_temp(folder=folder_name, all=False)

    """ Show result table """
    if opt.show_table:
        data.sort(key=lambda x: natural_keys(x[2]))
        print_table(data=data, col_names=col_names)

    """ Show uotput video """
    show_output(video_path=video_output_path, frame_delay=0.2 if opt.frame_delay<0 else  opt.frame_delay)
