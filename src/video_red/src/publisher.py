#!/usr/bin/env python
#coding: utf-8

import rospy
from std_msgs.msg import String
import cv2
import numpy as np

#global koor_str = None
def talker():
    global koor_str
    koor_str = None
    pub = rospy.Publisher('publisher', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz

    ver = cv2.__version__ # Get opencv version branch
    cv2.namedWindow( "result" ) # создаем главное окно
    cap = cv2.VideoCapture(-1) # обращаемся к любой камере устройства

    for i in range (30): # прогрев камеры))
        cap.read() # читаем с камеры

    # устанавливаем уровни красного в hsv
    hsv_min = np.array((0, 100, 100), np.uint8) # для первого диапазона
    hsv_max = np.array((6, 255, 255), np.uint8)
    hsv_min1 = np.array((168, 100, 100), np.uint8) # для второго диапазона
    hsv_max1 = np.array((179, 255, 255), np.uint8)

    color_yellow = (0,255,255) # цвет координат центра на видео

    while True:
        flag, img = cap.read() # делаем снимок
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV ) # переводим rgb в hsv
        thresh = cv2.inRange(hsv, hsv_min, hsv_max) # маска для первого диапазона
        thresh1 = cv2.inRange(hsv, hsv_min1, hsv_max1) # маска для второго диапазона
        thresh_all = thresh + thresh1 # сложение масок
        thresh_all = np.uint8(thresh_all) # приводим маску к uint8
        thresh_contour = thresh_all.copy()
        # ищем контуры и складируем их в переменную contours
        #openCV version fix for findContours unpacking
        if ver[0] == "3":
            dup, contours, hierarchy = cv2.findContours( thresh_contour, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # For OpenCV 3
        else:    
            contours, hierarchy = cv2.findContours( thresh_contour, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # For OpenCV cv4
    
        # отображаем контуры поверх изображения
        cv2.drawContours( thresh_contour, contours, -1, (255,0,0), 3, cv2.LINE_AA, hierarchy, 1) 
    
        # ищем самый большой контур
        largest = None
        for contour in contours:
            if largest is None or cv2.contourArea(contour) > cv2.contourArea(largest):
                    largest = contour
                
                
        # создаем маску для самого большого контура    
        base_arr = (thresh_contour.copy()) * 0
        largest_f = [largest]
        if largest_f[0] is not None:
            cv2.drawContours(base_arr,largest_f,-1,(255,0,0),-1)
        #cv2.imshow('zeros', base_arr)    

        #cv2.imshow('contours', thresh_contour) # выводим итоговое изображение в окно
    
        # находим моменты изображения по маске
        moments = cv2.moments(base_arr, 1)
        dM01 = moments['m01']
        dM10 = moments['m10']
        dArea = moments['m00']
    
        # рассматриваем области больше 100 пикселей
        # находим центр
        if dArea > 100:
            x = int(dM10 / dArea)
            y = int(dM01 / dArea)
            cv2.circle(img, (x, y), 5, color_yellow, 2)
            cv2.putText(img, "%d-%d" % (x,y), (x+10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, color_yellow, 2) 
            koor_str = str (str(x) +','+ str(y))

        #cv2.imshow('mask', thresh_all) 
        cv2.imshow('result', img)

        ch = cv2.waitKey(5)
        if ch == ord("q"):
            break


        rospy.loginfo(koor_str)
        pub.publish(koor_str)
        koor_str = None
        rate.sleep()


       
    # Отключаем камеру
    cap.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
