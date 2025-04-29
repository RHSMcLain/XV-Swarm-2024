import socket
import netifaces as ni
from Resources.Drone import Drone
import random as r
from threading import Thread
import os
from queue import Queue
from pynput.keyboard import Key, Listener
import time
from tkinter import * 
import customtkinter
import platform
from Resources.FlightStickCode.FlightStick import FlightStick
from Resources.Statics import colorPalette

global manualYes
global appThrottle
global usingAppThrottle
global controller

global UDP_IP, UDP_PORT, ip, sock
global manualControlThread
global listenerThread
global killThreads

global qFromComms
global qToComms

global app, removeDroneSelection

global pitch, roll, yaw, throttle, navHold, armVar, killswitch
global activeDrone, droneCount, selectedDrone, activeDrones, maxDrones

#default manual mode variables
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
activeDrone = -1
droneCount = 0
maxDrones = 8
removeDroneSelection = False

UDP_IP = 0
ip = 0
drones = [None]*8

#armvar is armed at 1575, disarmed at 1500
#fail safes: out of wifi range, landing drone before allowing a disable
#autoland feature where drone lands itself slowly

#the reason for all of the glitchiness in the console + drone display is they delete lines before reading them and
#the deletions don't sync with the monitor refresh rate, so you get frames where the text hasn't been inserted

#kill switch does not work in swarm mode

#sets up the flighstick
fs = FlightStick
try:
    fs.__init__(fs)
except:
    controller = False
    pass

#this is the black console, everything except sendMessage() print to it instead of the terminal
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
                    fg_color=colorPalette.console,
                    text_color="white"
                    
                    )

        self.textbox = customtkinter.CTkTextbox(**config, font=('Monaco', 13))
        self.textbox.grid(row=row, column=column)

        self.textbox.tag_config("red", foreground="red")
        self.textbox.insert("0.0", " "*17 +"- - - - - - - CONSOLE - - - - - - -" +"\n")

        self.disable()

        self.msgCount = 0
    
    def log(self, text):
        self.enable()
        self.textbox.insert("2.0", text + "\n")
        self.disable()
        self.msgCount = 0
    def error(self, text):
        self.enable()
        self.textbox.insert("2.0", text + "\n")
        self.textbox.tag_add("red", "2.0", "3.0")
        self.disable()
        self.msgCount = 0
    def logMsg(self):
        self.msgCount += 1
        self.enable()
        if self.msgCount != 1: self.textbox.delete(2.0, 3.0)
        self.textbox.insert("2.0", f"message count: {self.msgCount}\n")
        self.disable()
    def stick_not_connected(self):
        self.error('- - - - NO FLIGHTSTICK CONNECTED | CONNECT CONTROLLER AND RESTART - - - -')
    def killswitch(self):
        self.error('==========================KILL SWITCH ACTIVATED==========================')
    def IP_is_zero(self):
        self.error('=========================================================================')
        self.error('- - - - - - - FATAL ERROR: IP IS 0, IP GRABBING CODE FAILED - - - - - - -')
        self.error('=========================================================================')
    def port_is_zero(self):
        self.error('=========================================================================')
        self.error('- - - - - - FATAL ERROR: PORT IS 0, PORT GRABBING CODE FAILED - - - - - -')
        self.error('=========================================================================')
    def grid(self,**kwargs):self.textbox.grid(**kwargs)
    def configure(self,**kwargs):self.configure(**kwargs)
    def enable(self):self.textbox.configure(state="normal")
    def disable(self):self.textbox.configure(state="disabled")
    def clear(self):
        self.enable()
        self.textbox.delete(1.0, customtkinter.END)
        app.console.textbox.insert("0.0", " "*17 +"- - - - - - - CONSOLE - - - - - - -" +"\n")
        self.disable()
