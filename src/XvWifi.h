#include <Arduino.h>

#define localPort 2390
#define handShake "HND|-1|Betsy"
#define ssid "XV_Basestation"

WiFiUDP Udp;

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

IPAddress bsip;

int connectTime = 0;

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