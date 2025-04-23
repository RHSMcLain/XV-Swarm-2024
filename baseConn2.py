import socket
import netifaces as ni
from Drone import Drone
import random as r
from threading import Thread
import os
from queue import Queue
from pynput.keyboard import Key, Listener
import time
import customtkinter
import platform
from FlightStickCode.FlightStick import FlightStick

global manualYes
global appThrottle
global usingAppThrottle
global controller

global UDP_IP
global UDP_PORT
global ip
global sock
global manualControlThread
global killThreads
global app

global selectedDrone
global activeDrones

global pitch
global roll
global yaw
global throttle
global navHold
global killswitch

killswitch = 1000
throttle = 1000
navHold = 1000
armVar = 1000
pitch = 1500
roll = 1500
yaw = 1500

manualYes = False
controller = True
appThrottle = 0
usingAppThrottle = False
killThreads = False

UDP_IP = 0
ip = 0

#armvar is armed at 1575, disarmed at 1500
#fail safes: out of wifi range

fs = FlightStick
try:
    fs.__init__(fs)
except:
    controller = False
    pass

class tkConsole():
    def __init__(self, app, row=0, column=0):

        config = dict(
                    master=app, 
                    width=600, 
                    height=400,
                    corner_radius=20, 
                    border_color="grey",
                    activate_scrollbars=False,
                    border_width=7,
                    fg_color="black",
                    text_color="white"
                    )

        self.textbox = customtkinter.CTkTextbox(**config)
        self.textbox.grid(row=row, column=column)

        self.textbox.tag_config("red", foreground="red")
        
        self.textbox.insert("0.0", " "*50 +"- - - - - - - CONSOLE - - - - - - -" + " "*50 + "\n")

        self.disable()
    
    def log(self, text):
        self.enable()
        self.textbox.insert("2.0", text + "\n")
        self.disable()
    def error(self, text):
        self.enable()
        self.textbox.insert("2.0", text + "\n")
        self.textbox.tag_add("red", "2.0", "2.100")
        self.disable()
    def stick_not_connected(self):
        self.error('==================================================================')
        self.error('- - - - NO FLIGHTSTICK CONNECTED  |  CONNECT CONTROLLER AND RESTART - - - -')
        self.error('==================================================================')
    def killswitch(self):
        self.error("========================KILL SWITCH ACTIVATED=======================")
    def IP_is_zero(self):
        self.error('=================================================================')
        self.error('- - - - - - - - - - - FATAL ERROR: IP IS 0, IP GRABBING CODE FAILED - - - - - - - - - - -')
        self.error('=================================================================')
    def port_is_zero(self):
        self.error('=================================================================')
        self.error('- - - - - - - - - FATAL ERROR: PORT IS 0, PORT GRABBING CODE FAILED - - - - - - - - -')
        self.error('=================================================================')
    def grid(self,**kwargs):self.textbox.grid(**kwargs)
    def configure(self,**kwargs):self.configure(**kwargs)
    def enable(self):self.textbox.configure(state="normal")
    def disable(self):self.textbox.configure(state="disabled")
    def clear(self):
        self.enable()
        self.textbox.delete(1.0, customtkinter.END)
        app.console.textbox.insert("0.0", " "*50 +"- - - - - - - CONSOLE - - - - - - -" + " "*50 + "\n")
        self.disable()

class Button():
    def __init__(self, app, **kwargs):
        self.button = customtkinter.CTkButton(app, width=300, height=56, corner_radius=10, border_width=4, border_color="black", font=("Arial", 25, "bold"), fg_color="#63a5c5")
        self.button.configure(**kwargs)
    def grid(self,padx=10,pady=10,**kwargs):self.button.grid(padx=padx,pady=pady,**kwargs)
    def configure(self,**kwargs):self.button.configure(**kwargs)

class tkSwitch():
    def __init__(self, app, leftFunction, rightFunction, leftText="option1", rightText="option2"):
        self.leftFunction = leftFunction
        self.rightFunction = rightFunction
        
        self.baseColor = "#36719F"
        self.highLightColor = "#63a5c5"
        self.deselectedTextColor = "#B7B7B7"
        self.selectedTextColor="white"

        self.activeButton = "right"

        self.container = customtkinter.CTkFrame(master=app, width = 316, height=56, corner_radius=10, border_width=4, border_color="black", fg_color=self.baseColor)

        self.leftButton = Button(self.container,  font=("Arial", 20, "bold"), width=140, command=lambda:self.switchInteratction(), text=leftText, border_width=0,  fg_color=self.baseColor, text_color=self.deselectedTextColor, hover_color=self.baseColor)
        self.rightButton = Button(self.container, font=("Arial", 20, "bold"), width=140, command=lambda:self.switchInteratction(), text=rightText, border_width=0, fg_color=self.highLightColor, hover_color=self.highLightColor)
        self.leftButton.grid(row=0, column=0, padx=(8, 0), pady=8)
        self.rightButton.grid(row=0, column=1, padx=(0, 8), pady=8)

    def switchInteratction(self):
        if(self.activeButton == "left"):
            self.activeButton = "right"
            self.leftButton.configure (fg_color=self.baseColor,      text_color=self.deselectedTextColor, hover_color=self.baseColor)
            self.rightButton.configure(fg_color=self.highLightColor, text_color=self.selectedTextColor,   hover_color=self.highLightColor)
            self.rightFunction()
        else:
            self.activeButton = "left"
            self.leftButton.configure (fg_color=self.highLightColor, text_color=self.selectedTextColor,   hover_color=self.highLightColor)
            self.rightButton.configure(fg_color=self.baseColor,      text_color=self.deselectedTextColor, hover_color=self.baseColor)
            self.leftFunction()
    
    def grid(self, **kwargs):self.container.grid(**kwargs)