#Aesthetically pleasing button
class Button():
    def __init__(self, app, **kwargs):
        self.button = customtkinter.CTkButton(app, 
            width=300, 
            height=56, 
            corner_radius=10, 
            border_width=4, 
            border_color="black", 
            font=("Arial", 25, "bold"), 
            fg_color=colorPalette.buttonBlue, 
            hover_color=colorPalette.buttonBlueHover)
        
        self.button.configure(**kwargs)
    def grid(self,padx=10,pady=10,**kwargs):self.button.grid(padx=padx,pady=pady,**kwargs)
    def configure(self,**kwargs):self.button.configure(**kwargs)
#Guess what this is
class tkSwitch():
    def __init__(self, app, leftFunction, rightFunction, leftText="option1", rightText="option2"):
        self.leftFunction = leftFunction
        self.rightFunction = rightFunction
        
        self.baseColor = colorPalette.switchBack
        self.highLightColor = colorPalette.buttonBlue
        self.deselectedTextColor = "#B7B7B7"
        self.selectedTextColor="white"

        self.activeButton = "right"

        self.container = customtkinter.CTkFrame(master=app, width = 316, height=56, corner_radius=10, border_width=4, border_color="black", fg_color=self.baseColor)

        self.leftButton = Button(self.container,  font=("Arial", 20, "bold"), width=140, command=lambda:self.switchInteratction(), text=leftText, border_width=0,  fg_color=self.baseColor, text_color=self.deselectedTextColor, hover_color=self.baseColor)
        self.rightButton = Button(self.container, font=("Arial", 20, "bold"), width=140, command=lambda:self.switchInteratction(), text=rightText, border_width=0, fg_color=self.highLightColor, hover_color=self.highLightColor)
        self.leftButton.grid(row=0, column=0, padx=(8, 0), pady=8)
        self.rightButton.grid(row=0, column=1, padx=(0, 8), pady=8)

    def switchInteratction(self, callFunctions=True):
        if(self.activeButton == "left"):
            self.activeButton = "right"
            self.leftButton.configure (fg_color=self.baseColor,      text_color=self.deselectedTextColor, hover_color=self.baseColor)
            self.rightButton.configure(fg_color=self.highLightColor, text_color=self.selectedTextColor,   hover_color=self.highLightColor)
            if callFunctions:self.rightFunction()
        else:
            self.activeButton = "left"
            self.leftButton.configure (fg_color=self.highLightColor, text_color=self.selectedTextColor,   hover_color=self.highLightColor)
            self.rightButton.configure(fg_color=self.baseColor,      text_color=self.deselectedTextColor, hover_color=self.baseColor)
            if callFunctions:self.leftFunction()
    
    def grid(self, **kwargs):self.container.grid(**kwargs)
#8 of these control the connected drones
class droneActiveButton():
    def __init__(self, master, droneId):
        self.droneId = droneId
        self.state = "inactive" #inactive, active, manual
        self.inactiveColor = colorPalette.droneInactive
        self.activeColor = colorPalette.droneActive
        self.manualColor = colorPalette.droneManual
        self.inactiveHoverColor = colorPalette.droneInactiveHover
        self.activeHoverColor = colorPalette.droneActiveHover
        self.manualHoverColor = colorPalette.droneManualHover
        self.notConnectedColor = colorPalette.droneNotConnected
        self.currentColor = self.inactiveColor
        self.currentHoverColor = self.inactiveHoverColor
        self.assigned = False

        self.defaultName = "Not Connected"

        self.droneButton = customtkinter.CTkButton(
            master, 
            width=120, 
            height=120, 
            command=self.onClick, 
            hover_color=self.currentHoverColor, 
            text=self.defaultName)

        self.setColor()

    def setColor(self):

        if not self.assigned:
            self.currentColor = self.notConnectedColor
            self.currentHoverColor = self.notConnectedColor
        else:
            match self.state:
                case "inactive":
                    self.currentColor = self.inactiveColor
                    self.currentHoverColor = self.inactiveHoverColor
                case "active":
                    self.currentColor = self.activeColor
                    self.currentHoverColor = self.activeHoverColor
                case "manual":
                    self.currentColor = self.manualColor
                    self.currentHoverColor = self.manualHoverColor

        self.droneButton.configure(fg_color=self.currentColor, hover_color=self.currentHoverColor)

    def onClick(self):
        global removeDroneSelection

        if removeDroneSelection: #remove self if we are selected to delete drone
            removeDrone(self.droneId)
            removeDroneSelection = False
            return


        if (self.state == "inactive" and not manualYes and self.assigned):
            self.state = "active"
        elif (self.state != "manual" and manualYes and self.assigned):
            global activeDrone
            activeDrone = self.droneId
            buttonRefresh()
        else:
            self.state = "inactive"
            if not detectActiveDrone():
                activeDrone = -1
        
        self.setColor()

    def grid(self, **kwargs):
        self.droneButton.grid(**kwargs)
    
    def manualUpdate(self):
        global activeDrone
        if (activeDrone == self.droneId and manualYes and self.assigned):
            self.state = "manual"
        else:
            self.state = "inactive"

        self.setColor()
    
    def changeText(self, newText):
        self.droneButton.configure(text=newText)
    def getName(self): return self.droneButton.cget("text")

