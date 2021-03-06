# Distributed-System-Exercise
Client sends video to server and server will return the bounding box of detected objects

# 1. Usage
### 1.1. Install packages
```
pip install -r requirements.txt
```
### 1.2. Run server
```
python server.py --port 941
```
### 1.3. Run client
```
python client_multithread.py --input input.avi --output output.avi --folder temp --show_table --frame_delay 0.3 --servers 192.168.1.4:941
```
or
```
python client_multithread.py -i input.avi -o output.avi -f temp -t -d 0.3 -s 192.168.1.4:941,192.168.1.4:942
```
Note: '192.168.1.4:941' is the url that server.py will provide


# 2. Optional Arguments
### 2.1. server.py
```
optional arguments:
  -h, --help                                    show this help message and exit
  -p PORT, --port PORT                          port number
```
### 2.2. client_mulitithread.py
```
optional arguments:
  -h, --help                                    show this help message and exit
  -i INPUT, --input INPUT                       name of the recorded video
  -o OUTPUT, --output OUTPUT                    name of the processed video
  -f FOLDER, --folder FOLDER                    name of the folder used for processing
  -t, --show_table                              show result table
  -d FRAME_DELAY, --frame_delay FRAME_DELAY     frame delay when showing output video
  -s SERVERS, --servers SERVERS                 list of servers
```
