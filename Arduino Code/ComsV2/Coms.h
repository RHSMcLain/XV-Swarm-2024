#include <Arduino.h>
#include <WiFiNINA.h>                    //https://github.com/arduino-libraries/WiFiNINA/tree/master
#include <WiFiUDP.h>

#define MSP_ATTITUDE    108
#define MSP_SET_RAW_RC  200
#define MSP_RAW_GPS     106
#define MSP_WP          118
#define MSP_SET_WP      209

#define NAV_WP_FLAG_LAST 165
#define NAV_WP_FLAG_HOME 72

#define NAV_WP_ACTION_WAYPOINT  1
#define NAV_WP_ACTION_HOLD_TIME 3
#define NAV_WP_ACTION_RTH       4
#define NAV_WP_ACTION_SET_POI   5
#define NAV_WP_ACTION_JUMP      6
#define NAV_WP_ACTION_SET_HEAD  7
#define NAV_WP_ACTION_LAND      8

#define localPort 2390
#define ssid "XV_Basestation"

class Vector2D{
    public:
        double x; // Longitude or X coordinate
        double y; // Latitude or Y coordinate
        Vector2D() : x(0), y(0) {} // Default constructor
        Vector2D(double x, double y){
            this->x = x;
            this->y = y;
        }
};

class SearchArea{
    public:
        int dronesSearching;      // Number of drones searching this area
        int droneId;              // ID of this drone
        int alt;                  // Altitude in centimeters
        double viewDistance;      // View distance in meters
        Vector2D searchBounds[2]; // Two points defining the search area bounds
        SearchArea() : dronesSearching(0), alt(0), droneId(0), viewDistance(0) {
            searchBounds[0] = Vector2D();
            searchBounds[1] = Vector2D();
        }
        SearchArea(int dronesSearching, int alt, int droneId, double viewDistance, Vector2D point1, Vector2D point2){
            this->dronesSearching = dronesSearching;
            this->alt = alt;
            this->droneId = droneId;
            this->viewDistance = viewDistance;
            searchBounds[0] = point1;
            searchBounds[1] = point2;
        }
    private:
};

class Waypoint{
    public:
        uint8_t action;      // What to do at this waypoint (land, RTH, etc.)
        uint32_t lat;        // Latitude in degrees * 10 000 000
        uint32_t lon;        // Longitude in degrees * 10 000 000
        uint32_t alt;        // Altitude in centimeters
        uint16_t p1, p2, p3; // Action parameters (p3 is a bitfield)
        uint8_t flag;        // Flags (last, home, etc.)
        Waypoint() : action(0), lat(0), lon(0), alt(0), p1(0), p2(0), p3(0), flag(0) {}
        Waypoint(uint8_t action, uint32_t lat, uint32_t lon, uint32_t alt, uint16_t p1, uint16_t p2, uint16_t p3, uint8_t flag){
            this->action = action;
            this->lat = lat * 10000000;
            this->lon = 0x100000000 + lon * 10000000;
            this->alt = alt;
            this->p1 = p1;
            this->p2 = p2;
            this->p3 = p3;
            this->flag = flag;
        }
    private:
};

class msp_attitude_h{
    public:
        int16_t roll;   // Roll angle (degrees / 10)
        int16_t pitch;  // Pitch angle (degrees / 10)
        int16_t yaw;    // Yaw angle (degrees)
    private:
};

class msp_raw_gps_h{
    public:
        uint8_t gpsFix;     // 0 - 2
        uint8_t numSat;     // Number of satalites
        uint32_t lat;       // Degrees * 10,000,000
        uint32_t lon;       // Degrees * 10,000,000
        uint16_t gpsAlt;    // Centimeters
        uint16_t gpsSpeed;  // cm / seconds
        uint16_t gpsCourse; // Degrees
    private:
};

class PrevMessage_h{
    public:
        Arduino_h::IPAddress sourceIP;  //Source of ip
        Arduino_h::String cmd;          //Command (manual or swarm)
        int yaw;
        int pitch;
        int roll;
        int throttle;
        int killswitch;
        int armVar;
        int navHold;
        SearchArea searchArea; // Search area for swarm mode
    private:
};

class BSIPMessage_h{
    public:
        Arduino_h::String cmd;      //Command
        Arduino_h::IPAddress BSIP;  //Ip of the basestation
    private:
};

class WifiComs{
    public:
        PrevMessage_h parseMessage(char buffer[]);

        BSIPMessage_h parseBSIP(char buffer[]);

        int Listen(char packetBuffer[255]);

        int WifiConnection(char ReplyBuffer[]);

        void SendMessage(char msg[]);

        int GenerateSearchPath(SearchArea searchArea);

        WifiComs(char handShake[]){
            this->handShake = handShake;
        }

        PrevMessage_h PrevMessage;
        BSIPMessage_h BSIPMessage;
        Waypoint waypointArr[128];
        int countDis = 0;
        int wifiState = 0;
        Arduino_h::String state = "inactive";
        bool newWaypoints = false;
        
    private:
        char* handShake;
};

class FcComs{
    public:
        
        void begin(int baudRate);

        void commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes);

        void reqMSP(uint8_t req, uint8_t *data, uint8_t n_bytes);

        void sendWaypoints(Waypoint wp[], uint8_t size, uint8_t start);

        void readAttitudeData();

        void readGPSData();

        msp_attitude_h msp_attitude;
        msp_raw_gps_h msp_raw_gps;
    private:
};
