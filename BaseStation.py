# *---------------------------------------------------------*

# 38: libraries and imports
# 60: stuffs to install
# 73: globals
# 101: variables
# 160: def animation(current_frame
# 173: def stop_animation
# 179: def getMyIP
# 212: def setDroneName 
# 250: def updateDroneNames
# 269: def clamp(val
# 279: def introToAP
# 313: def show(key
# 347: def release(key
# 378: def MODESwarm
# 384: def MODEManual
# 390: def handshake(msg, addr
# 421: def color
# 430: def sendMessage(ipAddress, port, msg
# 444: def manualControl
# 519: def listDrones
# 525: def listen(q_out, q_in):#happens on a separate thread
# 548: def  addDrone
# 564: def kill
# 575: def arm
# 587: def navHoldFunc
# 599: def quit
# 610: def checkQueue(q_in
# 637: Real code starts here
# 676: class App(customtkinter.CTk
# 854: image functions
# 876: sockets
# 888: threads
# 904: gifs and mainloop

# *---------------------------------------------------------*
#libraries and imports
import socket
import netifaces as ni
from tkinter import *
from tkinter import ttk
import tkinter as tk
from Drone import Drone
import random as r
import _thread
from threading import Thread
from queue import Queue
from pynput.keyboard import Key, Listener
import time
import customtkinter
import platform
import tkinter
import tkinter.messagebox
from PIL import Image, GifImagePlugin, ImageTk
from collections import deque
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_ALWAYS
from FlightStickCode.FlightStick import FlightStick

#stuffs to install
# python3 -m install --upgrade pip
# python3 -m pip install customtkinter
# python3 -m pip install --upgrade Pillow
# pip3 install netifaces (for windows, make sure you have c++ build tools installed and SDK for your version)
# pip3 install pynput
# pip3 install PIL
# pip3 install hidapi



#Variable decloration for most functions of the drone including keyboard and modes
#Global ensures that functions dont create copys of variables and actually edit the right ones
#globals
global selectedDrone
global ipv4_address
global droneNumber
global killswitch
global shouldQuit
global manualyes
global selDrone
global throttle
global navHold
global UDP_IP
global going 
global pitch
global keyAU
global keyAD
global roll
global keyQ
global keyE
global keyA
global keyD
global keyW
global keyS
global keyT
global keyY
global yaw
global ip


#variables
my_image = customtkinter.CTkImage(light_image=Image.open('connecteddrone.jpg'),size=(215, 70))

colors =  ['#ff624b','#ffaf0e','#fde838','#16d511','#0995e5','#651bc8']
photoimage_objects = []

file = "Bjorn-unscreen.gif"
displayVar = "default Text"
droneName0 = "Connecting"
droneName1 = "Connecting"
droneName2 = "Connecting"
droneName3 = "Connecting"
droneName4 = "Connecting"
droneName5 = "Connecting"
droneName6 = "Connecting"
droneName7 = "Connecting"
selectedDrone = "None"

shouldQuit = False
manualyes = False
controller = True
going = False
keyAU = False
keyAD = False
keyQ = False
keyE = False
keyA = False
keyD = False
keyW = False
keyS = False
keyR = False
keyT = False
keyY = False

killswitch = 1000
throttle = 1000
navHold = 1000
armVar = 1000
pitch = 1500
roll = 1500
yaw = 1500

droneNumber = 0
UDP_IP = 0
ip = 0

dark_image=Image.open('connecteddrone.jpg')

#needed flight stick startup code
fs = FlightStick
try:
    fs.__init__(fs)
except:
    controller = False
    pass

curr_time = round(time.time()*1000)

#This function loops through the frames of a gif used to indicate connection    
def animation(current_frame=0):
    global loop
    image = photoimage_objects[current_frame]

    app.my_label.configure(image=image)
    current_frame = current_frame + 1

    if current_frame == frames:
        current_frame = 0

    loop = app.after(50, lambda: animation(current_frame))

#This simply stops the gif
def stop_animation():
    app.after_cancel(loop)

 #This function detects the local operating system and grabs the IP in slightly different ways depending

