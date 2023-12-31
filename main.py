import cv2
import numpy as np
from PIL import Image
from time import sleep
import threading
import serial

f = open("demofile2.txt", "a")

def get_limits(color):
    c = np.uint8([[color]])  # BGR values
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    hue = hsvC[0][0][0]  # Get the hue value

    # Handle red hue wrap-around
    if hue >= 165:  # Upper limit for divided red hue
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([180, 255, 255], dtype=np.uint8)
    elif hue <= 15:  # Lower limit for divided red hue
        lowerLimit = np.array([0, 100, 100], dtype=np.uint)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
    else:
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

    return lowerLimit, upperLimit

def object_detection(ser):
    yellow=[0,255,255]
    #cap=cv2.VideoCapture("http://192.168.173.165:8080/video")
    cap=cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    print("height:",cv2.CAP_PROP_FRAME_HEIGHT)
    print("width",cv2.CAP_PROP_FRAME_WIDTH)
    #"http://192.168.173.165:8080/video"
    while True:
        ret,frame=cap.read()
        hsvImage=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        lowerLimit, upperLimit=get_limits(color=yellow)

        mask=cv2.inRange(hsvImage,lowerLimit,upperLimit)

        mask_=Image.fromarray(mask)

        bbox=mask_.getbbox()    

        if bbox is not None:
            x1,y1,x2,y2=bbox

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),5)

            # Ekranın merkezine olan uzaklığı hesapla
            screen_center_x = frame.shape[1] // 2
            screen_center_y = frame.shape[0] // 2
            moments = cv2.moments(mask)
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            distance_y = cy - screen_center_y
            distance_x=cx-screen_center_x
            distance_text = f"Distance_Y: {distance_y}"
            distance_text2=f"Distance_X:{distance_x}"
            cv2.putText(frame, distance_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, distance_text2, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            timer=cv2.getTickCount()
            fps=cv2.getTickFrequency()/(cv2.getTickCount()-timer)
            cv2.putText(frame,"fps:"+str(int(fps)),(50,250),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.circle(frame, (cx,cy), 7, (255, 255, 255), -1)
            servo_function(distance_y,distance_x,frame,ser)
        cv2.imshow("frame",frame)
        if cv2.waitKey(1) & 0xff == ord("q") or cv2.waitKey(1) & 0xff == ord("Q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# def servo_function(distance_y,frame,ser):
#     while True:
#         if distance_y==0:
#             ser.write(b'90\n')
#             #f.write("distance="+str(distance_y)+" "+str(90)+"\n")
#             break
#         else:
#             ser.write(bytes(str(distance_y) + '\n', 'utf-8')) 
#             #f.write("distance="+str(distance_y)+" "+((str(map(distance_y, 360, -360, 180, 0))))+"\n")   
#             break
        
    """
    def servo_function(distance_y, distance_x, frame, ser):
    while True:
        if distance_y == 0 and distance_x == 0:
            ser.write(b'90\n')
            break
        else:
            ser.write(bytes(str(distance_y) + ',' + str(distance_x) + '\n', 'utf-8')) 
            break

    """
def servo_function(distance_y, distance_x, frame, ser):
    while True:
        if distance_y == 0 and distance_x == 0:
            ser.write(b'90\n')
            break
        else:
            ser.write(bytes(str(distance_y) + ',' + str(distance_x) + '\n', 'utf-8')) 
            break

try:
    ser = serial.Serial('COM6', 9600)
except serial.SerialException as e:
    print(f"Could not open port: {e}")
    ser = None

if ser is not None:
    t1=threading.Thread(target=object_detection, args=(ser,))
    t2=threading.Thread(target=servo_function, args=(ser,))

    t1.start()
    t2.start()



