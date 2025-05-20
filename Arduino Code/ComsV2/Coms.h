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
// #define handShake "HND|-1|Betsy"
#define ssid "XV_Basestation"

class Vector2D{
    public:
        double x;
        double y;
};

class SearchArea{
    public:
        int dronesSearching;
        int droneId;
        double viewDistance;    //Meters
        Vector2D searchBounds[2];
    private:
};

class Waypoint{
    public:
        uint8_t action;      //What to do, land, rth, etc.
        uint32_t lat;       //degrees
        uint32_t lon;       //degrees
        uint32_t alt;       //cm
        uint16_t p1, p2, p3;   //action valuse
        uint8_t flag;       //Last, home, etc.
    private:
};

class msp_attitude_h{
    public:
        int16_t roll;       //degrees / 10
        int16_t pitch;      //degrees / 10
        int16_t yaw;        //degrees
    private:
};

class msp_raw_gps_h{
    public:
        uint8_t gpsFix;     //0 or 1
        uint8_t numSat;     //number of satalites
        uint32_t lat;       //degrees * 10,000,000
        uint32_t lon;       //degrees * 10,000,000
        uint16_t gpsAlt;    //meters
        uint16_t gpsSpeed;  //cm / seconds
        uint16_t gpsCourse; //degrees
    private:
};

class PrevMessage_h{
    public:
        Arduino_h::IPAddress sourceIP;  //Source of ip
        Arduino_h::String cmd;          //Command (manual or swarm)
        double yaw;
        double pitch;
        double roll;
        double throttle;
        double killswitch;
        double armVar;
        double navHold;
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

        WifiComs(char hnd[]){
            handShake = hnd;
        }

        PrevMessage_h PrevMessage;
        BSIPMessage_h BSIPMessage;
        Waypoint waypointArr[128];
        int wifiState = 0;
        Arduino_h::String state = "inactive";
        bool newWaypoints = false;
        
    private:
        char* handShake;
};

class FcComs{
    public:
        void begin(int speed);

        void commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes);

        void reqMSP(uint8_t req, uint8_t *data, uint8_t n_bytes);

        void sendWaypoints(Waypoint wp[], uint8_t size);

        void readAttitudeData();

        void readGPSData();

        msp_attitude_h msp_attitude;
        msp_raw_gps_h msp_raw_gps;
    private:
};