#This function detects the operating system and grabs the computers IP for networking between the AP and drones
def getMyIP():
    try:
        global ipv4_address, ip, UDP_IP, UDP_PORT
        hostname = socket.gethostname()
        print(hostname)
        print("Checking for operating system...")
        if platform.system() == ("Windows"):
            #IP ADDRESS FOR WINDOWS OS -------------------------------------------------
            print(" ")
            print("Operating system is WINDOWS")
            print(" ")
            ipv4_address = socket.gethostbyname(hostname + ".local")
            print(f"Internal IPv4 Address for {hostname}: {ipv4_address}")
            ip = ipv4_address
            #IP ADDRESS FOR WINDOWS OS -------------------------------------------------
        if platform.system() == ("Darwin"):
            # IP ADRESSS FOR MAC OS =================================================================
            print(" ")
            print("Operating system is MACOS")
            print(" ")
            ip = ni.ifaddresses('en1')[ni.AF_INET][0]['addr']
            # ip = "0.0.0.0"
            # IP ADRESSS FOR MAC OS =================================================================
        UDP_PORT = 5005
        UDP_IP = ip
        print(ip)
    except socket.gaierror as e:
        print("There was an error resolving the hostname.")
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

#This function is used by handshake to add drones with their correct names which is defined in the arduino program
def setDroneName():
            global droneName0, droneName1, droneName2, droneName3, droneName4, droneName5, droneName6, droneName7, drones, selectedDrone,app
  
            try:
                droneName0 = drones[0].name
            except:
                droneName0 = "Drone Connecting..."
            try:
                droneName1 = drones[1].name
            except:
                droneName1 = "Drone Connecting..."
            try:
                droneName2 = drones[2].name
            except:
                droneName2 = "Drone Connecting..."
            try:
                droneName3 = drones[3].name
            except:
                droneName3 = "Drone Connecting..."
            try:
                droneName4 = drones[4].name
            except:
                droneName4 = "Drone Connecting..."
            try:
                droneName5 = drones[5].name
            except:
                droneName5 = "Drone Connecting..."
            try:
                droneName6 = drones[6].name
            except:
                droneName6 = "Drone Connecting..."
            try:
                droneName7 = drones[7].name
            except:
                droneName7 = "Drone Connecting..."
            app.optionmenu_1.configure(command=lambda x: updateDroneNames(),values=[droneName0, droneName1, droneName2, droneName3, droneName4, droneName5, droneName6, droneName7])

#This function updates the list of drones held by the controller app and the option menu for selecting them
def updateDroneNames():
            global selectedDrone, selDrone,app, going 
            going = False
            try:
                app.optionmenu_1.configure(fg_color = "dark-blue")
            except:
                excepted = True
            selectedDrone = app.optionmenu_1.get() #SELECTED DRONE AS A NAME
            print("-----------------------------------------Drone List Updated-----------------------------------------")
            print("Drone " + selectedDrone + " now selected.")
            setDroneName() #updates the list

            for i in range(len(drones)):
                if (selectedDrone == str(drones[i].name)):
                    selDrone = drones[i]
                    print ("Drone " + selDrone.name + " Connected with Port: " + str(selDrone.port) + " and IP: " + str(selDrone.ipAddress))
            setDroneName()
      
#This function is used to ensure that values for control inputs are kept in acceptable values
def clamp(val):
    lowLimit = 1000
    highLimit = 2000
    if val < lowLimit:
        val = lowLimit
    if val > highLimit:
        val = highLimit   
    return val

#This function runs the initial acces point connection
def introToAP():
    global sock
    #tell the AP that we are the base station. 
    #AP needs to save that IP address to tell it to drones (so they can connect to the base station)
    sendMessage("192.168.4.22", 80, "BaseStationIP")
    print ("sent message to AP")
    print("Listening for Response from AP.........")
    #listen 
    #TODO: PUT IN A RESEND EVERY FEW SECONDS
    #CODE FOR THAT INCLUDES: curr_time = round(time.time()*1000)
    startTime = time.time()
    introCount = 1
    while True:
    #check if we need to stop--grab from q_in  
        data = b""    #the b prefix makes it byte dat
        try:
            data, addr = sock.recvfrom(1024)
            print(data)
            print("Decoding Data...")
            strData = data.decode("utf-8")
            print("Received message %s" % data)
            
            break
        except:#crdrd
            if (time.time() - startTime >= 3):
                introCount += 1
                sendMessage("192.168.4.22", 80, "BaseStationIP")
                print ("sent message to AP: ", introCount)
                startTime = time.time()
            continue
        #test the input to see if it is the confirmation code
        #if it is, we can break

