import cv2
import numpy as np
from PIL import Image
from pyfirmata import Arduino, SERVO
from time import sleep

# Arduino ve servonun bağlantı bilgilerini burada tanımlayın
port = 'COM5'
pin = 10
board = Arduino(port)
board.digital[pin].mode = SERVO

# Servoyu hareket ettiren fonksiyon
def rotate_servo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)

# İkinci kod parçasını çalıştıran fonksiyon
def main_function():
    yellow = [0, 255, 255]
    cap = cv2.VideoCapture(0)#laptop kamerası kullanılıyor, eğer başka kamera girilecekse 1-2 rakamları ya da "http://192.168.0.19:8080/video" girilmesi gerek.
    #"http://192.168.0.19:8080/video" bu kamera telefonun kamerasıdır
    is_object_detected = False

    while True:
        ret, frame = cap.read()

        hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lowerLimit, upperLimit = get_limits(color=yellow)

        mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

        mask_ = Image.fromarray(mask)
        

        bbox = mask_.getbbox()

        if bbox is not None:
            x1, y1, x2, y2 = bbox

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
                 # Ekranın merkezine olan uzaklığı hesapla
            screen_center_x = frame.shape[1] // 2
            screen_center_y = frame.shape[0] // 2
            moments = cv2.moments(mask)
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            distance_y = cy - screen_center_y
            distance_text = f"Distance: {distance_y}"
            cv2.putText(frame, distance_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            timer=cv2.getTickCount()
            fps=cv2.getTickFrequency()/(cv2.getTickCount()-timer)
            cv2.putText(frame,str(int(fps)),(50,250),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.circle(frame, (cx,cy), 7, (255, 255, 255), -1)
            if not is_object_detected:
                rotate_servo(pin, 180)
                is_object_detected = True
        else:
            is_object_detected = False

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# Renk sınırlarını bulan fonksiyon
def get_limits(color):
    c = np.uint8([[color]])  # BGR değerleri
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    hue = hsvC[0][0][0]  # Hue değerini al

    # Kırmızı renkteki sarının sarma nedeniyle bölünmüş renk sınırlarını belirle
    if hue >= 165:  # Bölünmüş kırmızı renk sınırları için üst limit
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([180, 255, 255], dtype=np.uint8)
    elif hue <= 15:  # Bölünmüş kırmızı renk sınırları için alt limit
        lowerLimit = np.array([0, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
    else:
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

    return lowerLimit, upperLimit

main_function()
