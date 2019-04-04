#!/usr/bin/env python
#coding: utf-8
import rospy
from std_msgs.msg import String

koor_str = None
def callback(data):
    rospy.loginfo(rospy.get_caller_id() + "Koordinates %s", data.data)
    
def subscriber():
    rospy.init_node('subscriber', anonymous=True)
    rospy.Subscriber("publish", String, callback)
    rospy.spin()

if __name__ == '__main__':
    subscriber()
