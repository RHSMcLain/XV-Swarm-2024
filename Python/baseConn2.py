'''
 ________  ________  ________  _______   ________  ________  ________   ________     _______     
|\   __  \|\   __  \|\   ____\|\  ___ \ |\   ____\|\   __  \|\   ___  \|\   ___  \  /  ___  \    
\ \  \|\ /\ \  \|\  \ \  \___|\ \   __/|\ \  \___|\ \  \|\  \ \  \\ \  \ \  \\ \  \/__/|_/  /|   
 \ \   __  \ \   __  \ \_____  \ \  \_|/_\ \  \    \ \  \\\  \ \  \\ \  \ \  \\ \  \__|//  / /   
  \ \  \|\  \ \  \ \  \|____|\  \ \  \_|\ \ \  \____\ \  \\\  \ \  \\ \  \ \  \\ \  \  /  /_/__  
   \ \_______\ \__\ \__\____\_\  \ \_______\ \_______\ \_______\ \__\\ \__\ \__\\ \__\|\________\
    \|_______|\|__|\|__|\_________\|_______|\|_______|\|_______|\|__| \|__|\|__| \|__| \|_______|
                       \|_________|                                                                                                    

First off don't touch the networking (anything envolving socket, platform, subprocess and netifaces)
because it tends to break things. Secondly this program doesn't enjoy Mac, something about threading.

3 different threads will startup once you run this program ( see runAfterAppLaunch() ):
    - App thread
        This is the main thread that does not run from a separate Thread from the threading library
        The entire UI runs on this thread, the app in the UI ( see class App() )
            - App loop
                This is a loop that updates the app's manual variables display, and swarm display.
            - Check Queue
                This function recursively runs on the main thread, it checks incoming information about
                drone connections which it runs through handshake() to connect drones to the UI.
    - Listener thread
        This is running on a separate thread and is checking if we are receiving any information from
        the drones. Currently this is just the initial connection.
    - Manual thread
        The big boi, manual thread controls the manual control of the drones, but also everything else.
        It grabs the data coming from the flightstick and slaps those into the globals. It then every 5 
        seconds attempts to connect to the basestation wifi and the flight stick if either are disconnected.
            - Swarm Test Control
                We have a swarm test function (something like commanding the drones to go up then down) and 
                the manual control sends all swarm drones those messages if it is in that state.
        If manual mode is enabled it grabs the active drone and sends it the flight stick or in-app throttle
        data to the drone.

        
HOW TO FLY A DRONE IN MANUAL:
    1. Get yer drone and connect a battery
    2. plug in the access point (AP) and flightstick (optional) to the pc
    3. Start baseConn2.py
    4. Switch into manual mode, click Connect to AP
    5. Reset the drone arduino and wait for the drone to show up on the UI
    6. Click on the drones button in the App (turn it yellow), make sure throttle is at 1000 
    7. If it arms successfully you can now control it with the stick or throttle
after every step make sure to pray to the drone gods (optional)

If anything doesn't work try reuploading the arduino code.
Test for faulty motors in inav, and faulty arduinos in arduino IDE.
Otherwise it's a hardware issue and I wish you the best of luck.

Throttle Power:
1000: armed, lowest power
1500-1600: lifting off the ground
1700: flying
1700+: flying too fast
2000: crashing

'''


import socket, platform, subprocess
import netifaces as ni
from   threading import Thread
from   queue import Queue
import time, math, datetime, random
import customtkinter, tkinter
from   Resources.FlightStickCode.FlightStick import FlightStick
from   Resources.Statics import colorPalette
from   Resources.Drone import Drone

global manualYes # manual mode boolean
global appThrottle # value 0 - 100
global usingAppThrottle # in app throttle in use boolean
global controller, bypass_controller, bypass_wifi # controller boolean for if a flightstick is connected, bypass makes the console errors stop

global UDP_IP, UDP_PORT, ip, sock, os_name, wifi_connected, name_of_AP # ip is our ip, os_name is mac or windows
global manualControlThread
global listenerThread, lastData
global killThreads # bool, becomes True when we terminate the app
global ongoing_swarm_test_flight, ongoing_waypoint_swarm_flight, canceling_flight

global time_start, time_start2
global qFromComms, qToComms

global app, removeDroneSelection, messages_sent

global pitch, roll, yaw, throttle, navHold, armVar, killswitch # manual control variables
global activeDrone, droneCount, selectedDrone, activeDrones, maxDrones

#default manual mode variables
killswitch = 1000
throttle = 1000
navHold = 1500
armVar = 1000
pitch = 1500
roll = 1500
yaw = 1500

manualYes = False
controller = True
bypass_controller = False
bypass_wifi = False
appThrottle = 0
usingAppThrottle = False
killThreads = False
activeDrone = -1
droneCount = 0
maxDrones = 8
removeDroneSelection = False
messages_sent = 0
time_start = datetime.datetime.now()
time_start2 = datetime.datetime.now()
ongoing_swarm_test_flight = False
ongoing_waypoint_swarm_flight = False
canceling_flight = False
wifi_connected = False
accessPoint_connected = False
lastData = ''

name_of_AP = "XV_Basestation" # set this to the wifi name of your AP

UDP_IP = 0
ip = 0
drones = [None]*8 # empty drone slots are represented as None, allways an array of 8

