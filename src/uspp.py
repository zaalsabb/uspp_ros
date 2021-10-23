#!/usr/bin/env python3
import os
import sys
import rospy
import cv2
from CvBridge import imgmsg_to_cv2, cv2_to_imgmsg
from sensor_msgs.msg import Image, CameraInfo
import message_filters
import numpy as np
import pandas as pd
import tf2_ros

USPP_module=os.path.join(os.path.dirname(os.path.realpath(__file__)),'USPP')
sys.path.insert(0,USPP_module)

from USPP import main

class Node:

    def __init__(self):

        rospy.init_node('uspp')
       

        rospy.spin()

    def callback(self,*args):
      pass   


if __name__ == '__main__':
    Node() 

    
       