#The follwing two functions are used to capture keyboard inputs
def show(key):
    global yaw, roll, pitch, throttle, keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, shouldQuit, keyR, keyT, keyY
    try:
        if key == Key.up:
            #print("Up")
            keyAU = True
            return
        if key == Key.down:
            keyAD = True
            return
        if key.char == 'q':
            keyQ = True
        if key.char == 'e':
            keyE = True
        if key.char == 'a':
            keyA = True
        if key.char == 'd':
            keyD = True
        if key.char == 'w':
            keyW = True
        if key.char == 's':
            keyS = True
        if key.char == 'p':
            shouldQuit = True
        if key.char == 'r':
            keyR = True
        if key.char == 't':
            keyT = True
        if key.char == 'y':
            keyY = True
    except:
        pass

#See above comment
def release(key):
    global keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, throttle, keyR, keyT, keyY
    try:
        if key == Key.up:
            keyAU = False
            return
        if key == Key.down:
            keyAD = False
            return
        if key.char == 'q':
            keyQ = False   
        if key.char == 'e':
            keyE = False
        if key.char == 'a':
            keyA = False
        if key.char == 'd':
            keyD = False
        if key.char == 'w':
            keyW = False
        if key.char == 's':
            keyS = False
        if key.char == 'r':
            keyR = False
        if key.char == 't':
            keyT = False
        if key.char == 'y':
            keyY = False
    except:
        pass

#This function switches from Manual to Swarm
def MODESwarm():
    global manualyes
    manualyes = False
    print("|||  MANUAL STOPPED  |||")

#This function switches from Swarm to Manual
def MODEManual():
    global manualyes
    manualyes = True
    print("|||  MANUAL ENABLED   |||")

#This function handles the initial connection when a drone's arduino reaches out to basestation
def handshake(msg, addr):
    global droneNumber,displayVar, going
    parts = msg.split("|")
    i = int(parts[1])
    if (i == -1):
        i = len(drones)
        print(i)
        print(addr)
        print(addr[1])
        drone =  Drone(i, parts[2], addr[0], addr[1])
        drones.append(drone)
        droneNumber = (droneNumber+1)
        # app.my_label.configure(text="DRONE CONNECTED", image=my_image)
        animation(current_frame=0)
        displayVar = displayVar.replace("\nChecking Que", "")
        updateDroneNames()
        going = True
        for i in range(1,len(drones)):
            displayVar += ("\nConnected: " + drones[i].name)
            app.textbox1.configure(text = displayVar)
        for adrone in drones:
            print(adrone)

    else:
        if drones[i].name == parts[2]:
            #we could update here
            drones[i].ipAddress = addr[0]
            drones[i].port = addr[1]
    #droneList.update() 

#This function is used to flash colors to indicate connectivity
def color():
    try:
        if going:
            app.optionmenu_1.configure(fg_color=colors[r.randint(0,5)])
            time.sleep(.002)
    except:
        excepted = True
        
#This function is used to send the packets of instructions to the drone
def sendMessage(ipAddress, port, msg):
    global sock, displayVar, throttle
    print("sendMessage")
    print(ipAddress)
    print(port)
    print(msg)
    print("----------------------------")    
    bMsg = msg.encode("ascii")
    sock.sendto(bMsg, (ipAddress, int(port)))
    app.textbox1.configure(text = displayVar)
    #print("sent message")
    time.sleep(0.002)

