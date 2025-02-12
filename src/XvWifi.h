#include <Arduino.h>
#include <WiFiNINA.h>                    //https://github.com/arduino-libraries/WiFiNINA/tree/master
#include <WiFiUDP.h>

#define localPort 2390
#define handShake "HND|-1|Betsy"
#define ssid "XV_Basestation"

struct ManualControlMessage_h{
    IPAddress sourceIP;
    String cmd;
    double yaw;
    double pitch;
    double roll;
    double throttle;
    double killswitch;
    double armVar;
    double navHold;
};

struct BSIPMessage_h{
    String cmd;
    IPAddress BSIP;
};

class XvWifi{
    public:
        ManualControlMessage_h parseMessage(char buffer[]);

        BSIPMessage_h parseBSIP(char buffer[]);

        int Listen(int wifiState, char packetBuffer[255]);

        int WifiConnection(char ReplyBuffer[], int wifiState, int droneState);

        void SendMessage(char msg[]);

        ManualControlMessage_h ManualControlMessage;
        BSIPMessage_h BSIPMessage;
    private:
};