#The entire UI is in the app
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controlling Module")
        self.geometry(f"{1500}x{800}")
        self.configure(fg_color=colorPalette.backgroundDark)

        self.attemptingTerminate = False

        #killswitch, connect to ap, add test drone, bypass controller, Manual UDP Console and Send USP Message, Mode and Stage Control
        #textbox with Throttle, Pitch, Yaw, Roll, ArmVar, and Navhold

        self.console = tkConsole(self) #Initiate Main Console

        self.leftButtonBar = customtkinter.CTkFrame(self, width=140, corner_radius=0, fg_color=self.cget("fg_color")) #Holds left buttons (killswitch, connect to ap, text drone, bypass controller, and mode switch)
        
        self.droneDisplay = customtkinter.CTkTextbox(self, activate_scrollbars=False, font=("Monaco", 20), width=305, spacing3=17, spacing1=19, fg_color=colorPalette.droneDisplay) #Orange bar left of console that displays drone throttle, pitch, yaw, etc.

        #Buttons in left button bar
        self.killswitchbutton =       Button(self.leftButtonBar, text="Kill Drones",       command=lambda:self.killswitch(), fg_color=colorPalette.buttonRed, hover_color=colorPalette.buttonRedHover)
        self.bypassControllerButton = Button(self.leftButtonBar, text="Bypass Controller", command=lambda:bypassController(self))
        self.addTestDroneButton =     Button(self.leftButtonBar, text="Add Test Drone",    command=lambda:addDrone("Test Drone #" + str(r.randint(100, 1000)), "10.20.18.23", 85))
        self.connectToAPButton =      Button(self.leftButtonBar, text="Connect To AP",     command=lambda:introToAP())
        
        self.manualControlSwitch = tkSwitch(self.leftButtonBar, MODEManual, MODESwarm, leftText="Manual", rightText="Swarm") #switch for Manual and Swarm modes in left button bar

        self.throttleBar = customtkinter.CTkFrame(self) #Holds all components of the in-display throttle system left of the drone display (far right)
        #These are the components in the throttle bar
        self.throttleDisplay = customtkinter.CTkTextbox(self.throttleBar, height=100, font=("Arial", 18))
        self.throttleSlider = customtkinter.CTkSlider(self.throttleBar, orientation="vertical", height=200, from_=0, to=100, command=lambda a: self.updateThrottleDisplay(a, self)) #Dont touch the aurguments
        self.displayThrottleSwitch = customtkinter.CTkSwitch(self.throttleBar, text="Enable Display Throttle", command=lambda: self.toggleDisplayThrottle())

        #Holds remove drones button and terminate button
        self.lowerLeftButtonBar = customtkinter.CTkFrame(self, fg_color=self.cget("fg_color"))

        #removes right most drone in drone array
        self.removeDroneButton = Button(self.lowerLeftButtonBar, text="remove drone", command=self.select_drone_for_removal)

        #quit button
        self.quitButton = Button(self.lowerLeftButtonBar, text="TERMINATE", command=lambda: self.attemptTerminateApp(), fg_color=colorPalette.buttonRed, hover_color=colorPalette.buttonRedHover)


        self.activeDroneBar = customtkinter.CTkFrame(self, width=600)
        self.droneButtons = [None]*8
        self.activeDroneBar.grid (row=3, column=1)
        for i in range(0, 8): #creates 8 drone buttons in a 4x2 array
            self.droneButtons[i] = droneActiveButton(self.activeDroneBar, i)
            colMinus = 0
            if i > 3: colMinus = 4
            self.droneButtons[i].grid(row=round(i/8+0.1), column=i-colMinus, padx=15, pady=15)

        # Aligning all parts of the UI
        self.leftButtonBar.grid(row=0, column=0, pady=(10, 0), rowspan=4, sticky="nsew") #far left frame
        self.leftButtonBar.grid_rowconfigure(5, weight=1)

        self.killswitchbutton.grid      (row=0, column=0)
        self.bypassControllerButton.grid(row=1, column=0)
        self.addTestDroneButton.grid    (row=2, column=0)
        self.connectToAPButton.grid     (row=3, column=0)


        self.manualControlSwitch.grid   (row=4, column=0)
        self.console.grid               (row=0, column=1, padx=10, pady=10)
        self.droneDisplay.grid          (row=0, column=2, padx=(0, 10), pady=10, sticky="nsew")

        self.throttleBar.grid                (row=0, column=5, rowspan=2, sticky="nsew") #far right frame
        self.throttleSlider.grid             (row=1, column=0, pady=15)
        self.throttleDisplay.grid            (row=0, column=0)
        self.displayThrottleSwitch.grid      (row=2, column=0, pady=(20, 0))

        self.lowerLeftButtonBar.grid(row=3, column=0)
        self.removeDroneButton.grid (row=0, column=0)
        self.quitButton.grid        (row=1, column=0)      

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
    #creates a popup window asking user if they want to quit the app
    def attemptTerminateApp(self):
        
        if self.attemptingTerminate:
            tkprint("allready attempting to terminate")
            return

        self.attemptingTerminate = True

        tkprint("attempting termination")
        #check if drones are active and deny to terminate even if one is
        if detectActiveDrone():
            self.console.error("Failsafe: AT LEAST ONE DRONE IS ACTIVE -- failed to close app")
            self.attemptingTerminate = False
            return

        popup = customtkinter.CTkToplevel()
        popup.title("confirm terminate")
        popup.attributes("-topmost", True)

        confirmButton = Button(popup, text="confirm", command=self.terminateApp, width=150, fg_color=colorPalette.buttonRed, hover_color=colorPalette.buttonRedHover)
        cancelButton = Button(popup, text="cancel", command=lambda: self.destroyPopup(popup), width=150)
        confirmButton.grid(row=0, column=0)
        cancelButton.grid(row=0, column=1)
    #kills all threads then shutsdown when those threads have ended
    def terminateApp(self):
        global killThreads
        self.console.error("!!!  TERMINATING APP  !!!")
        killThreads = True

        self.after(750, self.destroy) #more time than checkQueue update loop delays
    #kills the popup window
    def destroyPopup(self, popup):
        self.attemptingTerminate = False
        popup.destroy()
    #if using the far right in-app throttle then this will update the display showing the %
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
    #runs when the switch to turn on/off the app throttle is clicked
    def toggleDisplayThrottle(self, runFunction=True):
        global usingAppThrottle, appThrottle, throttle

        if not runFunction: return

        if detectActiveDrone(): 
            self.console.error("Failsafe -- Can't toggle the app throttle while a drone is active")
            if usingAppThrottle:self.displayThrottleSwitch.select()
            else:self.displayThrottleSwitch.deselect()
            return
        if not manualYes: #can't have the display throttle be on in swarm mode
            tkprint("app throttle only available in manual mode")
            self.displayThrottleSwitch.deselect()
            usingAppThrottle = False
            self.updateThrottleDisplay(0, self)
            appThrottle = 0
            throttle = 1000
            return

        usingAppThrottle = not usingAppThrottle

        if usingAppThrottle:tkprint("Display Throttle Enabled") 
        else: tkprint("Display Throttle Disabled")

        self.updateThrottleDisplay(0, self)
        appThrottle = 0
        throttle = 1000
    #sets manual killswitch to 1700
    def killswitch(self):
        global killswitch
        killswitch = 1700
        self.console.killswitch()
        self.killswitchbutton.configure(text="Drones Killed", fg_color="darkred")
    #grabs the manual mode variables and displays them in the orange display
    def updateDroneDisplay(self):
        global throttle, roll, yaw, pitch, armVar, navHold
        displayText = f"Throttle: {round(throttle)}\nPitch:    {round(roll)}\nYaw:      {round(yaw)}\nRoll:     {round(pitch)}\nArmVar:   {round(armVar)}\nNavHold:  {round(navHold)}"
        if displayText.replace(" ", "").replace("\n", "") != self.droneDisplay.get("1.0", customtkinter.END).replace(" ", "").replace("\n", ""):
            self.droneDisplay.configure(state="normal")
            self.droneDisplay.tag_config("center", justify="center")
            self.droneDisplay.delete(0.0, customtkinter.END)
            self.droneDisplay.insert(0.0, displayText)
            self.droneDisplay.tag_add("center", 0.0, customtkinter.END)
            self.droneDisplay.configure(state="disabled")
    #toggles the variable that tells the drone buttons to delete themselves if clicked
    def select_drone_for_removal(self):
        global removeDroneSelection, droneCount
        if droneCount == 0: 
            tkprint("no drones to remove")
            return
        removeDroneSelection = not removeDroneSelection
        if removeDroneSelection:
            self.removeDroneButton.configure(text="removing drone")
            tkprint("selected a drone to remove")
        else:
            self.removeDroneButton.configure(text="remove drone")