#This function is where all of the manual contol is handled
def manualControl():
    global yaw, displayVar, roll, pitch, throttle, keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, shouldQuit, manualyes, killswitch, armVar, navHold, app, keyR, sock, keyT, keyY
    global selDrone
    listener =  Listener(on_press = show, on_release = release)   
    listener.start()

    while True:
        # if keyQ:
        #     yaw -= 1
        # elif keyE:
        #     yaw += 1
        # if keyA:
        #     roll -= 1
        # elif keyD:
        #     roll += 1
        # if keyW:
        #     pitch += 1
        # elif keyS:
        #     pitch -= 1
        # if keyAU:
        #     throttle += 1
        # elif keyAD:
        #     throttle -= 1
        if keyR:
            kill()
        if keyT:
            try:
                app.checkbox_3.toggle()
                time.sleep(0.2)
            except:
                pass
        if keyY:
            try:
                app.checkbox_2.toggle()
                time.sleep(0.2)
            except:
                pass
        if shouldQuit:
            pass


        displayVar = "Throttle: " + str(throttle) + "\n Pitch: " + str(roll) + "\n Yaw: " + str(yaw) + "\n Roll: " + str(pitch) + "\nArmVar: " + str(armVar) + "\nNavHold: " + str(navHold)
        # App.textbox1.configure(text = displayVar)
        
       
        
       
        if controller:
            fs.readFlightStick(fs)
            yaw = clamp(round(fs.yaw, 2))
            roll = clamp(round(fs.roll, 2))
            pitch = clamp(round(fs.pitch, 2))
            throttle = clamp(round(fs.throttle, 2))
        else:
            print('\033[31m===========================================================================\033[0m')
            print('\033[31m- - - - NO FLIGHTSTICK CONNECTED  |  CONNECT CONTROLLER AND RESTART - - - -\033[0m')
            print('\033[31m===========================================================================\033[0m')
            displayVar = "NO FLIGHTSTICK CONNECTED | FATAL ERROR"
            try:
                throttle = int(app.slider_2.get())
            except:
                # print("e")
                pass
        
        if (manualyes == True):
            
            sendMessage(selDrone.ipAddress, selDrone.port, "MAN" + "|" + ip + "|" + str(yaw) + "|" + str(pitch) + "|" + str(roll) + "|" + str(throttle) + "|" + str(killswitch) + "|" + str(armVar) + "|" + str(navHold) + "|")
            if(killswitch == 1700):
                print("======================================KILL SWITCH ACTIVATED=======================================")
        else:
            color()
        
        time.sleep(0.01)

#This function just prints the list of drones
def listDrones():
    global drones
    for drone in drones:
        print(drone.name, drone.ipAddress, drone.port, "\t") 

#I dont atcually know what magic this function does but it is part of how we connect
def listen(q_out, q_in):#happens on a separate thread
    print("Listener Thread began")
    while True:
        #check if we need to stop--grab from q_in  
        data = b""    #the b prefix makes it byte data
        if (not q_in.empty()):
            qIn = q_in.get()
            if (qIn == "TERMINATE"):
                q_out.put("STOPPING")
                break
        try:
            data, addr = sock.recvfrom(1024)
        except:
            continue
        strData = data.decode("utf-8")
        print("Received message %s" % data)
        # strData = strData + "|" + addr[0] + "|" + str(addr[1])#the message, the ip, the port
        strData = addr[0] + "*" + str(addr[1]) + "*" + strData#the ip, the port, the message
        # the message is pipe (|) delimited. The ip, port, and message are * delimited
        q_out.put(strData) #this sends the message to the main thread
    print("goodbye")
    
#This function adds a drone object to the list
def  addDrone():
    global droneNumber, app, drones, my_image,displayVar, going
    
    #this is just to test if tkinter will add them to the listbox on a button press.
    drones.append(Drone(8, "test", "none", 17))
    droneNumber = (droneNumber+1)
    print(str(drones))
    updateDroneNames()
    going = True
    # rainbor(app)
    animation(current_frame=0)
    for i in range(1,len(drones)):
            displayVar += ("\nConnected: " + drones[i].name)
            app.textbox1.configure(text = displayVar)
    # app.my_label.configure(text="DRONE CONNECTED", image=gifplay(app.my_label,"Bjorn-unscreen.gif",1))
#This function k0..ills the drone by turning on the killswitch
def kill():
    global killswitch
    killswitch = 1700
    for n in range(0,10):
        print("======================================KILL SWITCH ACTIVATED=======================================")
    app.sidebar_button_1.configure(fg_color="Black", text="=KILLED=")
    app.radio_button_1.configure(fg_color="Red", text="Drone Killed", text_color="Red")
    app.radio_button_2.configure(fg_color="Red", text="Drone Killed", text_color="Red")
    app.radio_button_3.configure(fg_color="Red", text="Drone Killed", text_color="Red")

