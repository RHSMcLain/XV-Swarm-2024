#include <Coms.h>

#define hndShake "HND|-1|Betsy"

char ReplyBuffer[] = "Drone 1";
char packetBuffer[256]; 

WifiComs wifi(hndShake);
FcComs msp; 
uint16_t rc_values[8];

void Setup(){
    msp.begin(9600);
    Serial.begin(9600);
    wifi.WifiConnection(ReplyBuffer);
}

void Loop(){
    wifi.wifiState = wifi.WifiConnection(ReplyBuffer);
    wifi.wifiState = wifi.Listen(packetBuffer);
}