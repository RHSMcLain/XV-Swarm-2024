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
    global waypointArr
    waypointArr = [None]
    def __init__(self, id, name, ipAddress, port, state) -> None:
        self.id = id
        self.name = name
        self.ipAddress = ipAddress
        self.port = port
        self.state = state
    def __str__(self):
        #This provides the string that will be used in the listbox
        return self.name
    def waypointAdd(targetLat, targetLon, targetAlt, waitTime): #pushes a new waypoint onto the list
        waypointArr.append(Track(targetLat, targetLon, targetAlt, waitTime, len(waypointArr)))
    def waypointRemove(waypointID): #deletes the waypoint from the list
        del waypointArr[waypointID]
    def waypointReplace(targetLat, targetLon, targetAlt, waitTime, waypointID): #replaces the waypoint
        waypointArr[waypointID] = Track(targetLat, targetLon, targetAlt, waitTime, waypointID)
    def waypointClear(): #deletes all waypoints and replaces id 0 with none
        for i in range(0,len(waypointArr)):
            if i == 0:
                waypointArr[0] = None
            else:
                del waypointArr[i]
class Track():
    id = None
    gpsLon = None
    gpsLat = None
    alt = None
    time = None
    def __init__(self, gpsLon, gpsLat, alt, time, id) -> None:
        self.gpsLon = gpsLon
        self.gpsLat = gpsLat
        self.alt = alt
        self.time = time
        self.id = id