#This funcion sends the drone arming values
def arm():
    global armVar
    if(app.checkbox_2.get() == 1):
        armVar = 1575
        print(app.checkbox_2.get())
        print("armed!!!!!!!!!")
    else:
        armVar = 1000
        print(app.checkbox_2.get())
        print("UNarmed!!!!!!!!!")  

#This function tells the drone to hold in place
def navHoldFunc():
    global navHold
    if(app.checkbox_3.get() == 1):
        navHold = 1600
        print(app.checkbox_3.get())
        print("HOLDING!!!!!!!!!")
    else:
        navHold = 1000
        print(app.checkbox_3.get())
        print("DRIFITNG!!!!!!!!!")

#This function closes the application
def quit():
    qToComms.put("TERMINATE") #tell the subloop on the backup thread to quit.
    t = qFromComms.get(timeout=3.0)
    #give it a chance to quit
    print("all done")
    app.destroy()
    # App.destroy()
    # sys.exit()
    exit()

#This function checks and connects to drones waiting in the connection que
def checkQueue(q_in):
    global selDrone, displayVar
    global going
    if (not q_in.empty()):
        print("checking queue")
        displayVar += "\nChecking Que"
        app.textbox1.configure(text=displayVar)
        #grab the item
        #process the info
        #mark it complete
        data = q_in.get()
        parts = data.split("*")
        addr = parts[0]
        port = int(parts[1])
        msg = parts[2]
        # print(parts)
        msgParts = msg.split("|")

        cmd = msgParts[0]

        if cmd == "HND":
            #HANDSHAKE
            handshake(msg, (addr, port))
    app.after(700, checkQueue, q_in)

getMyIP()

#Real code starts here

#error protection
if UDP_IP == 0:
    print('\033[31m=========================================================\033[0m')
    print('\033[31mFATAL ERROR: IP IS 0, IP GRABBING CODE FAILED\033[0m')
    print('\033[31m=========================================================\033[0m')
if UDP_PORT == 0:
    print('\033[31m=========================================================\033[0m')
    print('\033[31mFATAL ERROR: PORT IS 0, PORT GRABBING CODE FAILED\033[0m')
    print('\033[31m=========================================================\033[0m')
print("UDP IP is " + str(UDP_IP))


#We love customTkinter for making application pretty
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
#This function clamps drone control signals to acceptable levels

#--------------------------------------------
#--------------- Main Code ------------------

qFromComms = Queue() #gets information from the comms thread
qToComms = Queue() #sends information to the comms thread
sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

terminate = False
maxDrones = 3
drones = []
#these next two lines are for testing only. Remove them
drones.append(Drone(0, "HelloWorldDrone", "10.20.18.23", 85))
droneNumber = (droneNumber+1)
selDrone = drones[0]

#-----------------------------------------------------------------------------
#------------------------------------CUSTOM TKINTER GUI-----------------------
#-----------------------------------------------------------------------------

