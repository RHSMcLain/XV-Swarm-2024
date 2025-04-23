class Drone:
    id = -1
    name = ""
    ipAddress = ""
    port = 0
    state = "inactive"
    def __init__(self, id, name, ipAddress, port, state) -> None:
        self.id = id
        self.name = name
        self.ipAddress = ipAddress
        self.port = port
        self.state = state
    def __str__(self):
        #This provides the string that will be used in the listbox
        return self.name