'''
Cody Webb made this, Bjorn didn't help one bit
I helped some :(

!! DOES NOT WORK ON MAC !! 
Something about multithreading and mac not liking globals and objects being passed between them.

manual MSG: MAN IP yaw pitch roll throttle killswitch armVar navHold

#TODO:
fail safes: out of wifi range, landing drone before allowing a disable
autoland feature where drone lands itself slowly <-- this is done when AP is disconnected, but an auto land button would be good

the reason for all of the glitchiness in the console + MAN/SWM displays is they delete lines before reading them and
the deletions don't sync with the monitor refresh rate, so you get frames where the text hasn't been inserted
No easy way to solve this HA I SOLVED IT >:D

WAYPOINTS ARE JUST PRINTING WHAT THEY ARE GOING TO SEND, NOT SENDING ANYTHING!

'''

#attempts to connect to the a flightstick
def connect_flightStick(check = True):
    global controller
    if check and os_name == "mac": return
    try:
        fs.__init__(fs)
        if check: tkprint("flightstick connected")
        controller = True
    except:
        controller = False
        pass

def get_os_name():
    if platform.system() == ("Darwin"): return "mac"
    if platform.system() == ("Windows"): return "windows"
    print("unsupported OS")

os_name = get_os_name()

#sets up the flighstick, on mac we cant periodically try to connect to the flightstick.
fs = FlightStick
if os_name == "mac":
    connect_flightStick(check=False)
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
        self.textbox.insert(1.0, " "*17 +"- - - - - - - CONSOLE - - - - - - -")

        self.disable()
    
    def log(self, text):
        global messages_sent
        messages_sent = 0
        self.enable()
        self.textbox.insert(2.0, f"\n{text}")
        self.disable()
    def error(self, text):
        global messages_sent
        messages_sent = 0
        self.enable()
        self.textbox.insert(2.0, f"\n{text}")
        self.textbox.tag_add("red", 3.0, 4.0)
        self.disable()
    def check_sent_messages(self):
        global messages_sent
        self.enable()
        if messages_sent > 1 and "message count: " in self.textbox.get(3.0, 4.0):
            self.textbox.delete(3.15, f"3.{messages_sent + 15}")
            self.textbox.insert(3.15, f"{messages_sent}")
        else:
            self.textbox.insert(2.0, f"\nmessage count: {messages_sent}")
        self.config["master"].updateManualDisplay()
        self.disable()
    def stick_not_connected(self):
        self.error('- - !!! NO FLIGHTSTICK CONNECTED !!! - -')
    def killswitch(self):
        self.error('========================KILL SWITCH ACTIVATED========================')
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
        app.console.textbox.insert(0.0, " "*17 +"- - - - - - - CONSOLE - - - - - - -")
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
        global removeDroneSelection, drones, ongoing_swarm_test_flight, app

        if ongoing_swarm_test_flight:
            app.console.error("Failsafe: ONGOING SWARM FLIGHT, BUTTONS DISABLED")
            return

        if removeDroneSelection and self.assigned: #remove self if we are selected to delete drone
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
        
        if self.assigned: drones[self.droneId].state = self.state

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
        self.geometry(f"{1600}x{800}")
        self.configure(fg_color=colorPalette.backgroundDark)

        self.attemptingTerminate = False
        self.displaying_swarm_variables = False
        self.swarm_drone_displays = []

        #killswitch, connect to ap, add test drone, bypass controller, Manual UDP Console and Send USP Message, Mode and Stage Control
        #textbox with Throttle, Pitch, Yaw, Roll, ArmVar, and Navhold

        self.console = tkConsole(self) #Initiate Main Console

        self.leftButtonBar = customtkinter.CTkFrame(self, width=140, corner_radius=0, fg_color=self.cget("fg_color")) #Holds left buttons (killswitch, connect to ap, text drone, bypass controller, and mode switch)
        
        self.droneDisplay = customtkinter.CTkTextbox(self, activate_scrollbars=False, font=("Monaco", 20), text_color="black", width=320, spacing3=17, spacing1=19, fg_color=colorPalette.droneDisplay) #Orange bar left of console that displays drone throttle, pitch, yaw, etc.

        #Buttons in left button bar
        self.killswitchbutton =       Button(self.leftButtonBar, text="Kill Drones",       command=lambda:self.killswitch(), fg_color=colorPalette.buttonRed, hover_color=colorPalette.buttonRedHover)
        self.connectToAPButton =      Button(self.leftButtonBar, text="Connect To AP",     command=lambda:introToAP(0))
        self.manualControlSwitch =  tkSwitch(self.leftButtonBar, MODEManual, MODESwarm, leftText="Manual", rightText="Swarm") #switch for Manual and Swarm modes in left button bar
        self.sendWaypointsButton =    Button(self.leftButtonBar, text="Send Waypoints",    command=initiate_waypoints)

        self.throttleBar = customtkinter.CTkFrame(self) #Holds all components of the in-display throttle system left of the drone display (far right)
        #These are the components in the throttle bar
        self.throttleDisplay = customtkinter.CTkTextbox     (self.throttleBar, height=124, font=("Arial", 18))
        self.throttleSlider = customtkinter.CTkSlider       (self.throttleBar, orientation="vertical", height=200, from_=0, to=100, command=lambda a: self.updateThrottleDisplay(a, self)) #Dont touch the aurguments
        self.displayThrottleSwitch = customtkinter.CTkSwitch(self.throttleBar, text="Enable Display Throttle", command=lambda: self.toggleDisplayThrottle())

        #Holds remove drones button and terminate button
        self.lowerLeftButtonBar = customtkinter.CTkFrame(self, fg_color=self.cget("fg_color"))

        #removes right most drone in drone array
        self.removeDroneButton = Button(self.lowerLeftButtonBar, text="remove drone", command=self.select_drone_for_removal)

        #quit button
        self.quitButton = Button(self.lowerLeftButtonBar, text="TERMINATE", command=lambda: self.attemptTerminateApp(), fg_color=colorPalette.buttonRed, hover_color=colorPalette.buttonRedHover)

        self.activeDroneBar = customtkinter.CTkFrame(self, width=600)
        self.droneButtons = [None]*8
        self.activeDroneBar.grid (row=1, column=1)
        for i in range(0, 8): #creates 8 drone buttons in a 4x2 array
            self.droneButtons[i] = droneActiveButton(self.activeDroneBar, i)
            colMinus = 0
            if i > 3: colMinus = 4
            self.droneButtons[i].grid(row=round(i/8+0.1), column=i-colMinus, padx=15, pady=15)

        self.swarmBar = customtkinter.CTkFrame(self)
        self.swarmTestButton =             Button(self.swarmBar, text="Swarm Test",      fg_color="#28663c", hover_color="#1a4227", command=swarmTest3)
        self.stopSwarmTestButton =         Button(self.swarmBar, text="Stop Swarm",      fg_color="#28663c", hover_color="#1a4227", command=cancel_swarm_flight)
        self.displaySwarmVariablesButton = Button(self.swarmBar, text="Swarm Variables", fg_color="#28663c", hover_color="#1a4227", command=self.display_swarm_variables_popup)
        self.putNextButtonHere =           Button(self.swarmBar, text="",                fg_color="#28663c", hover_color="#1a4227")

        self.my_label = customtkinter.CTkLabel(self, text="", height= 70, width = 210)

        #test buttons
        self.testingButtonBar = customtkinter.CTkFrame(self)

        self.bypassControllerButton = Button(self.testingButtonBar, text="Bypass Controller", command=self.bypassController)
        self.bypassWifiButton =       Button(self.testingButtonBar, text="Bypass Wifi",       command=self.bypass_wifi)
        self.addTestDroneButton =     Button(self.testingButtonBar, text="Add Test Drone",    command=lambda:addDrone("Test Drone #" + str(random.randint(100, 1000)), "10.20.18.23", 85))
        self.navHoldToggleButton =    Button(self.testingButtonBar, text="Toggle NavHold",    command=self.toggleNavHold)

        # Aligning all parts of the UI

        self.my_label.grid(row=1, column=0, padx=0, pady=0, sticky="new")

        self.swarmBar.grid                   (row=1, column=2, sticky="nsw")
        self.swarmTestButton.grid            (row=0, column=0)
        self.stopSwarmTestButton.grid        (row=1, column=0)
        self.displaySwarmVariablesButton.grid(row=2, column=0)
        self.putNextButtonHere.grid          (row=3, column=0)

        self.testingButtonBar.grid           (row=1, column=3, padx=10, rowspan=4)
        self.bypassControllerButton.grid     (row=0, column=0)
        self.bypassWifiButton.grid           (row=1, column=0)
        self.addTestDroneButton.grid         (row=2, column=0)
        self.navHoldToggleButton.grid        (row=3, column=0)

        self.leftButtonBar.grid(row=0, column=0, pady=(10, 0), rowspan=4, sticky="nsew") #far left frame
        self.leftButtonBar.grid_rowconfigure(5, weight=1)

        self.killswitchbutton.grid      (row=0, column=0)
        self.connectToAPButton.grid     (row=1, column=0)
        self.sendWaypointsButton.grid   (row=3, column=0)

        self.manualControlSwitch.grid(row=4, column=0)
        self.console.grid            (row=0, column=1, padx=10, pady=10)
        self.droneDisplay.grid       (row=0, column=2, pady=10, sticky="ns")

        self.throttleBar.grid          (row=0, column=3, padx=10, pady=10, rowspan=2, sticky="nw") #far right frame
        self.throttleSlider.grid       (row=1, column=0, pady=15)
        self.throttleDisplay.grid      (row=0, column=0)
        self.displayThrottleSwitch.grid(row=2, column=0, pady=(20, 0))

        self.lowerLeftButtonBar.grid(row=1, column=0)
        self.removeDroneButton.grid (row=0, column=0)
        self.quitButton.grid        (row=1, column=0)      

        #Placing text in the textboxes on bootup
        self.droneDisplay.tag_config("center", justify="center")
        self.droneDisplay.insert(1.0, f"Yaw:      {1500}\nPitch:    {1500}\nRoll:     {1500}\nThrottle: {1000}\nArmVar:   {1500}\nNavHold:  {1000}")
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
        global ongoing_swarm_test_flight
        
        if self.attemptingTerminate:
            tkprint("allready attempting to terminate")
            return
        if ongoing_swarm_test_flight:
            self.console.error("Failsafe: ONGOING SWARM FLIGHT")
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

        def on_closing():
            self.attemptingTerminate = False
            popup.destroy()  # Destroy the popup window
        
        popup.protocol("WM_DELETE_WINDOW", on_closing)

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
    #kills the popup terminate window
    def destroyPopup(self, popup):
        self.attemptingTerminate = False
        popup.destroy()

    def display_swarm_variables_popup(self):
        global drones
        
        if self.displaying_swarm_variables:
            tkprint("allready displaying swarm drone variables")
            return

        swarm_variables_popup = customtkinter.CTkToplevel(fg_color="grey")
        swarm_variables_popup.title("Swarm Drone Variables")
        swarm_variables_popup.attributes("-topmost", True)

        def on_closing():
            self.displaying_swarm_variables = False
            swarm_variables_popup.destroy()  # Destroy the popup window
        
        swarm_variables_popup.protocol("WM_DELETE_WINDOW", on_closing)

        self.swarm_drone_displays = [None]*8

        for i in range(0, 8): #creates 8 drone buttons in a 4x2 array
            self.swarm_drone_displays[i] = customtkinter.CTkTextbox(swarm_variables_popup, width=170, height=170, corner_radius=10, font=("Monaco", 12), border_color="black", border_width=5)
            colMinus = 0
            if i > 3: colMinus = 4
            self.swarm_drone_displays[i].grid(row=round(i/8+0.1), column=i-colMinus, padx=15, pady=15)
            self.swarm_drone_displays[i].tag_config("center", justify="center")

            if drones[i]:
                self.swarm_drone_displays[i].insert(1.0 , f"{drones[i].name}\nNo messages sent")
            else:
                self.swarm_drone_displays[i].insert(1.0 ,"Not Connected")

            
            self.swarm_drone_displays[i].tag_add("center", 1.0, customtkinter.END)
            self.swarm_drone_displays[i].configure(state="disabled")

        self.displaying_swarm_variables = True
    
    def update_swarm_varibles_display(self):
        global drones, manualYes, killswitch

        if not self.displaying_swarm_variables: return

        text = ""
        i = -1
        for display in self.swarm_drone_displays:
            i+=1

            text = "Not Connected"
            drone_selector = drones[i]

            if drone_selector:
                if killswitch >= 1700:
                    text = f"{drone_selector.name}\n- DRONE KILLED -"
                elif drone_selector.state != "inactive":
                    text = f"{drone_selector.name}\nIP: {drone_selector.ipAddress}\nPORT:     {drone_selector.port}\nYaw:      {drone_selector.yaw}\nPitch:    {drone_selector.pitch}\nRoll:     {drone_selector.roll}\nThrottle: {drone_selector.throttle}\nArmVar:   {drone_selector.armVar}\nNavHold:  {drone_selector.navHold}"
            
            try: # throws an error if you close the window while this is running
                if text.replace("\n", "") != display.get(1.0, customtkinter.END).replace("\n", ""):
                    display.configure(state="normal")
                    display.tag_config("center", justify="center")
                    display.delete(1.0, customtkinter.END)
                    display.insert(1.0 , text)
                    display.tag_add("center", 1.0, customtkinter.END)
                    display.configure(state="disabled")
            except:pass
    #ignores the errors coming from the wifi connecting, and wrong wifi
    def bypass_wifi(self):
        global bypass_wifi
        tkprint("Wifi Bypassed")
        self.bypassWifiButton.configure(text="Wifi Bypassed", fg_color=colorPalette.buttonBlueHover)
        bypass_wifi = True
    
    #ignores the errors coming from the flightstick not connecting
    def bypassController(self):
        global controller, bypass_controller
        tkprint("Contoller bypassed")
        self.bypassControllerButton.configure(text="Controller Bypassed", fg_color=colorPalette.buttonBlueHover)
        controller = True
        bypass_controller = True

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
            if not runFunction: tkprint("app throttle only available in manual mode")
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
    #sets manual killswitch to 1700 and sends kill msg to all swarm drones
    def killswitch(self):
        global killswitch
        killswitch = 1700 # manual killswitch variable, 1700 is kill
        kill_all_swarm_drones() # sets all drones killswitch to 1700
        self.console.killswitch() # console prints that drones have been killed
        self.killswitchbutton.configure(text="Drones Killed", fg_color=colorPalette.buttonRedHover, hover_color=colorPalette.buttonRedHover)
    #grabs the manual mode variables and displays them in the orange display
    def updateManualDisplay(self):
        global throttle, roll, yaw, pitch, armVar, navHold
        self.droneDisplay.configure(state="normal")
        
        l = [yaw, pitch, roll, throttle, armVar, navHold]

        for i in range(0, 6):
            self.droneDisplay.delete(f"{i+1}.10", f"{i+1}.14")
            self.droneDisplay.insert(f"{i+1}.10", l[i])

        self.droneDisplay.configure(state="disabled")
    #toggles the variable that tells the drone buttons to delete themselves if clicked
    def select_drone_for_removal(self):
        global removeDroneSelection, droneCount, ongoing_swarm_test_flight
        if ongoing_swarm_test_flight:
            self.console.error("Drone buttons disabled during swarm flight")
            return
        if droneCount == 0: 
            tkprint("no drones to remove")
            return
        removeDroneSelection = not removeDroneSelection
        if removeDroneSelection:
            self.removeDroneButton.configure(text="removing drone")
            tkprint("selected a drone to remove")
        else:
            self.removeDroneButton.configure(text="remove drone")
    
    def toggleNavHold(a):
        global navHold
        if navHold == 1600:
            navHold = 1500
        else: navHold = 1600