#THIS PART IS ALL OF THE APPLICATION COMPONENTS. DONT TOUCH
class App(customtkinter.CTk):  
    def __init__(self):
        super().__init__()
        self.title("Controlling Module")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Swarm Control Module", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=lambda: kill(), text="Kill Switch", fg_color="Red")
        #self.sidebar_button_event  -------------REMOVEED TEMP FOR TEST
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=lambda: introToAP(), text="Connect To AP")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Test")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Quit")
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        self.my_label = customtkinter.CTkLabel(self, text="", height= 70, width = 210)
        self.my_label.grid(row=1, column=0, padx=5, pady=(25,50))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(0, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Manual UDP Console")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Send UDP Message")
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox1 = customtkinter.CTkLabel(self, width=250)
        self.textbox1.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Control")
        self.tabview.add("Info")
        self.tabview.add("Swarm")
        self.tabview.tab("Control").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Info").grid_columnconfigure(0, weight=1)

        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("Control"), dynamic_resizing=True) #creates the optionmenu
        self.optionmenu_1.configure(command=lambda x: updateDroneNames(),values=[droneName0, droneName1, droneName2, droneName3, droneName4, droneName5, droneName6, droneName7])
        
        self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.combobox_1 = customtkinter.CTkComboBox(self.tabview.tab("Control"),
                                                    values=["Value 1", "Value 2", "Value Long....."])
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Control"), text="Direct Command",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Info"), text="Ip, Port will be here")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        # create radiobutton frame
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Mode and Stage Control:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0, text="Swarm Mode", command=lambda: MODESwarm())
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1, text="Manual Mode", command = lambda: MODEManual())
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # create slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        self.seg_button_1 = customtkinter.CTkSegmentedButton(self.slider_progressbar_frame)
        self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical", from_=1000, to=2000)
        self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        self.slider_2.set(1000)
        self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Main Swarm Communications")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []
        for i in range(100):
            switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"Drone {i}")
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches.append(switch)

        # create checkbox and switch frame
        self.checkbox_slider_frame = customtkinter.CTkFrame(self)
        self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.checkbox_1 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame, text="Basestation Comms")
        self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_2 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame, text="ARM ME")
        self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_3 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame, text="NAV HOLD")
        self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")


        #----------- image






        listVar = StringVar(value = drones)
        #droneList = Listbox(width =10, height = 25, listvariable = listVar)
        selDroneTK = tk.StringVar()

        # set default values
        self.sidebar_button_3.configure(command=lambda: addDrone(), text="Connect to Swarm")
        self.sidebar_button_4.configure(command=lambda: quit(), hover_color='Red', fg_color='Black', text_color = 'Red4')
      
        self.checkbox_1.select()
        self.checkbox_2.configure(command=lambda: arm())
        self.checkbox_3.configure(command=lambda: navHoldFunc())
        
        self.scrollable_frame_switches[0].select()
        self.scrollable_frame_switches[4].select()
        self.radio_button_3.configure(state="disabled", text="Auto Mode")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.optionmenu_1.set("Drone List")
        self.combobox_1.set("Drones")
        self.slider_1.configure(command=self.progressbar_2.set)
        self.slider_2.configure(command=self.progressbar_3.set)
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()
        self.textbox1.configure(text = displayVar)
        self.seg_button_1.configure(values=["Sensitivity", "Throttle", "Max Range"])
        self.seg_button_1.set("Value 2")


        my_progressbar = customtkinter.CTkProgressBar(self, orientation="horizontal",
            width=200,
            height=25,
            corner_radius=15,
            mode="indeterminate",
            determinate_speed=5,
            indeterminate_speed=.5,

        )

        my_progressbar.place(anchor="center", x=405, y=450)
        my_progressbar.lift()
        my_progressbar.set(0)
        my_progressbar.start()
        
        
        #image functions
        #The following four functions are used for changing how images are displayed
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Enter a Direct UDP Drone Command:", title="Direct Command")
        print("CTkInputDialog:", dialog.get_input())

    #See above comment
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    #See above comment
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    #See above comment
    def sidebar_button_event(self):
        print("sidebar_button click")

#-----------------------------------------------------------------------------
#----------------------------- END OF FIRST GRAB -----------------------------
#-----------------------------------------------------------------------------
#sockets
#This function does socket assignment for networking stuff
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.setblocking(0)

sock.bind((UDP_IP, UDP_PORT))

print("Ready3")
#----- END OF SECOND GRAB
#-----------  WHAT WAS ALREADY HERE IS BELOW

#threads
#Starting a thread for listening
t = Thread(target=listen, args=(qFromComms, qToComms))
t.start()

#Starting the Thread for manual control
m = Thread(target=manualControl, args=())
m.start()

#Creating the App
app = App()
app.after(1000, checkQueue, qFromComms)

info = Image.open(file)
frames = info.n_frames  # number of frames

#gifs and mainloop
for i in range(frames):
    obj = tk.PhotoImage(file=file, format=f"gif -index {i}")
    # obj2 = customtkinter.CTkImage(dark_image = obj)
    photoimage_objects.append(obj)

app.mainloop()
qToComms.put("TERMINATE") #tell the subloop on the backup thread to quit.
t = qFromComms.get(timeout=3.0)
#give it a chance to quit
print("all done")
exit()