class dronActiveButton():
    def __init__(self, master):

        self.state = "inactive" #inactive, active, manual
        self.inactiveColor = "Red"
        self.activeColor = "Green"
        self.manualColor = "Yellow"

        self.currentColor = "Red"

        self.droneButton = customtkinter.CTkButton(master, width=120, height=120, command=self.onClick, hover_color=self.currentColor)

        self.setColor()

    def setColor(self):
        match self.state:
            case "inactive":
                self.currentColor = self.inactiveColor
            case "active":
               self.currentColor = self.activeColor
            case "manual":
                self.currentColor = self.manualColor
        self.droneButton.configure(fg_color=self.currentColor, hover_color=self.currentColor)

    def onClick(self):
        if (self.state == "inactive"):
            self.state = "active"
        elif (self.state == "active"):
            self.state = "manual"
        else:
            self.state = "inactive"
        
        self.setColor()

    def grid(self, **kwargs):
        self.droneButton.grid(**kwargs)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controlling Module")
        self.geometry(f"{1500}x{800}")

        #killswitch, connect to ap, add test drone, bypass controller, Manual UDP Console and Send USP Message, Mode and Stage Control
        #textbox with Throttle, Pitch, Yaw, Roll, ArmVar, and Navhold

        self.console = tkConsole(self) #Initiate Main Console

        self.leftButtonBar = customtkinter.CTkFrame(self, width=140, corner_radius=0, fg_color=self.cget("fg_color")) #Holds left buttons (killswitch, connect to ap, text drone, bypass controller, and mode switch)
        
        self.droneDisplay = customtkinter.CTkTextbox(self, activate_scrollbars=False, font=("Monaco", 20), width=305, spacing3=17, spacing1=19, fg_color="#fac771") #Orange bar left of console that displays drone throttle, pitch, yaw, etc.

        #Buttons in left button bar
        self.killswitchbutton =       Button(self.leftButtonBar, text="Kill Drones",       command=lambda:self.killswitch(), fg_color="red", hover_color="darkred")
        self.bypassControllerButton = Button(self.leftButtonBar, text="Bypass Controller", command=lambda:bypassController(self))
        self.addTestDroneButton =     Button(self.leftButtonBar, text="Add Test Drone",    command=lambda:addDrone())
        self.connectToAPButton =      Button(self.leftButtonBar, text="Connect To AP",     command=lambda:introToAP())
        
        self.manualControlSwitch = tkSwitch(self.leftButtonBar, MODEManual, MODESwarm, leftText="Manual", rightText="Swarm") #switch for Manual and Swarm modes in left button bar

        self.throttleBar = customtkinter.CTkFrame(self) #Holds all components of the in-display throttle system left of the drone display (far right)
        #These are the components in the throttle bar
        self.throttleDisplay = customtkinter.CTkTextbox(self.throttleBar, height=100, font=("Arial", 18))
        self.throttleSlider = customtkinter.CTkSlider(self.throttleBar, orientation="vertical", height=200, from_=0, to=100, command=lambda a: self.updateThrottleDisplay(a, self)) #Dont touch the aurguments
        self.displayThrottleToggleButton = customtkinter.CTkSwitch(self.throttleBar, text="Enable Display Throttle", command=lambda: self.toggleDisplayThrottle())


        #quit button
        self.quitButton = Button(self, text="TERMINATE", command=lambda: self.attemptTerinteApp(), fg_color="red", hover_color="darkred")


        self.activeDroneBar = customtkinter.CTkFrame(self, width=600)

        self.drone0Button = dronActiveButton(self.activeDroneBar)
        self.drone1Button = dronActiveButton(self.activeDroneBar)
        self.drone2Button = dronActiveButton(self.activeDroneBar)
        self.drone3Button = dronActiveButton(self.activeDroneBar)
        self.drone4Button = dronActiveButton(self.activeDroneBar)
        self.drone5Button = dronActiveButton(self.activeDroneBar)
        self.drone6Button = dronActiveButton(self.activeDroneBar)
        self.drone7Button = dronActiveButton(self.activeDroneBar)

        self.drone1Button.grid(row=0, column=1, padx=15, pady=15)
        self.drone2Button.grid(row=0, column=2, padx=15, pady=15)
        self.drone3Button.grid(row=0, column=3, padx=15, pady=15)
        self.drone0Button.grid(row=0, column=0, padx=15, pady=15)
        self.drone4Button.grid(row=1, column=0, padx=15, pady=15)
        self.drone5Button.grid(row=1, column=1, padx=15, pady=15)
        self.drone6Button.grid(row=1, column=2, padx=15, pady=15)
        self.drone7Button.grid(row=1, column=3, padx=15, pady=15)


        # Aligning all parts of the UI
        self.leftButtonBar.grid(row=0, column=0, pady=(10, 0), rowspan=4, sticky="nsew") #far left frame
        self.leftButtonBar.grid_rowconfigure(5, weight=1)

        self.killswitchbutton.grid      (row=0, column=0)
        self.bypassControllerButton.grid(row=1, column=0)
        self.addTestDroneButton.grid    (row=2, column=0)
        self.connectToAPButton.grid     (row=3, column=0)


        self.manualControlSwitch.grid   (row=4, column=0)
        self.console.grid               (row=0, column=1)
        self.droneDisplay.grid          (row=0, column=2, sticky="nsew")

        self.throttleBar.grid(row=0, column=5, rowspan=2, sticky="nsew") #far right frame

        self.throttleSlider.grid(row=1, column=0, pady=15)
        self.throttleDisplay.grid(row=0, column=0)

        self.displayThrottleToggleButton.grid(row=2, column=0, pady=(20, 0))

        self.quitButton.grid(row=3, column=0)

        self.activeDroneBar.grid(row=3, column=1)        

        #Placing text in the textboxes on bootup
        self.droneDisplay.tag_config("center", justify="center")
        self.droneDisplay.insert(0.0, "\n\nAwaiting Display Update")
        self.droneDisplay.tag_add("center", 0.0, customtkinter.END)
        self.droneDisplay.configure(state="disabled")


        #Display throttle defaults to disabled
        self.throttleDisplay.tag_config("center", justify="center")
        self.throttleDisplay.insert(0.0, "\nDisplay Throttle\nis Disabled")
        self.throttleDisplay.tag_add("center", 0.0, customtkinter.END)
        self.throttleDisplay.configure(state="disabled")

        self.throttleSlider.set(0)

        self.after(100, runAfterAppLaunch) #delay enough for the mainloop to start

    def attemptTerinteApp(self):
        #check if drones are active and deny to terminate even if one is
        tkprint("attempting termination")

        popup = customtkinter.CTkToplevel()
        popup.title("confirm terminate")

        confirmButton = Button(popup, text="confirm", command=self.terminateApp, width=150, fg_color="red", hover_color="darkred")
        cancelButton = Button(popup, text="cancel", command=popup.destroy, width=150)
        confirmButton.grid(row=0, column=0)
        cancelButton.grid(row=0, column=1)

    def terminateApp(self): #a is self for some reason
        global killThreads
        self.console.error("!!!  TERMINATING APP  !!!")
        killThreads = True

        self.after(3000, self.destroy)

    def updateThrottleDisplay(a, b, self): #Dont touch the aurguments, very finicky
        global appThrottle, usingAppThrottle

        appThrottle = int(b)
        self.throttleDisplay.configure(state="normal")
        self.throttleDisplay.delete(0.0, customtkinter.END)

        if(usingAppThrottle):
            self.throttleDisplay.insert(0.0, "\nThrottle Power\n" + str(appThrottle) + "%")
        else:
            self.throttleDisplay.insert(0.0, "\nDisplay Throttle\nis Disabled")
            self.throttleSlider.set(0)
            appThrottle = 0
            
        self.throttleDisplay.tag_add("center", 0.0, customtkinter.END)
        self.throttleDisplay.configure(state="disabled")
    
    def toggleDisplayThrottle(self):
        global usingAppThrottle, appThrottle, throttle
        usingAppThrottle = not usingAppThrottle

        if usingAppThrottle:tkprint("Display Throttle Enabled") 
        else: tkprint("Display Throttle Disabled")

        self.updateThrottleDisplay(0, self)
        appThrottle = 0
        throttle = 1000

    def killswitch(self): #not connected to killswitch right now
        self.console.killswitch()
        self.killswitchbutton.configure(text="Drones Killed", fg_color="darkred")

    def updateDroneDisplay(self):
        global throttle, roll, yaw, pitch, armVar, navHold
        self.droneDisplay.configure(state="normal")
        self.droneDisplay.tag_config("center", justify="center")
        self.droneDisplay.delete(0.0, customtkinter.END)
        self.droneDisplay.insert(0.0, 
        "Throttle: " + str(throttle) + 
        "\nPitch:    " + str(roll) + 
        "\nYaw:      " + str(yaw) + 
        "\nRoll:     " + str(pitch) + 
        "\nArmVar:   " + str(armVar) + 
        "\nNavHold:  " + str(navHold))
        self.droneDisplay.tag_add("center", 0.0, customtkinter.END)
        self.droneDisplay.configure(state="disabled")