#prints text to the console, use this instead of print() in most cases
def tkprint(text):
    try:
        app.console.log(str(text))
    except:
        print("Failed to reach console, printing in terminal instead:\n" + str(text))

#generates a message packet for the drone index you give it
def manMsgConstruct(droneNum):
    global ip
    return ("MAN" + "|" + 
            ip + "|" + 
            str(drones[droneNum].yaw) + "|" + 
            str(drones[droneNum].pitch) + "|" + 
            str(drones[droneNum].roll) + "|" + 
            str(drones[droneNum].throttle) + "|" + 
            str(drones[droneNum].killswitch) + "|" + 
            str(drones[droneNum].armVar) + "|" + 
            str(drones[droneNum].navHold) + "|")   

#Detects the operating system and grabs the computers IP for networking between the AP and drones
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

#ignores the errors coming from the flightstick not connecting and clears the console
def bypassController(app):
    global controller
    app.console.clear()
    tkprint("Contoller bypassed, console cleared")
    app.bypassControllerButton.configure(text="Controller Bypassed")
    controller = True

#Sends the packets of instructions to the drone
def sendMessage(ipAddress, port, msg):
    global sock, throttle, app
    print("sendMessage -- IP: " + str(ipAddress) + ", PORT: " + str(port) + "\n" + str(msg) + "\n----------------------------")
    app.console.logMsg()
    bMsg = msg.encode("ascii")
    sock.sendto(bMsg, (ipAddress, int(port)))
    app.updateDroneDisplay()
    #time.sleep(0.002)