#prints text to the console, use this instead of print() in most cases
def tkprint(text):
    try:    app.console.log(str(text))
    except: print(f"Failed to reach console, printing in terminal instead:\n{text}\n")

#generates a message packet for the drone index you give it
def manMsgConstruct(droneNum):
    global ip
    return ("MAN|" + 
            ip + "|" + 
            str(clamp(round(drones[droneNum].yaw))) + "|" + 
            str(clamp(round(drones[droneNum].roll))) + "|" + 
            str(clamp(round(drones[droneNum].pitch))) + "|" + 
            str(clamp(round(drones[droneNum].throttle))) + "|" + 
            str(clamp(round(drones[droneNum].killswitch))) + "|" + 
            str(clamp(round(drones[droneNum].armVar))) + "|" + 
            str(clamp(round(drones[droneNum].navHold))) + "|")  
    
#generates a message packet 
def swmMsgConstruct(droneNum):
    global ip
    length = len(drones[droneNum].waypointArr)
    store = None
    for i in range(1, length+1):
        if(i != length):
            store + (drones[droneNum].waypointArr[i].message +"|" +"loop" +"|")
        else:
            store + (drones[droneNum].waypointArr[i].message +"|" +"end" +"|")
    return "SWM|" +ip +"|" +drones[droneNum].state +"|" +length +"|" +store

