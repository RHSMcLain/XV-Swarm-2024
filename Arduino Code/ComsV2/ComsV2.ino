/*
    * This sketch is for a drone communication system using MSP protocol and WiFi.
    * It handles waypoints, telemetry, and manual control commands.
    * It includes a search area definition and manages drone states.
    * It is designed to work on an Arduino Nano 33 IoT.
    * Requires:
    *   https://github.com/arduino-libraries/WiFiNINA/tree/master
    *   Accompanying python code running on a computer to send commands
    *   An ESP8622 or similar WiFi module to function as an access point
    * Created by:
    * Date:
*/

#include "Coms.h"

#define ident "HND|-1|Betsy"

char ReplyBuffer[] = "Drone 1";
char packetBuffer[256]; 
bool mspTelemetry = true; // Flag to enable/disable telemetry
int reqUpdate = 10000;   //how often to update drone data
int pathLength = 1;
long lastUpdate = 0;

FcComs msp; 
WifiComs wifi(ident);
Vector2D point1(-122.685728, 45.454396);
Vector2D point2(-122.685349, 45.453885);
Waypoint home(NAV_WP_ACTION_LAND, -122.685679, 45.454211, 500, 0, 0, 0, NAV_WP_FLAG_HOME); // Home waypoint
SearchArea searchArea(1, 150, 1, 2, point1, point2);

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
    Serial.begin(115200); // Start serial communication for debugging
    msp.begin(9600);
    while(!Serial && millis() < 2000);// Wait for serial to be ready or timeout after 2 seconds  
    //home Waypoint
    wifi.waypointArr[0] = home;
    msp.sendWaypoints(wifi.waypointArr, 1, 0);
    Serial.println("setup");
    pinMode(LED_BUILTIN, OUTPUT); // Set built-in LED as output
    Serial.println("msp");
    wifi.WifiConnection(ReplyBuffer); // Attempt WiFi connection
    for(int i = 0; i < 3; i++){
        msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16); // Send initial RC values
        delay(100);
    }
    //custom waypoints
    //wifi.waypointArr[0] = Waypoint(NAV_WP_ACTION_WAYPOINT, 0x100000000 + (-122.685830* 10000000), (45.454398) * 10000000, 500, 0, 0, 0, 0);
    //wifi.waypointArr[1] = Waypoint(NAV_WP_ACTION_WAYPOINT, 0x100000000 + (-122.685349* 10000000), (45.453885) * 10000000, 500, 0, 0, 0, NAV_WP_FLAG_LAST);
    // wifi.newWaypoints = true; // Flag to send new waypoints
}

void loop(){
    wifi.WifiConnection(ReplyBuffer); // Optionally reconnect WiFi
    wifi.Listen(packetBuffer); // Optionally listen for new messages
    if(reqUpdate < millis() - lastUpdate && mspTelemetry){ // Time to update drone data?
        while(Serial1.available()) Serial1.read();
        // msp.readGPSData();
        // msp.readAttitudeData();
        // Serial.println();
        lastUpdate = millis();
        // wifi.newWaypoints = true; // Request new waypoints to be sent
    }
    if(wifi.newWaypoints){
        Serial.println("New Waypoints");
        pathLength = wifi.GenerateSearchPath(wifi.PrevMessage.searchArea); // Generate new search path
        msp.sendWaypoints(wifi.waypointArr, pathLength, 1); // Send waypoints to flight controller
        wifi.newWaypoints = false;
    }
    if(wifi.PrevMessage.cmd == "MAN"){
        // Manual mode: update RC values from received message
        rc_values[0] = wifi.PrevMessage.pitch;
        rc_values[1] = wifi.PrevMessage.roll;
        rc_values[2] = wifi.PrevMessage.throttle;
        rc_values[3] = wifi.PrevMessage.yaw;
        rc_values[4] = wifi.PrevMessage.navHold;
        rc_values[5] = wifi.PrevMessage.armVar;
        rc_values[6] = 1700;
        rc_values[7] = wifi.PrevMessage.killswitch;
        msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16); // Send RC values
        // for(int i = 0; i < 8; i++){
        //   Serial.print(rc_values[i]);
        //   Serial.print("  ");
        //   if(i == 7){
        //     Serial.println();
        //   }
        // }
    }
    else if(wifi.PrevMessage.cmd == "SWM"){
        // Swarm mode: set RC values for autonomous operation
        if(wifi.state == "active"){
            RcSet(1500, 1500, 885, 1500, 1500, 1700, 1500, 1500);
        }
    }
    else{
        // Default RC values
        RcSet(1500, 1500, 885, 1500, 1500, 1500, 1500, 1500);
        msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16); // Send default RC values
        while (Serial1.available()){
            Serial1.read();
        }  
    }
    if((millis() - lastBlink > blinkT) && flashing){
        LightSR(); // Toggle LED for status indication
    }
    else{
        digitalWrite(LED_BUILTIN, HIGH); // Keep LED on
    }
    switch (wifi.wifiState){    //switch depending on the drone's state
    case 1:
        flashing = true; // Fast blink
        blinkT = 100;
        break;
    case 3:
        flashing = true; // Slow blink
        blinkT = 1000;
        break;
    case 5:
        flashing = false; // LED solid
        break;
    }
  delay(10); // Main loop delay
}

void RcSet(uint16_t pitch, uint16_t roll, uint16_t throttle, uint16_t yaw, uint16_t navHold, uint16_t armVar, uint16_t unused, uint16_t killswitch){
    // Helper to set RC values
    rc_values[0] = pitch;
    rc_values[1] = roll;
    rc_values[2] = throttle;
    rc_values[3] = yaw;
    rc_values[4] = navHold;
    rc_values[5] = armVar;
    rc_values[6] = unused;
    rc_values[7] = killswitch;
}

void LightSR(){ //built in light as indicator SR latch
    if(light){
        digitalWrite(LED_BUILTIN, HIGH); // LED on
    }
    else{
        digitalWrite(LED_BUILTIN, LOW); // LED off
    }
    light ^= 1; // Toggle light state
}