#Switches from Manual to Swarm
def MODESwarm():
    global manualYes, activeDrone, app

    if detectActiveDrone():
        app.console.error("Failsafe -- Attempted to switch modes while at drone is active")
        app.manualControlSwitch.switchInteratction(callFunctions=False)
        return

    manualYes = False
    activeDrone = -1
    buttonRefresh()

    app.toggleDisplayThrottle() #make sure it's switched off for swarm mode

    tkprint("|||  MANUAL STOPPED  |||")

#Switches from Swarm to Manual
def MODEManual():
    global manualYes, app

    if detectActiveDrone():
        app.console.error("Failsafe -- Attempted to switch modes while at drone is active")
        app.manualControlSwitch.switchInteratction(callFunctions=False)
        return

    manualYes = True
    buttonRefresh()
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

#if there are any drones that are active this will return True
def detectActiveDrone():
    global app
    for i in range(0, 8):
        if not app.droneButtons[i].state == "inactive":
            return True
    return False

#in manual mode, this updates all buttons when one is clicked
def buttonRefresh():
    global app
    for i in range(0,8):
        app.droneButtons[i].manualUpdate()

#returns the height and width of the screen in a tuple
def findScreenScale():
    root = Tk()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.destroy()
    return (height, width)

#adds the drones to the drone list
def handshake(msg, addr):
    global going
    parts = msg.split("|")
    i = int(parts[1])
    if (i == -1):
        i = len(drones)
        tkprint(i)
        tkprint(addr)
        tkprint(addr[1])
        addDrone(parts[2], addr[0], addr[1])
        tkprint("\nChecking Que")
        going = True
        for i in range(1,len(drones)):
            tkprint(f"\nConnected: {drones[i].name}")
        for adrone in drones:
            tkprint(adrone)

    else:
        if drones[i].name == parts[2]:
            #we could update here
            drones[i].ipAddress = addr[0]
            drones[i].port = addr[1]

