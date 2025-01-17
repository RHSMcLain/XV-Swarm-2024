import socket
import netifaces as ni
from tkinter import *
from tkinter import ttk
import tkinter as tk
from Drone import Drone
from threading import Thread
from queue import Queue
from pynput.keyboard import Key, Listener
import time
import customtkinter
import tkinter
import tkinter.messagebox
from PIL import Image
#pip3 install "requests>=2.*"
#pip3 install netifaces
#python3 -m pip install customtkinter
#python3 -m pip install --upgrade Pillow
global UDP_IP, ip, ipv4_address
ip = 0
UDP_IP = 0
def getMyIP():
    #TODO: DETECT THE CORRECT OPERATING SYSTEM SO IT DOES IT ITSELF
    try:
        global ipv4_address, ip, UDP_IP, UDP_PORT
        hostname = socket.gethostname()
        print(hostname)
        print("00000")
        #IP ADDRESS FOR WINDOWS OS -------------------------------------------------
        # ipv4_address = socket.gethostbyname(hostname + ".local")
        # print(f"Internal IPv4 Address for {hostname}: {ipv4_address}")
        # ip = ipv4_address
        #IP ADDRESS FOR WINDOWS OS -------------------------------------------------
        # 
        # IP ADRESSS FOR MAC OS =================================================================
        ip = ni.ifaddresses('en1')[ni.AF_INET][0]['addr']
        UDP_IP = ip
        # ip = "0.0.0.0"
        # IP ADRESSS FOR MAC OS =================================================================
        UDP_PORT = 5005
        print(ip)
    except socket.gaierror as e:
        print("There was an error resolving the hostname.")
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

getMyIP()


#ip = "0.0.0.0"
# UDP_IP = ipv4_address
# ip = ipv4_address
print("UDP IP is " + str(UDP_IP))

#BRENDAN CODE _____________________________________________________________________________________________________
global yaw, roll, pitch, throttle, keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, shouldQuit, navHold
yaw = 0
keyQ = False
keyE = False
roll = 0 
keyA = False
keyD = False
pitch = 0
keyW = False
keyS = False
throttle = 0
keyAU = False
keyAD = False
shouldQuit = False
global manualyes
global selDrone
global selDroneTK
manualyes = False
global droneNumber
droneNumber = 0
global selectedDrone
global killswitch
killswitch = 1000
armVar = 1000
navHold = 1000
my_image = customtkinter.CTkImage(light_image=Image.open('connecteddrone.jpg'))
dark_image=Image.open('connecteddrone.jpg')
selectedDrone = "None"
curr_time = round(time.time()*1000)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")




def clamp(val):
    lowLimit = 1000
    highLimit = 2000
    if val < lowLimit:
        val = lowLimit
    if val > highLimit:
        val = highLimit   
    return val
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

def show(key):
    global yaw, roll, pitch, throttle, keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, shouldQuit
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
    except:
        pass
def release(key):
    global keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, throttle
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
    except:
        pass
def begin():
    global manualyes
    if (manualyes == True):
        manualyes = False
        print("MANUAL STOPPED")
    elif (manualyes == False):
        manualyes = True
def MODESwarm():
    global manualyes
    manualyes = False
    print("|||  MANUAL STOPPED  |||")
def MODEManual():
    global manualyes
    manualyes = True
    print("|||  MANUAL ENABLED   |||")
# Collect all event until released
#BRENDAN CODE _____________________________________________________________________________________________________

def handshake(msg, addr):
    global droneNumber
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
        app.my_label.configure(text="DRONE CONNECTED", image=my_image, size=(150,150))
        for adrone in drones:
            print(adrone)
        #updateList()
        #sendMessage(drone.ipAddress, drone.port, "HSC|" + str(i))

    else:
        if drones[i].name == parts[2]:
            #we could update here
            drones[i].ipAddress = addr[0]
            drones[i].port = addr[1]
    #droneList.update()    
def sendMessage(ipAddress, port, msg):
    global sock
    print("sendMessage")
    print(ipAddress)
    print(port)
    print(msg)
    print("----------------------------")    
    bMsg = msg.encode("ascii")
    sock.sendto(bMsg, (ipAddress, int(port)))
    #print("sent message")
    time.sleep(0.0001)
