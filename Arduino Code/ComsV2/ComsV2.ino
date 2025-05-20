#include "Coms.h"

#define ident "HND|-1|Betsy"

char ReplyBuffer[] = "Drone 1";
char packetBuffer[256]; 
int reqUpdate = 10000;   //how often to update drone data
int pathLength = 1;
long lastUpdate = 0;

WifiComs wifi(ident);
FcComs msp; 
SearchArea searchArea;
Vector2D point1;
Vector2D point2;

uint16_t rc_values[8] = {//rc channel values
    1500,
    1500, 
    885, 
    1500, 
    1500, 
    1000, 
    1500, 
    1500
};    

bool light = false;     //light is on
bool flashing = true;   //light should flash
int blinkT = 100;       //time between state switches (ms)
long lastBlink = 0;     //time of last state switch (ms)

void setup(){
    Serial.begin(115200);
    while(!Serial);
    Serial.println("setup");
    pinMode(LED_BUILTIN, OUTPUT);
    msp.begin(9600);
    Serial.println("msp");
    wifi.WifiConnection(ReplyBuffer);
    // for(int i = 0; i < 3; i++){
    //     msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16);
    //     delay(100);
    // }
    if(false){
        wifi.waypointArr[0].alt = 500;
        wifi.waypointArr[0].flag = 0;
        wifi.waypointArr[0].lat = (45.454165) * 10000000;
        wifi.waypointArr[0].lon = 0x100000000 + (-122.685459* 10000000);
        wifi.waypointArr[0].action = NAV_WP_ACTION_WAYPOINT;
        wifi.waypointArr[0].p1 = 0;
        wifi.waypointArr[0].p2 = 0;
        wifi.waypointArr[0].p3 = 0;
        wifi.waypointArr[1].alt = 500;
        wifi.waypointArr[1].flag = NAV_WP_FLAG_LAST;
        wifi.waypointArr[1].lat = (45.455165) * 10000000;
        wifi.waypointArr[1].lon = 0x100000000 + (-122.686459* 10000000);
        wifi.waypointArr[1].action = NAV_WP_ACTION_WAYPOINT;
        wifi.waypointArr[1].p1 = 0;
        wifi.waypointArr[1].p2 = 0;
        wifi.waypointArr[1].p3 = 0;
    }
    if(true){
        point1.x = -122.685830;
        point1.y = 45.454398;
        point2.x = -122.685349;
        point2.y = 45.453885;
        Serial.println("points");
        searchArea.viewDistance = 2;
        searchArea.dronesSearching = 1;
        searchArea.searchBounds[0] = point1;
        searchArea.searchBounds[1] = point2;
        searchArea.droneId = 1;
        Serial.println("search area");
        pathLength = wifi.GenerateSearchPath(searchArea);
        Serial.println("waypoints");
    }
    wifi.newWaypoints = true;
}

void loop(){
    // Serial.println("loop");
    //wifi.WifiConnection(ReplyBuffer);
    //wifi.Listen(packetBuffer);
    if(reqUpdate < millis() - lastUpdate){
      // msp.readGPSData();
      // msp.readAttitudeData();
      // msp.sendWaypoints(wifi.waypointArr);
      // msp.reqMSP(100, 0, 0);
      // Serial.print("Ident  - ");

      // while(Serial1.available()){
      //   Serial.print(String(Serial1.read()));
      //   Serial.print("  ");
      // }
      // Serial.println();
      // delay(100);
      // msp.reqMSP(106, 0, 0);
      // Serial.print("GPS - ");
      // while(Serial1.available()){
      //   Serial.print(String(Serial1.read()));
      //   Serial.print("  ");
      // }
      Serial.println("\n");
      lastUpdate = millis();
      wifi.newWaypoints = true;
    }
    if(wifi.newWaypoints){
        msp.sendWaypoints(wifi.waypointArr, pathLength);
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
        msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16);
        for(int i = 0; i < 8; i++){
          Serial.print(rc_values[i]);
          Serial.print("  ");
          if(i == 7){
            Serial.println();
          }
        }
    }
    else if(wifi.PrevMessage.cmd == "SWM"){
        if(wifi.state == "active"){
            RcSet(1500, 1500, 885, 1500, 1500, 1700, 1500, 1500);
        }
    }
    if((millis() - lastBlink > blinkT) && flashing){
        LightSR();
    }
    else{
        digitalWrite(LED_BUILTIN, HIGH);
    }
    switch (wifi.wifiState){    //switch depending on the drones state
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
  delay(100);
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

void LightSR(){ //built in light as indicator sr latch
    if(light){
        digitalWrite(LED_BUILTIN, HIGH);
    }
    else{
        digitalWrite(LED_BUILTIN, LOW);
    }
    light ^= 1;
}