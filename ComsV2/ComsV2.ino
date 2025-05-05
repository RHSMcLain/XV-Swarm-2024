#include <Coms.h>

#define ident "HND|-1|Betsy"

char ReplyBuffer[] = "Drone 1";
char packetBuffer[256]; 

WifiComs wifi(ident);
FcComs msp; 
uint16_t rc_values[8] = {1500, 1500, 885, 1500, 1500, 1000, 1500, 1500};

bool light = false;
bool flashing = true;
int blinkT = 100;
long lastBlink = 0;

void setup(){
    pinMode(LED_BUILTIN, OUTPUT);
    msp.begin(9600);
    Serial.begin(9600);
    wifi.WifiConnection(ReplyBuffer);
    for(int i = 0; i < 3; i++){
        msp.commandMSP(MSP_SET_RAW_RC, rc_values, (2*sizeof(rc_values)));
        delay(100);
    }
}

void loop(){
    wifi.WifiConnection(ReplyBuffer);
    wifi.Listen(packetBuffer);
    msp.readGPSData();
    if(wifi.newWaypoints){
        msp.sendWaypoints(wifi.waypointArr);
        wifi.newWaypoints = false;
    }
    if(wifi.PrevMessage.cmd == "MAN"){
        rc_values[0] = wifi.PrevMessage.pitch;
        rc_values[1] = wifi.PrevMessage.roll;
        rc_values[2] = wifi.PrevMessage.throttle;
        rc_values[3] = wifi.PrevMessage.yaw;
        rc_values[4] = wifi.PrevMessage.navHold;
        rc_values[5] = wifi.PrevMessage.armVar;
        rc_values[6] = 1700;
        rc_values[7] = wifi.PrevMessage.killswitch;
        msp.commandMSP(MSP_SET_RAW_RC, rc_values, (2*sizeof(rc_values)));
    }
    else if(wifi.PrevMessage.cmd == "SWM"){
        if(wifi.state == "active"){
            RcSet(1500, 1500, 885, 1500, 1500, 1700, 1500, 1500);
        }
    }
    if((millis() - blinkT > lastBlink) && flashing){
        LightSR();
    }
    else{
        digitalWrite(LED_BUILTIN, HIGH);
    }
    switch (wifi.wifiState){
    case 1:
        flashing = true;
        blinkT = 100;
        break;
    case 3:
        flashing = true;
        blinkT = 1000;
        break;
    case 5:
        flashing = false;
        break;
    }

}

void RcSet(uint16_t pitch, uint16_t roll, uint16_t throttle, uint16_t yaw, uint16_t navHold, uint16_t armVar, uint16_t unused, uint16_t killswitch){
    rc_values[0] = pitch;
    rc_values[1] = roll;
    rc_values[2] = throttle;
    rc_values[3] = yaw;
    rc_values[4] = navHold;
    rc_values[5] = armVar;
    rc_values[6] = unused;
    rc_values[7] = killswitch;
}

void LightSR(){
    if(light){
        digitalWrite(LED_BUILTIN, HIGH);
    }
    else{
        digitalWrite(LED_BUILTIN, LOW);
    }
    light ^= 1;
}