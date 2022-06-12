# Distributed-System-Exercise
Client sends video to server and server will return the bounding box of detected objects

# Usage
### Run server
```
python server.py --port 941
```
### Run client
```
python client_multithread.py --input input.avi --output output.avi --folder temp --show_table --frame_delay 0.3 --servers 192.168.1.4:941
```
Note: '192.168.1.4:941' is the url that server.py will provide
