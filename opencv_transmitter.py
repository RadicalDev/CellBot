__author__ = 'jfindley'
# Run this script on the turret to bridge local stream to video_relay socket
import socket
import time
import math
import cv2
import Image
import StringIO

total = 0
frames = 0
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2.bind(("0.0.0.0", 2550))
#udp_dest = (("192.168.1.136", 2550))
udp_dest = (("192.168.1.137", 2550))
# udp_dest = (("192.168.1.43", 2550))
cam = cv2.VideoCapture(0)
cam.set(3, 320)
cam.set(4, 240)
last_time = time.time()
while True:
    x, frame = cam.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    jpg = Image.fromarray(frame_rgb)
    f = StringIO.StringIO()
    jpg.save(f, 'jpeg', quality=80)
    data = f.getvalue()
    data_len = len(data)
    s2.sendto(f.getvalue(), udp_dest)
    total += data_len
    frames += 1
    print "{4}: {2}: Sent {0} bytes to {1}: {3}".format(data_len, udp_dest, 1/(time.time()-last_time), total/1000000.0, frames)
    cv2.imshow("test", frame)
    if cv2.waitKey(30) != -1:
        break
    last_time = time.time()
    #time.sleep(1/30.0)
cam.release()