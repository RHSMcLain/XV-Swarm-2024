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
    waypointArr = [None]
    def __init__(self, id, name, ipAddress, port, state) -> None:
        self.id = id
        self.name = name
        self.ipAddress = ipAddress
        self.port = port
        self.state = state
        self.waypointArr
    def __str__(self):
        #This provides the string that will be used in the listbox
        return self.name
    def waypointAdd(self, targetLat, targetLon, targetAlt, waitTime): #pushes a new waypoint onto the list
        self.waypointArr.append(Track(targetLat, targetLon, targetAlt, waitTime, len(self.waypointArr)))
    def waypointRemove(self, waypointID): #deletes the waypoint from the list
        del self.waypointArr[waypointID]
    def waypointReplace(self, targetLat, targetLon, targetAlt, waitTime, waypointID): #replaces the waypoint
        self.waypointArr[waypointID] = Track(targetLat, targetLon, targetAlt, waitTime, waypointID)
    def waypointClear(self): #deletes all waypoints and replaces id 0 with none
        for i in range(0,len(self.waypointArr)):
            if i == 0:
                self.waypointArr[0] = None
            else:
                del self.waypointArr[i]
class Track:
    id = None
    gpsLon = None
    gpsLat = None
    alt = None
    heading = None
    time = None
    def __init__(self, gpsLon, gpsLat, alt, heading, time, id) -> None:
        self.gpsLon = gpsLon
        self.gpsLat = gpsLat
        self.alt = alt
        self.time = time
        self.heading = heading
        self.id = id
    def message(self):
        return (str(self.id) +"|" +str(self.gpsLon) +"|" +str(self.gpsLat) +"|" +str(self.alt) +"|" +str(self.heading) +"|" +str(self.time) +"|" +str(1))
