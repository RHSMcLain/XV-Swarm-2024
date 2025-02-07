class Drone:
    id = -1
    name = ""
    ipAddress = ""
    port = 0
    def __init__(self, id, name, ipAddress, port) -> None:
        self.id = id
        self.name = name
        self.ipAddress = ipAddress
        self.port = port
    def __str__(self):
        #This provides the string that will be used in the listbox
        return self.name