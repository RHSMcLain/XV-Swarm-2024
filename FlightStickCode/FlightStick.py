import hid
      
class FlightStick:
    #establishing properties
    roll = 1500
    pitch = 1500
    yaw = 1500
    throttle = 1000
    gamepad = None
    

    def __init__(self):
        for device in hid.enumerate():
            print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}") 
            self.gamepad = hid.device()
            self.gamepad.open(0x044F, 0xB10A)
            self.gamepad.set_nonblocking(True)
          
  
    def readFlightStick(self):
      
        report = self.gamepad.read(16,16)
        if report:
    
            #convert for our drones
            print(report)
            self.roll =  report[3] 
            self.pitch = report[5]
            self.yaw = report[7]
            self.throttle = report[8]
            







































            # self.yaw = ((self.yaw/255) * 1000) + 1000 - 1.96
            # self.pitch  = ((self.pitch/255) * 1000) + 1000
            # self.roll  = ((self.roll/255) * 1000) + 1000      #these are commented out due to hardware issues      
            # self.throttle  = ((self.throttle/255) * 1000) + 1000
            
            
            
            #self.pitch = 1500
            #self.roll = 1500

            # print(self.roll)
            # print(self.pitch)
            # print(self.yaw)
            # print(self.throttle)
            
              # Rbutton1 = 0
        # Rbutton2 = 0
        # Rbutton3 = 0
        # Rbutton4 = 0
        # Rbutton5 = 0
        # Rbutton6 = 0
        # Rbutton7 = 0
        # Rbutton8 = 0
        # Lbutton1 = 0
        # Lbutton2 = 0
        # Lbutton3 = 0
        # Lbutton4 = 0
        # Lbutton5 = 0
        # Lbutton6 = 0
        # Lbutton7 = 0
        # Lbutton8 = 0
        # direction = "-"
        #while True:
                
                        # print(report)
            # self.roll =  report[3] 
            # self.pitch = report[5]
            # self.yaw = report[7]
            # self.throttle = report[8]

            # Rbutton1 = report[0] & 0b00000001
            # Rbutton2 = report[0] & 0b00000010
            # Rbutton3 = report[0] & 0b00000100
            # Rbutton4 = report[0] & 0b00001000
            # Rbutton5 = report[0] & 0b00010000
            # Rbutton6 = report[0] & 0b00100000
            # Rbutton7 = report[0] & 0b01000000
            # Rbutton8 = report[0] & 0b10000000

            # Lbutton1 = report[1] & 0b00000001
            # Lbutton2 = report[1] & 0b00000010
            # Lbutton3 = report[1] & 0b00000100
            # Lbutton4 = report[1] & 0b00001000
            # Lbutton5 = report[1] & 0b00010000
            # Lbutton6 = report[1] & 0b00100000
            # Lbutton7 = report[1] & 0b01000000
            # Lbutton8 = report[1] & 0b10000000
            
            # direction = "neutral"
            # if report[2] == 0:
            #     direction = "N"
            # elif report[2] == 1:
            #     direction = "NE"
            # elif report[2] == 2: 
            #     direction = "E"
            # elif report[2] == 3:
            #     direction = "SE"
            # elif report[2] == 4:
            #     direction = "S"
            # elif report[2] == 5:
            #     direction = "SW"
            # elif report[2] == 6:
            #     direction = "W"
            # elif report[2] == 7:
            #     direction = "NW"