#connects to AP
def introToAP():
    global sock
    #tell the AP that we are the base station. 
    #AP needs to save that IP address to tell it to drones (so they can connect to the base station)
    sendMessage("192.168.4.22", 80, "BaseStationIP")
    tkprint ("sent message to AP")
    tkprint("Listening for Response from AP.........")
    #listen 
    #TODO: PUT IN A RESEND EVERY FEW SECONDS
    #CODE FOR THAT INCLUDES: curr_time = round(time.time()*1000)
    startTime = time.time()
    introCount = 1
    while introCount < 3:
    #check if we need to stop--grab from q_in  
        data = b""    #the b prefix makes it byte dat
        try:
            data, addr = sock.recvfrom(1024)
            tkprint(data)
            tkprint("Decoding Data...")
            strData = data.decode("utf-8")
            tkprint("Received message %s" % data)
            
            break
        except:#crdrd
            if (time.time() - startTime >= 1.5):
                introCount += 1
                sendMessage("192.168.4.22", 80, "BaseStationIP")
                tkprint(f"sent message to AP: {introCount}")
                startTime = time.time()
            continue
        #test the input to see if it is the confirmation code
        #if it is, we can break

#connects the drones, runs once every 700ms
def checkQueue(q_in):
    global selDrone
    global going
    if (not q_in.empty() and not killThreads):
        tkprint("checking queue")
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
    if not killThreads:app.after(700, checkQueue, q_in)
    else:tkprint("checkQueue loop exited")

#returns the index in array: drones that is the first empty slot
def get_open_drone_index():
    global drones, droneCount
    for i in range(0, 8):
        if i > droneCount:
            return i
        elif not drones[i]:
            return i
    return -1

#adds a drone object to array: drones
def addDrone(name, ipAdr, port):
    global droneCount
    global app
    open_drone_index = get_open_drone_index() #returning -1 means all slots are filled

    if open_drone_index == -1:
        app.console.error(f"Max number of drones is 8, limit exceeded with drone: {name}")
        return
    
    drones[open_drone_index] = Drone(open_drone_index, name, ipAdr, port, "inactive")
    app.droneButtons[open_drone_index].changeText(drones[open_drone_index].name)
    app.droneButtons[open_drone_index].assigned = True
    app.droneButtons[open_drone_index].setColor()
    tkprint(f"Drone \"{name}\" added")
    droneCount += 1