def active_drone_count(i=0):
    global drones
    for drone in drones: 
        if drone: i += 1
    return i

#2 points lat long, search between, how many drones, what drone it is, alt of search

def waypointConstruct(id, num, lat1, long1, lat2, long2, alt):
    global drones, app, ip

    if not drones[id]: 
        app.console.error("!!! ERROR: WAYPOINT CONSTSRUCT ID DOESNT EXIST !!!")
        return

    swarm_count = active_drone_count()

    return f"WAY|{ip}|{num}|{lat1}|{long1}|{lat2}|{long2}|{swarm_count}|{alt}|"

def initiate_waypoints():
    global drones, app, droneCount

    if not detectActiveDrone() or droneCount == 0:
        app.console.error("No drones to send waypoints")
        return

    tkprint("sending waypoints")

    lat1  = 1.11
    long1 = 2.22
    lat2  = 3.33
    long2 = 4.44

    alt   = 20

    i = 0
    for drone in drones:
        if drone:
            if drone.state == "active":
                i += 1
                construct = waypointConstruct(drone.id, i, lat1, long1, lat2, long2, alt)
                for k in range(0, 3):
                    print(construct) #send msg here

#Detects the operating system and grabs the computers IP for networking between the AP and drones
def getMyIP():
    global app, ip, UDP_IP, UDP_PORT, os_name, wifi_connected, name_of_AP
    try:
        hostname = socket.gethostname()
        if os_name == "windows": # IP ADDRESS FOR WINDOWS OS
            #tkprint("Operating system is WINDOWS")
            ip = socket.gethostbyname(hostname + ".local")
        if os_name == "mac": # IP ADRESSS FOR MAC OS
            #tkprint("Operating system is MACOS")
            ip = ni.ifaddresses('en1')[ni.AF_INET][0]['addr']
        UDP_PORT = 5005
        UDP_IP = ip
        tkprint(f"host name: {hostname} || ip: {ip}")

        wifi_name = get_wifi_info()["SSID"]

        tkprint(f"Wifi name: {wifi_name}")

        if wifi_name != name_of_AP:
            app.console.error(f"Connected to wrong wifi, connect to {name_of_AP} wifi")
        else:
            wifi_connected = True
        
        return

    except socket.gaierror as e: app.console.error(f"There was an error resolving the hostname: {e}")
    except Exception as e:       app.console.error(f"An unexpected error occurred: {e}")
    app.console.error("Unabled to connect to wifi.")

