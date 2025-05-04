#include <Arduino.h>
#include <WiFiNINA.h>                    //https://github.com/arduino-libraries/WiFiNINA/tree/master
#include <WiFiUDP.h>

#define MSP_ATTITUDE 108
#define MSP_SET_RAW_RC 200
#define MSP_RAW_GPS 106
#define MSP_WP 118
#define MSP_SET_WP 209 

#define localPort 2390
// #define handShake "HND|-1|Betsy"
#define ssid "XV_Basestation"

class WifiComs{
    public:
        PrevMessage_h parseMessage(char buffer[]);

        BSIPMessage_h parseBSIP(char buffer[]);

        int Listen(char packetBuffer[255]);

        int WifiConnection(char ReplyBuffer[]);

        void SendMessage(char msg[]);

        WifiComs(char handShake_1[]){
            strcpy(handShake, handShake_1);
        }

        PrevMessage_h PrevMessage;
        BSIPMessage_h BSIPMessage;
        int wifiState = 0;
    private:
        char handShake[];

};

class FcComs{
    public:
        void begin(int speed);

        void commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes);

        void reqMSP(uint8_t req, uint8_t *data, uint8_t n_bytes);

        void sendWaypoints();

        void readAttitudeData();

        void readGPSData();

        Waypoint waypointArr[16];

        msp_attitude_h msp_attitude;
        msp_raw_gps_h msp_raw_gps;
    private:
};

class Waypoint{
    public:
        uint32_t lat;
        uint32_t lon;
        uint32_t alt;
        uint16_t heading;
        uint16_t time;
        uint8_t flag;
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
        uint8_t numSat;
        uint32_t lat;       //degrees / 10,000,000
        uint32_t lon;       //degrees / 10,000,000
        uint16_t gpsAlt;    //meters
        uint16_t gpsSpeed;  //cm / seconds
        uint16_t gpsCourse; //degrees
    private:
};

class PrevMessage_h{
    public:
        IPAddress sourceIP;
        String cmd;
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
        String cmd;
        IPAddress BSIP;
    private:
};