#!/usr/bin/python3

import motorcortex
import cv2 as cv
import mcx_tracking_cam_pb2 as tracking_cam_msg
import os
from math import cos, sin, sqrt
import numpy as np

class tc3():
    def __init__(self):
        self.data = None

        # Creating empty object for parameter tree
        parameter_tree = motorcortex.ParameterTree()
        # Loading protobuf types and hashes
        motorcortex_types = motorcortex.MessageTypes()
        # Open request connection
        self.ip = "192.168.42.1"
        self.frame = "tracking_cam3"
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.req, self.sub = motorcortex.connect("ws://"+self.ip+":5558:5557", motorcortex_types, parameter_tree,
                                    certificate=dir_path+"/motorcortex.crt", timeout_ms=1000,
                                    login="root", password="vectioneer")

        self.subscription6 = self.sub.subscribe(["root/Comm_task/utilization_max","root/Processing/image"], "camera", 1)
        self.subscription6.get()
        self.subscription6.notify(self.onImage)
        #self.out = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 1,(640,480))
        
        self.subscription2 = self.sub.subscribe(["root/Processing/BlobDetector/blobBuffer"], "blob", 1)
        self.subscription2.get()
        self.subscription2.notify(self.onBlob)
        self.BlobsBlobs = tracking_cam_msg.Blobs

    
    def onBlob(self,val):
        print("find blob")
        try:
            blobs = tracking_cam_msg.Blobs()
            if blobs.ParseFromString(val[0].value):
                print(blobs.value)
                self.data = blobs.value
        except Exception as e:
            print(e)

    def onImage(self,val):
        frame = cv.imdecode(np.frombuffer(val[1].value, np.uint8), -1)
        image_original = frame
        cv.waitKey(1)

if __name__ == '__main__':
    tc3_ex = tc3()
    while True:
        try:
           print(tc3_ex.data)
        except Exception as e:
            print(e)
            tc3_ex.req.close()
            tc3_ex.sub.close()