#!/usr/bin/env python3
import os
import sys
import rospy
import cv2
import CvBridge
from sensor_msgs.msg import Image, CameraInfo, CompressedImage
from std_msgs.msg import Empty
import numpy as np
import pandas as pd
from utils import *
from yolox_ros.msg import SegmentImage
import requests

class Node:

    def __init__(self):

        rospy.init_node('uspp')
        self.max_num_images = rospy.get_param('~max_num_images', 8)
        self.url = rospy.get_param('~url', 'http://localhost:5000/')

        rospy.Subscriber('/segment_image', SegmentImage, self.callback1)
        rospy.Subscriber('/segment_req', Empty, self.callback2)
        
        self.image_buffer = []
        self.bb_df = pd.DataFrame(columns=['x1', 'y1', 'x2', 'y2', 'track',
                                           'camera_pos','camera_rot'])
        self.i = 0
        rospy.spin()

    def callback1(self,*args):
        msg = args[0]
        bbsTrack = msg.bbox
        self.image_buffer.append(msg.image)
        p,q = unpack_transform(msg.transform) #unpack translation and rotation
        entry = pd.DataFrame(
                {'x1': bbsTrack.x1, 'y1': bbsTrack.y1, 'x2': bbsTrack.x2, 'y2': bbsTrack.y2,
                 'track': bbsTrack.track, 'camera_pos':[p], 'camera_rot':[q]}, index=[self.i])
        self.bb_df = self.bb_df.append(entry)
        self.i += 1

    def callback2(self,*args):
        # sample random images if there are more than max_num_images
        if len(self.bb_df) > self.max_num_images:
            bb_df_elements = self.bb_df.sample(n=self.max_num_images) #randomly sample elements
            self.image_buffer = [self.image_buffer[i] for i in bb_df_elements.index]
        else:
            bb_df_elements = self.bb_df

        # send post request containing list of images and dataframe to server
        # server returns mask   
        mask = self.send_request(self.url, bb_df_elements, self.image_buffer)

        # clear images buffer and dataframe
        self.image_buffer = []
        self.bb_df = pd.DataFrame(columns=['x1', 'y1', 'x2', 'y2', 'track',
                                           'camera_pos','camera_rot'])

    def send_request(self, url, bb_df_elements, image_buffer):
        # read and decompress images from buffer and convert them to cv2 format
        images_list = [CvBridge.compressed_imgmsg_to_cv2(image) for image in image_buffer]
        # send request to server and get mask in response
        try:
            res = requests.post(url, data = {'images':images_list}, json = bb_df_elements.to_json())
            return res.json()
        except:
            print('Error in sending request to server')
            return None

if __name__ == '__main__':
    Node() 

    
       