def tkprint(text):
    app.console.log(str(text))
    #print(text)

#This function detects the operating system and grabs the computers IP for networking between the AP and drones
def getMyIP():
    try:
        global ipv4_address, ip, UDP_IP, UDP_PORT
        hostname = socket.gethostname()
        tkprint(hostname)
        tkprint("Checking for operating system...")
        if platform.system() == ("Windows"):
            #IP ADDRESS FOR WINDOWS OS -------------------------------------------------
            tkprint("Operating system is WINDOWS")
            ipv4_address = socket.gethostbyname(hostname + ".local")
            tkprint(f"Internal IPv4 Address for {hostname}: {ipv4_address}")
            ip = ipv4_address
            #IP ADDRESS FOR WINDOWS OS -------------------------------------------------
        if platform.system() == ("Darwin"):
            # IP ADRESSS FOR MAC OS =================================================================
            tkprint("Operating system is MACOS")
            ip = ni.ifaddresses('en1')[ni.AF_INET][0]['addr']
            # ip = "0.0.0.0"
            # IP ADRESSS FOR MAC OS =================================================================
        UDP_PORT = 5005
        UDP_IP = ip
        tkprint(ip)
    except socket.gaierror as e:
        tkprint("There was an error resolving the hostname.")
        tkprint(e)
    except Exception as e:
        tkprint(f"An unexpected error occurred: {e}")