def manualControl():
    global yaw, roll, pitch, throttle, keyQ, keyE, keyA, keyD, keyW, keyS, keyAU, keyAD, shouldQuit, manualyes, killswitch, armVar, navHold
    global selDrone
    global selDroneTK
    listener =  Listener(on_press = show, on_release = release)   
    listener.start()

    # yaw = 0
    # keyQ = False
    # keyE = False
    # roll = 0 
    # keyA = False
    # keyD = False
    # pitch = 0
    # keyW = False
    # keyS = False
    # throttle = 0
    # keyAU = False
    # keyAD = False
    # shouldQuit = False
    while True:
        if keyQ:
            yaw -= 1
        elif keyE:
            yaw += 1
        if keyA:
            roll -= 1
        elif keyD:
            roll += 1
        if keyW:
            pitch += 1
        elif keyS:
            pitch -= 1
        if keyAU:
            throttle += 1
        elif keyAD:
            throttle -= 1
        if shouldQuit:
            #listener.stop()
            #break
            pass



        if yaw > 1500 and keyQ == False and keyE == False:
            yaw -= 1
        elif yaw < 1500 and keyQ == False and keyE == False:
            yaw += 1
        if roll > 1500 and keyA == False and keyD == False:
            roll -= 1
        elif roll < 1500 and keyA == False and keyD == False:
            roll += 1
        if pitch > 1500 and keyW == False and keyS == False:
            pitch -= 1
        elif pitch < 1500 and keyW == False and keyS == False:
            pitch += 1
        # if throttle > 1000 and keyAU == False and keyAD == False:
        #     # throttle -= 1
        # elif throttle < 1000 and keyAU == False and keyAD == False:
        #     throttle += 1

        
        yaw = clamp(yaw)
        roll = clamp(roll)
        pitch = clamp(pitch)
        throttle = clamp(throttle)
        yaw = round(yaw, 2)
        roll = round(roll, 2)
        pitch = round(pitch, 2)
        throttle = round(throttle, 2)
        # print(yaw, " -- yaw")
        # print(roll, " -- roll")
        # print(pitch, " -- pitch")
        # print(throttle, " -- throttle")
        # for i in droneList.curselection():
        #     selDrone = drones[i]
            #print(selDrone)
        
        #print(selDrone.ipAddress)Fa
        if (manualyes == True):
            sendMessage(selDrone.ipAddress, selDrone.port, "MAN" + "|" + ip + "|" + str(yaw) + "|" + str(pitch) + "|" + str(roll) + "|" + str(throttle) + "|" + str(killswitch) + "|" + str(armVar) + "|" + str(navHold) + "|")
        #sendMessage(selDrone.ipAddress, selDrone.port, yaw + str(i))
        
        time.sleep(0.01)

#def updateList():
    #clear the list box
    #droneList.delete(0, len(drones)-1)

    #walk through drones
    #for i in range(len(drones)):
        #droneList.insert(i, str(drones[i]))
    #insert all the drone elements


def listDrones():
    global drones
    for drone in drones:
        print(drone.name, drone.ipAddress, drone.port, "\t") 

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
        # parts = strData.split("|")
        # print(parts)
        # cmd = parts[0]

        # if cmd == "HND":
        #     #HANDSHAKE
        #     handshake(parts, addr)
    print("goodbye")
def addDrone():
    global droneNumber, app
    #this is just to test if tkinter will add them to the listbox on a button press.
    drones.append(Drone(8, "test", "none", 17))
    droneNumber = (droneNumber+1)
    print(str(drones))
    app.my_label.configure(text="DRONE CONNECTED", image=my_image, size=(150,150))
def kill():
    global killswitch
    killswitch = 1700
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    print("======================================KILL SWITCH ACTIVATED=======================================")
    app.sidebar_button_1.configure(fg_color="Black", text="=KILLED=")
    app.radio_button_1.configure(fg_color="Red", text="Drone Killed", text_color="Red")
    app.radio_button_2.configure(fg_color="Red", text="Drone Killed", text_color="Red")
    app.radio_button_3.configure(fg_color="Red", text="Drone Killed", text_color="Red")
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

def quit():
    qToComms.put("TERMINATE") #tell the subloop on the backup thread to quit.
    t = qFromComms.get(timeout=3.0)
    #give it a chance to quit
    print("all done")
    app.destroy()
    App.destroy()
    exit()
def checkQueue(q_in):
    global selDrone
    global selDroneTK
    #selDroneTK.set(selDrone.ipAddress)
    #lblDroneIP.config(text = selDrone.ipAddress)
    #root.update_idletasks()
    #print(selDrone.ipAddress)
    if (not q_in.empty()):
        print("checking queue")
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
    app.after(1000, checkQueue, q_in)


#--------------------------------------------
#------------    Main Code ------------------

qFromComms = Queue() #gets information from the comms thread
qToComms = Queue() #sends information to the comms thread
sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

terminate = False
maxDrones = 3
drones = []
#these next two lines are for testing only. Remove them
drones.append(Drone(0, "one", "10.20.18.23", 85))
droneNumber = (droneNumber+1)
drones.append(Drone(1, "two", "10.20.18.23", 85))
droneNumber = (droneNumber+1)
drones.append(Drone(2, "three", "192.168.4.22", 80))
droneNumber = (droneNumber+1)
selDrone = drones[0]

