import time
from FlightStickCode.FlightStick import FlightStick

fs = FlightStick
fs.__init__(fs)
while True:

    fs.readFlightStick(fs)
    
    yaw = round(fs.yaw, 2)
    roll = round(fs.roll, 2)
    pitch = round(fs.pitch, 2)
    throttle = round(fs.throttle, 2)
    print("yaw:", str(yaw), "   roll:", str(roll), "  pitch:", str(pitch), "   throttle:", str(throttle))
    time.sleep(.01)

