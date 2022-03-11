#!/usr/bin/python3

import motorcortex
import mcx_tracking_cam_pb2 as tracking_cam_msg
import os
import serial
import time
class tc3():
    def __init__(self):
        self.data = [0, 0, 0]

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

        self.shape = 0
        # #self.out = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 1,(640,480))
        
        self.subscription2 = self.sub.subscribe(["root/Processing/BlobDetector/blobBuffer"], "blob", 1)
        self.subscription2.get()
        self.subscription2.notify(self.onBlob)


    def onBlob(self,val):
        try:
            blobs = tracking_cam_msg.Blobs()
            if blobs.ParseFromString(val[0].value):
                #print('blob.value', blobs.value)
                self.data[0] = blobs.value[0].cx
                self.data[1] = blobs.value[0].cy
                self.data[2] = blobs.value[0].area
                #print(self.data)
            else:
                self.data =  None
        except Exception as e:
            print(e)

class SerialUSB():
    def __init__(self):
        self.ser = serial.Serial(
                port='/dev/ttyACM1',
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
        self.shape_image = 640 # 240

    def turn_red(self, data): #fix controller
        if  data >= self.shape_image / 2 :
            flag_right = True
        else:
            flag_right = False
        cx = data
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

    def move_forward(self, data): #fix controller
        if  data <= 1700:
            move = 70
        else:
            move = -40
            
        return move


if __name__ == '__main__':
    tc3_ex = tc3()
    serial_1 = SerialUSB()
    car = Car()
    while True:
        try:     
            #print(serial_1.read_data())
            print('cx = ', tc3_ex.data[0])
            print('area = ', tc3_ex.data[2])
            turn_car = car.turn_red(tc3_ex.data[0])
            
            move_car = car.move_forward(tc3_ex.data[2])
            data = [0, 0]
            #print(data)
            serial_1.write_data(data)
            #print(tc3_ex.shape)
            print('----------------------------------------')
            time.sleep(0.1)
        except Exception as e:
            print(e)
            # print(e)
            tc3_ex.req.close()
            tc3_ex.sub.close()