#----- Setup our OLD GUI --------
#OLD GUI==============================
'''
root = Tk()
root.geometry("400x400")
root.title("Drone Manager")

frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="hello world").grid(column = 0, row = 0)
ttk.Label(frm, text="Drones List").grid(column = 0, row = 1)

listVar = StringVar(value = drones)
droneList = Listbox(master = root,width =10, height = 25, listvariable = listVar)

droneList.grid(column = 0, row = 2)
black = "black"

manualbutton = Button(root, text="Manual", width=5, height=5, command=lambda: begin()).grid(column=3, row=2, padx=50)

selDroneTK = tk.StringVar(root)
button = Button(root,text = "Test!", width=5, height=5, command=lambda: introToAP()).grid()
ttk.Label(root, text="Name | IP | Port").grid(column = 2, row = 1,padx=50)
lblDroneIP = ttk.Label(root, textvariable=selDroneTK).grid(column = 2, row = 2,padx=50)
'''


#-------------------------------------------------------------------------------------------------
#------------------------------------CUSTOM TKINTER GUI----------------------------
#-----------------------------------------------------------------------------

# #create window
# custom = customtkinter.CTk()
# custom.geometry("300x400")
# #create button
# button = customtkinter.CTkButton(master=custom, text="test")
# button.place(relx=0.5, rely=0.5, anchor=CENTER)

#run loop
#-------------custom.mainloop()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
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



        my_image = customtkinter.CTkImage(light_image=Image.open('connecteddrone.jpg'),
        dark_image=Image.open('connecteddrone.jpg'),
        size=(150,150)) # WidthxHeight
        self.my_label = customtkinter.CTkLabel(self, text="")
        self.my_label.grid(row=1, column=0, padx=2, pady=2)
        



        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Manual UDP Console")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Send UDP Message")
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Control")
        self.tabview.add("Info")
        self.tabview.add("Swarm")
        self.tabview.tab("Control").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Info").grid_columnconfigure(0, weight=1)



        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("Control"), dynamic_resizing=True) #creates the optionmenu
        selectedDrone = self.optionmenu_1.get()
        def setDroneName():
            global droneName0, droneName1, droneName2, droneName3, droneName4, droneName5, droneName6, droneName7, drones, selectedDrone
  
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
            self.optionmenu_1.configure(command=lambda x: updateDroneNames(),
                                                        values=[droneName0, droneName1, droneName2, droneName3, droneName4, droneName5, droneName6, droneName7])
        setDroneName()
        def updateDroneNames():
            global selectedDrone, selDrone
            selectedDrone = self.optionmenu_1.get() #SELECTED DRONE AS A NAME
            print("-----------------------------------------Drone List Updated-----------------------------------------")
            print("Drone " + selectedDrone + " now selected.")
            setDroneName() #updates the list

            for i in range(len(drones)):
                if (selectedDrone == str(drones[i].name)):
                    selDrone = drones[i]
                    print ("Drone " + selDrone.name + " Connected with Port: " + str(selDrone.port) + " and IP: " + str(selDrone.ipAddress))
            setDroneName()
        self.optionmenu_1.configure(command=lambda x: updateDroneNames(),
                                                        values=[droneName0, droneName1, droneName2, droneName3, droneName4, droneName5, droneName6, droneName7])
        
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
        self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
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
        self.textbox.insert("0.0", "flup\n\n" + "epic box.\n\n" * 20)
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



#image testing-----------------

    #     global my_image
    #     self.iconbitmap('images/codemy.ico')
    #     my_image = customtkinter.CTkImage(light_image=Image.open("C:\Users\Conno\Downloads\Screenshot 2024-03-28 124033.png"),
	#         dark_image=Image.open("C:\Users\Conno\Downloads\Screenshot 2024-03-28 124033.png"),
	#         size=(180,250)) # WidthxHeight

    # my_label = customtkinter.CTkLabel(root, text="", image=my_image)
    # my_label.pack(pady=10)

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Enter a Direct UDP Drone Command:", title="Direct Command")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")









#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#--------- END OF FIRST GRAB ----------
#unsure
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.bind((UDP_IP, UDP_PORT))

print("Ready3")
#----- END OF SECOND GRAB

#-----------  WHAT WAS ALREADY HERE IS BELOW
t = Thread(target=listen, args=(qFromComms, qToComms))
t.start()
m = Thread(target=manualControl, args=())
m.start()
#root.after(1000, checkQueue, qFromComms)
# root.bind("<<updateevent>>", updateDronesList)
#root.mainloop()
app = App()
app.after(1000, checkQueue, qFromComms)
app.mainloop()
qToComms.put("TERMINATE") #tell the subloop on the backup thread to quit.
t = qFromComms.get(timeout=3.0)
#give it a chance to quit
print("all done")
exit(0)