#deletes last drone in array: drones unless an index is specified
def removeDrone(index=-1):
    global drones, droneCount, app

    if index == -1: index = droneCount - 1

    if droneCount == 0:
        tkprint("no drones to remove")
        return
    if not drones[index]:
        tkprint(f"no drone at index: {index}")
        return

    if app.droneButtons[index].state != "inactive":
        app.console.error(f"Failsafe -- Attempted to delete active drone: {app.droneButtons[index].getName()}")
        return
    
    droneCount -= 1

    tkprint(f"deleting drone {drones[index].name}")

    app.droneButtons[index].state = "inactive"
    app.droneButtons[index].changeText(app.droneButtons[index].defaultName)
    app.droneButtons[index].assigned = False
    app.droneButtons[index].setColor()

    drones[index] = None

    app.removeDroneButton.configure(text = "remove drone")

#runs a while True loop on a separate thread, recieves flighstick inputs and sends outputs
def manualControl():
    global manualYes, killswitch, throttle, yaw, roll, pitch, armVar, navHold, app, sock, killThreads, usingAppThrottle, appThrottle
    tkprint("Manual Control Thread initiated")
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
            app.console.stick_not_connected()

        if(manualYes):
            app.updateDroneDisplay()
            armVar = 1600
            if(usingAppThrottle):
                throttle = appThrottle * 10 + 1000
        else:
            armVar = 1000
            appThrottle = 0
        if(activeDrone != -1):
            sendMessage(drones[activeDrone].ipAddress, drones[activeDrone].port, "MAN" + "|" + ip + "|" + str(yaw) + "|" + str(pitch) + "|" + str(roll) + "|" + str(throttle) + "|" + str(killswitch) + "|" + str(armVar) + "|" + str(navHold) + "|")
        time.sleep(0.002)
    tkprint("Manual Control Thread terminated")

#recieves messages on a seperate thread
def listen(q_out, q_in):
    global killThreads
    tkprint("Listener Thread initiated")
    while not killThreads:
        #check if we need to stop--grab from q_in  
        data = b""    #the b prefix makes it byte data
        if (not q_in.empty()):
            qIn = q_in.get()
        try:
            data, addr = sock.recvfrom(1024)
        except:
            continue
        strData = data.decode("utf-8")
        tkprint("Received message %s" % data)
        # strData = strData + "|" + addr[0] + "|" + str(addr[1])#the message, the ip, the port
        strData = addr[0] + "*" + str(addr[1]) + "*" + strData#the ip, the port, the message
        # the message is pipe (|) delimited. The ip, port, and message are * delimited
        q_out.put(strData) #this sends the message to the main thread
    tkprint("Listener thread Terminated")

#runs everything inside of it after the app launches so we have access to the UI
def runAfterAppLaunch():
    global UDP_IP, UDP_PORT, sock, manualControlThread, qFromComms, qToComms

    getMyIP()

    qFromComms = Queue() #gets information from the comms thread
    qToComms = Queue() #sends information to the comms thread

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

    #Starting the Thread for the listener
    listenerThread = Thread(target=listen, args=(qFromComms, qToComms))
    listenerThread.start()

    app.after(1000, checkQueue, qFromComms)

#adjusting the size of the app
screenHeight, screenWidth = findScreenScale()
if(screenWidth < 1200):
    customtkinter.set_widget_scaling(0.5)
    customtkinter.set_window_scaling(0.5)
elif(screenWidth < 1500):
    customtkinter.set_widget_scaling(0.7)
    customtkinter.set_window_scaling(0.7)



app = App() #creates an instance of the UI

app.mainloop() #Program doesn't make it past this point until the UI is closed or terminated

#this only runs once the app is closed
if killThreads == False:
    print("\033[31mplease use the TERMINATE button in the future as it has safegaurds in place.\033[0m")
    killThreads = True

