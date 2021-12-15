#!/usr/bin/python3

import motorcortex
import cv2 as cv
import mcx_tracking_cam_pb2 as tracking_cam_msg
import os
import serial
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
        self.shape = 0
        # #self.out = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 1,(640,480))
        
        # self.subscription2 = self.sub.subscribe(["root/Processing/BlobDetector/blobBuffer"], "blob", 1)
        # self.subscription2.get()
        # self.subscription2.notify(self.onBlob)
        # self.BlobsBlobs = tracking_cam_msg.Blobs

        self.subscription4 = self.sub.subscribe(["root/Processing/BlobDetectorNew/blobBuffer"], "blob", 1)
        self.subscription4.get()
        self.subscription4.notify(self.onBlobNew)

    
    # def onBlob(self,val):
    #     print("find blob")
    #     try:
    #         blobs = tracking_cam_msg.Blobs()
    #         if blobs.ParseFromString(val[0].value):
    #             print(blobs.value)
    #             self.data = blobs.value
    #     except Exception as e:
    #         print(e)

    def onImage(self,val):
        frame = cv.imdecode(np.frombuffer(val[1].value, np.uint8), -1)
        image_original = frame
        self.shape = frame.shape
        cv.waitKey(1)

    def onBlobNew(self,val):
        # print("find new blob")
        try:
            blobs = tracking_cam_msg.Blobs()
            if blobs.ParseFromString(val[0].value):
                print(blobs.value)
                self.data = blobs.value
            else:
                self.data =  None
        except Exception as e:
            print(e)

class SerialUSB():
    def __init__(self):
        self.ser = serial.Serial(
                port='/dev/ttyACM0',
                baudrate=115200)
    
    def write_data(self, data):
        data_str = str(data[0]) + ',' + str(data[1])
        data_str_bytea = data_str.encode('utf-8')
        self.ser.write(data_str_bytea)
    

    def read_data(self):
        data_str = self.ser.read(10).decode('utf-8')
        return data_str

class Car():
    def __init__(self) -> None:
        self.len_base_car = 0.17
        self.len_mass_c = 0.08  
        self.radius_whell = 0.0325
        self.shape_image = 320 # 240
    
    def tracking_red(self, data): # red color blob nomber 1, no 0   
        for index in range(len(data)):  
            if data[index].id == 0:
                cx = data[index].cx
                cy = data[index].cy    
                return [cx, cy] 
            else:
                return [None, None]

    def turn_red(self, data): #fix controller
        if  data[0] >= self.shape_image / 2 :
            flag_right = True
        else:
            flag_right = False
        cx = data[0]
        kp = 30 / 80
        if flag_right == True:
            err =  cx - self.shape_image / 2 
            if err > 80:
                turn = 30
            else:
                turn = err * kp
        else:
            err = self.shape_image / 2 - cx 
            if err > 80:
                turn =  - 30
            else:
                turn = - err * kp
        
        return turn


if __name__ == '__main__':
    tc3_ex = tc3()
    serial_1 = SerialUSB()
    car = Car()
    while True:
        try:     
            
            #print(serial_1.read_data())
            #print(tc3_ex.data[0].id)
            blob_coord = car.tracking_red(tc3_ex.data)
            #print(blob_coord)
            turn = car.turn_red(blob_coord)
            print(turn)
            data = [0, turn]
            serial_1.write_data(data)
            #print(tc3_ex.shape)
            print('----------------------------------------')
        except Exception as e:
            print(e)
            # print(e)
            # tc3_ex.req.close()
            # tc3_ex.sub.close()