def bypassController(app):
    global controller
    app.console.clear()
    app.console.log("Contoller bypassed, console cleared")
    app.bypassControllerButton.configure(text="Controller Bypassed")
    controller = True

#Sends the packets of instructions to the drone
def sendMessage(ipAddress, port, msg):
    global sock, throttle
    tkprint("sendMessage -- IP: " + str(ipAddress) + ", PORT: " + str(port) + "\n" + str(msg) + "\n----------------------------")
    bMsg = msg.encode("ascii")
    sock.sendto(bMsg, (ipAddress, int(port)))
    app.updateDroneDisplay()
    time.sleep(0.002)

#Switches from Manual to Swarm
def MODESwarm():
    global manualYes
    manualYes = False
    tkprint("|||  MANUAL STOPPED  |||")

#Switches from Swarm to Manual
def MODEManual():
    global manualYes
    manualYes = True
    tkprint("|||  MANUAL ENABLED  |||")

#This function is used to ensure that values for control inputs are kept in acceptable values
def clamp(val):
    lowLimit = 1000
    highLimit = 2000
    if val < lowLimit:
        val = lowLimit
    if val > highLimit:
        val = highLimit   
    return val

def manualControl():
    global manualYes, killswitch, throttle, yaw, roll, pitch, armVar, navHold, app, sock, killThreads, usingAppThrottle, appThrottle

    while not killThreads: #continously loop until killThreads is true

        if controller:
            try:
                fs.readFlightStick(fs)
                yaw = clamp(round(fs.yaw, 2))
                roll = clamp(round(fs.roll, 2))
                pitch = clamp(round(fs.pitch, 2))
                throttle = clamp(round(fs.throttle, 2))
            except:
                pass
        else:
            #app.console.error("NO FLIGHTSTICK CONNECTED | FATAL ERROR")
            try:
                throttle = int(app.slider_2.get())
            except:
                # print("e")
                pass

        if(manualYes):
            app.updateDroneDisplay()

            if(usingAppThrottle):
                throttle = appThrottle * 10 + 1000
        else:
            appThrottle = 0

        time.sleep(0.1)
    tkprint("Manual Control Thread terminated")

#place holder functions
def addDrone():tkprint("Trust me I added a drone.")
def introToAP():tkprint("Trust me I'm connecting to AP.")

def runAfterAppLaunch():
    global UDP_IP, UDP_PORT, sock, manualControlThread

    getMyIP()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setblocking(0)

    sock.bind((UDP_IP, UDP_PORT))

    if UDP_IP == 0:
        app.console.IP_is_zero() #send error
    if UDP_PORT == 0:
        app.console.port_is_zero() #send error
    tkprint("UDP IP is " + str(UDP_IP))


    #Starting the Thread for manual control
    manualControlThread = Thread(target=manualControl, args=())
    manualControlThread.start()

app = App()

app.mainloop()



