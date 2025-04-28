class Drone:
    id = -1
    name = ""
    ipAddress = ""
    port = 0
    state = "inactive"
    yaw = 1500
    pitch = 1500
    roll = 1500
    throttle = 1000
    killswitch = 1000
    armVar = 1000
    navHold = 1000
    def __init__(self, id, name, ipAddress, port, state) -> None:
        self.id = id
        self.name = name
        self.ipAddress = ipAddress
        self.port = port
        self.state = state
    def __str__(self):
        #This provides the string that will be used in the listbox
        return self.name