# gets info including SSID, returns an object. use get_wifi_info()["SSID"]
def get_wifi_info():
    global os_name
    if os_name == "mac":
        process = subprocess.Popen(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport','-I'], stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(['netsh', 'wlan', 'show', 'interfaces'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    out, err = process.communicate()
    process.wait()
    wifi_info = {}
    for line in out.decode('utf-8', errors='ignore').split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().replace(' ', '')
            val = parts[1].strip()
            wifi_info[key] = val

    return wifi_info

#Sends the packets of instructions to the drone
def sendMessage(ipAddress, port, msg):
    global sock, throttle, app, messages_sent, canceling_flight
    if canceling_flight:
        print("canceling swarm flight")
    else:
        print(f"sendMessage -- IP: {ipAddress}, PORT: {port}\n{msg}\n=====================")
        messages_sent += 1
        if(messages_sent % 10 == 0):
            try: app.console.check_sent_messages()
            except: pass
        bMsg = msg.encode("ascii")
        sock.sendto(bMsg, (ipAddress, int(port)))

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

# #all drones throttle to 1200 and back down. 6 seconds total
# def swarmTest():
#     global app
#     tkprint("swarm test started!")
#     arm_all_swarm_drones()
#     app.after(1000, send_to_swarm, 1500, 1500, 1500, 1200, 1000)
#     app.after(5000, send_to_swarm, 1500, 1500, 1500, 1000, 1000)
#     app.after(6000, disarm_all_swarm_drones)

# # all drones arm, gradually increase throttle to 1600 and back down, disarm. 10 seconds total
# def swarmTest2(start_time=0, r=True):
#     global app

#     if not detectActiveDrone():
#         tkprint("no active drones to test swarm")
#         return

#     if r: 
#         tkprint(f"swarm test 2 started")
#         start_time = time.time()
#         arm_all_swarm_drones()
#     current_seconds = time.time() - start_time

#     throttle_curve = 1000

#     if current_seconds >= 1 and current_seconds <= 5:
#         throttle_curve = map_range(current_seconds, 1, 5, 1000, 1500)
#     elif current_seconds >=5 and current_seconds <=6:
#         throttle_curve = 1500
#     elif current_seconds >=6 and current_seconds <=9:
#         throttle_curve = 1500 - map_range(current_seconds, 6, 9, 0, 500)
    
#     #tkprint(f"{round(current_seconds, 4)}, {throttle_curve}")
#     throttle_curve = clamp(round(sigmoid_smooth(throttle_curve, 1000, 1500, 1.2)))
#     send_to_swarm(1500, 1500, 1500, throttle_curve, 1000)

#     if current_seconds >= 9:
#         send_to_swarm(1500, 1500, 1500, 1000, 1000)
#         disarm_all_swarm_drones()

#     if current_seconds < 10:
#         app.after(10, swarmTest2, start_time, False)
#     else:
#         tkprint("swarm test 2 ended")

# slowly increases throttle to 1550, stays there to 1 second, then goes to 1400 for 5 seconds and disarms at 11s
def swarmTest3(start_time=0, r=True):
    global app, ongoing_swarm_test_flight, canceling_flight

    if canceling_flight: return

    if not detectActiveDrone():
        tkprint("no active drones to test swarm")
        return
    
    if r and ongoing_swarm_test_flight:
        app.console.error("Failsafe: ALLREADY AN ONGOING SWARM FIGHT")
        return
    else: ongoing_swarm_test_flight = True

    # first itteration arm all drones (0s)
    if r: 
        tkprint(f"swarm test 3 started")
        start_time = time.time()
        arm_all_swarm_drones()
    current_seconds = time.time() - start_time

    if current_seconds < 1:
        send_to_swarm(1500, 1500, 1500, 1000, 1000)
    # from 1s to 5s increase throttle slowly from 1000 to 1550, taking off
    elif current_seconds >= 1 and current_seconds <=3:
        send_to_swarm(1500, 1500, 1500, round(map_range(current_seconds, 1, 5, 1000, 1575)), 1000)
    
    # from 5s to 6s throttle set to 1550, in the air
    elif current_seconds <= 6:
        send_to_swarm(1500, 1500, 1500, 1550, 1000)

    # from 6s to 11s set throttle to 1400, drifting down and landing
    elif current_seconds <= 15:
        send_to_swarm(1500, 1500, 1500, 1500, 1000)

    # at 11s disarms drones
    elif current_seconds <= 18:
        send_to_swarm(1500, 1500, 1500, 1000, 1000)
        disarm_all_swarm_drones()

    # swarm test ends at 13s
    if current_seconds < 13:
        app.after(10, swarmTest3, start_time, False)
    else:
        tkprint("swarm test 2 ended")
        ongoing_swarm_test_flight = False

# send it 1450 throttle then disconnects AP
def cancel_swarm_flight():
    global canceling_flight
    tkprint("!!! CANCELING SWARM FLIGHT !!!")    
    canceling_flight = True

    send_to_swarm(1500, 1500, 1500, 1450, 1000)

# sets all active swarm drones variables to the ones provided
def send_to_swarm(yaw, pitch, roll, throttle, killswitch):
    global drones
    for drone in drones:
        if drone:
            if drone.state != "inactive" and drone.killswitch < 1700 and drone.armVar >= 1575:
                drone.yaw = yaw
                drone.pitch = pitch
                drone.roll = roll
                drone.throttle = throttle
                drone.killswitch = killswitch
                #tkprint(f"sent swarm message to drone: {drone.name}")
# I wonder what this does
def arm_all_swarm_drones():
    for drone in drones:
        if drone:
            if drone.state != "inactive" and drone.armVar <= 1575:
                drone.throttle = 1000
                drone.armVar = 1600
                tkprint(f"armed swarm drone: {drone.name}")
# does this need explaining?
def disarm_all_swarm_drones():
    for drone in drones:
        if drone:
            if drone.state != "inactive" and drone.armVar >= 1575:
                drone.armVar = 1500
                tkprint(f"disarmed swarm drone: {drone.name}")
# to complicated for you to understand
def kill_all_swarm_drones():
    send_to_swarm(1500, 1500, 1500, 1000, 1700)


#This function is used to ensure that values for control inputs are kept in acceptable values
def clamp(val):
    lowLimit = 1000
    highLimit = 2000
    if val < lowLimit:
        val = lowLimit
    if val > highLimit:
        val = highLimit   
    return val

#intensity of 5 is strong, 1 is moderate, 0.1 is nearly linear
def sigmoid_smooth(x, min_val, max_val, intensity):
    # Clamp x to [min_val, max_val]
    x = max(min(x, max_val), min_val)

    # Normalize x to [0, 1]
    normalized = (x - min_val) / (max_val - min_val)

    # Apply sigmoid transformation
    # The intensity affects the steepness of the sigmoid
    # Higher intensity makes the curve steeper
    steepness = intensity * 10  # adjust this multiplier as needed
    sigmoid = 1 / (1 + math.exp(-steepness * (normalized - 0.5)))

    # Map back to [min_val, max_val]
    smoothed = min_val + sigmoid * (max_val - min_val)
    return smoothed

#maps the number between from_min and from_max onto the range between to_min and to_max, all inclusive
def map_range(value, from_min, from_max, to_min, to_max):
    # Clamp input value within the original range
    if from_max == from_min:
        raise ValueError("Original range cannot be zero.")
    
    # Calculate the scaled value
    scaled = (value - from_min) / (from_max - from_min)
    return to_min + (scaled * (to_max - to_min))

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
    root = tkinter.Tk()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.destroy()
    return (height, width)

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
    global droneCount, app, drones, killswitch

    if killswitch >= 1700:
        app.console.error("KILLSWITCH is active, failed to add drone!")
        return

    open_drone_index = get_open_drone_index() #returning -1 means all slots are filled

    if open_drone_index == -1:
        app.console.error(f"Max number of drones is 8, limit exceeded with drone: {name}")
        return
    
    for drone in drones:
        if drone:
            if drone.name == name:
                tkprint("duplicate drones detected")
                break
    
    drones[open_drone_index] = Drone(open_drone_index, name, ipAdr, port, "inactive")
    app.droneButtons[open_drone_index].changeText(drones[open_drone_index].name) # get the drones assigned button to the drones name
    app.droneButtons[open_drone_index].assigned = True # make the button know it has a drone
    app.droneButtons[open_drone_index].setColor() # setting the color red
    tkprint(f"Drone \"{name}\" added")
    droneCount += 1

#deletes last drone in array: drones, unless an index is specified
def removeDrone(index=-1):
    global drones, droneCount, app, removeDroneSelection

    if index == -1: index = droneCount - 1

    if droneCount == 0:
        tkprint("no drones to remove")
        return
    
    if not drones[index]:
        tkprint(f"no drone at index: {index}")
        return

    if app.droneButtons[index].state != "inactive":
        app.console.error(f"Failsafe -- Attempted to delete active drone: {app.droneButtons[index].getName()}")
        removeDroneSelection = False
        app.removeDroneButton.configure(text = "remove drone")
        return
    
    droneCount -= 1

    tkprint(f"deleting drone {drones[index].name}")

    # button assigned to the drone is disassigned and made inactive
    app.droneButtons[index].state = "inactive"
    app.droneButtons[index].changeText(app.droneButtons[index].defaultName)
    app.droneButtons[index].assigned = False
    app.droneButtons[index].setColor()

    drones[index] = None

    app.removeDroneButton.configure(text = "remove drone")

#adds the drones to the drone list
def handshake(msg, addr):
    parts = msg.split("|")
    i = int(parts[1])
    if (i == -1):
        i = len(drones)
        tkprint(f"i: {i}, addr: {addr}, addr[1]: {addr[1]}")
        addDrone(parts[2], addr[0], addr[1])
        for adrone in drones:
            if adrone:tkprint(adrone)
    else:
        if drones[i].name == parts[2]:
            #we could update here
            drones[i].ipAddress = addr[0]
            drones[i].port = addr[1]

#new function uses recursion instead of an unleashed while True loop
#Connects to AP, sends up to 3 messages with a 1.5 second delay
def introToAP(introCount):
    global app, lastData, accessPoint_connected

    if accessPoint_connected:
        tkprint("Connected to AP!")
        return

    sendMessage("192.168.4.22", 80, "BaseStationIP")
    introCount += 1

    tkprint(f"sent message to AP (msg #{introCount})")
    if introCount == 3: tkprint("unable to connect to AP, try resetting it")
    else: app.after(1500, introToAP, introCount)

#connects the drones, runs once every 700ms, sometimes gets stuck when closing the app without using the terminate button
def checkQueue(q_in):
    global killThreads, app
    if (not q_in.empty() and not killThreads):
        tkprint("checking q_in")
        #grab the item
        #process the info
        #mark it complete
        data = q_in.get()
        parts = data.split("*")
        addr = parts[0]
        port = int(parts[1])
        msg = parts[2]
        msgParts = msg.split("|")

        cmd = msgParts[0]

        if cmd == "HND":
            handshake(msg, (addr, port))
    if not killThreads: app.after(700, checkQueue, q_in)
    else: tkprint("checkQueue loop exited")

def appLoop():
    global app, killThreads
    app.update_swarm_varibles_display()
    app.updateManualDisplay()
    if not killThreads: app.after(50, appLoop)
    else: tkprint("appLoop exited")

#runs a while True loop on a separate thread, recieves flighstick inputs and sends outputs. Funny enough it also calls swarm control, so this more like a main loop.
def manualControl():
    global manualYes, killswitch, throttle, yaw, roll, pitch, armVar, navHold, app
    global sock, killThreads, usingAppThrottle, appThrottle, time_start, time_start2, bypass_controller, controller
    global sock, wifi_connected, name_of_AP, UDP_IP, UDP_PORT, bypass_wifi
    tkprint("Manual Control Thread initiated")
    while not killThreads: #continously loop until killThreads is true

        if not usingAppThrottle: # if we are not using the in-app throttle
            if controller and killswitch < 1700: # if the controller is connected, read the outputs and load the manual global variables
                try:
                    fs.readFlightStick(fs)
                    yaw = clamp(round(fs.yaw)) - 4 # fucking scuffed
                    roll = clamp(round(fs.roll))
                    pitch = clamp(round(fs.pitch))
                    throttle = clamp(round(fs.throttle))
                except: # if it returns an error we know the controller is no longer connected
                   controller = False
            # if the controller is not connected, periodically try to connected to it (windows only), and connect to wifi
            if((datetime.datetime.now() - time_start) > datetime.timedelta(seconds=5)):

                if get_wifi_info()["SSID"] != name_of_AP:
                    wifi_connected = False

                if not wifi_connected and not bypass_wifi:
                    getMyIP()
                    
                    setup_sock()
                    
                if not controller:
                    if not bypass_controller: app.console.stick_not_connected()
                    connect_flightStick()
                time_start = datetime.datetime.now()
            if((datetime.datetime.now() - time_start2) > datetime.timedelta(seconds=1)):
                time_start2 = datetime.datetime.now()
        elif killswitch < 1700:
                throttle = appThrottle * 10 + 1000

        if not manualYes:
            appThrottle = 0
            if killswitch < 1700 and ongoing_swarm_test_flight: swarmControlTest() # <-- if manualYes is false it calls swarm control
        
        one_drone_armed = False
        for i in range(0, 8):
            if drones[i]:
                try: #deleting a drone in manual mode will sometimes throw an error which is caught be this, because it looks up a nonexistant drone obj
                    if i == activeDrone:
                        armVar = 1600
                        drones[activeDrone].throttle = throttle
                        drones[activeDrone].pitch = pitch
                        drones[activeDrone].roll = roll
                        drones[activeDrone].yaw = yaw
                        drones[activeDrone].navHold = navHold
                        drones[activeDrone].killswitch = killswitch
                        drones[activeDrone].armVar = armVar
                        sendMessage(drones[activeDrone].ipAddress, drones[activeDrone].port, manMsgConstruct(activeDrone))
                        one_drone_armed = True
                    elif manualYes:
                        drones[i].throttle = 1000
                        drones[i].pitch = 1500
                        drones[i].roll = 1500
                        drones[i].yaw = 1500
                        drones[i].navHold = navHold
                        drones[i].killswitch = killswitch
                        drones[i].armVar = 1500
                        sendMessage(drones[i].ipAddress, drones[i].port, manMsgConstruct(i))
                except:pass
        if not one_drone_armed:
            armVar = 1500

        time.sleep(0.000001)
    tkprint("Manual Control Thread terminated")

def setup_sock():
    global app, sock, UDP_PORT, UDP_IP
    try: sock.close()
    except: pass

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.setblocking(0)
        sock.bind((UDP_IP, UDP_PORT))
    except: app.console.error(f"Can't assign UDP_IP {UDP_IP} and UDP_PORT {UDP_PORT}")

    if UDP_IP == 0:
        app.console.IP_is_zero() #send error
    if UDP_PORT == 0:
        app.console.port_is_zero() #send error
    #tkprint("UDP IP is " + str(UDP_IP))

# runs continuously when manualYes is false
def swarmControlTest():
    global drones
    for drone in drones:
        if drone and drone.state == "active":
            sendMessage(drone.ipAddress, drone.port, manMsgConstruct(drone.id))
    
def search_control(lat1, long1, lat2, long2, alt):
    droneNum = 1
    global drones
    for drone in drones:
        if drone and drone.state == "active":
            waypointConstruct(drone.id, droneNum, lat1, long1, lat2, long2, alt)
            droneNum += 1
            tkprint("waypoint sent to {drone.name}")

#recieves messages on a seperate thread, don't fuck with this, i've tried
def listen(q_out, q_in):
    global killThreads, lastData, accessPoint_connected
    tkprint("Listener Thread initiated")
    while not killThreads:
        time.sleep(0.00002) # lags spikes can happen if Threads are running while True loops, a delay seems to fix this
        #check if we need to stop--grab from q_in  
        data = b""    #the b prefix makes it byte data
        if (not q_in.empty()):
            qIn = q_in.get()
        try:
            data, addr = sock.recvfrom(1024)
        except:
            pass

        try: strData = data.decode("utf-8")
        except Exception as e:
            tkprint(f"I failed to decode data! {strData}")
        
    
        try:
            if data == b"" or not wifi_connected: continue

            tkprint("Received message %s" % data)
            if data == b'reply': accessPoint_connected = True
            if wifi_connected:
                lastData = data
            else:
                lastData = b""

            # strData = strData + "|" + addr[0] + "|" + str(addr[1])#the message, the ip, the port
            strData = addr[0] + "*" + str(addr[1]) + "*" + strData#the ip, the port, the message
            # the message is pipe (|) delimited. The ip, port, and message are * delimited
            q_out.put(strData) #this sends the message to the main thread
        except: pass

    tkprint("Listener thread Terminated")

#runs everything inside of it after the app launches so we have access to the UI
def runAfterAppLaunch():
    global UDP_IP, UDP_PORT, sock, manualControlThread, qFromComms, qToComms

    getMyIP()
    #connect_flightStick()

    qFromComms = Queue() #gets information from the comms thread
    qToComms = Queue() #sends information to the comms thread

    setup_sock()

    #Starting the Thread for manual control
    manualControlThread = Thread(target=manualControl, args=())
    manualControlThread.start()

    #Starting the Thread for the listener
    listenerThread = Thread(target=listen, args=(qFromComms, qToComms))
    listenerThread.start()

    app.after(1000, appLoop)
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