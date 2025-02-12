#include <XvMsp.h>
#include <XvWifi.h>

XvMsp msp;
XvWifi net;

char packetBuffer[256];                  //buffer to hold incoming packet
char ReplyBuffer[] = "Drone 1";

bool serialUSB = false;
bool isArmed = false;
bool isFailsafed = false;
bool isKilled = false;
bool lightOn = false;
bool enabled = false;

double pitch = 1500;
double roll = 1500;
double yaw = 1500;
double throttle = 885;
double armVar = 1000;
double navHold = 1000;

int status = WL_IDLE_STATUS;             // the Wi-Fi radio's status
int ledState = LOW;                      //ledState used to set the LED
int wifiState = 0;                       //Wifi connection state
int updateTime = 0;
int droneState = -1;  
int killswitch = 1000;
int failsafe = 1000;
int blinkSpeed = 10;
const int intervalInfo = 5000;           // interval at which to update the board information

uint16_t rc_values[10] = {1500, 1500, 885, 1500, 1500, 1000, 1500, 1500, 1500, 1600};

long t = 0;
long blinkTime = 0;
unsigned long previousMillisInfo = 0;    //will store last time Wi-Fi information was updated
unsigned long previousMillisLED = 0;     // will store the last time LED was updated

void setup(){
  //Initialize serial and wait for port to open: 
  Serial.begin(9600);
  msp.begin(9600);
  if(Serial){
    serialUSB = true;
    Serial.println("Setup");
  }
  delay(1000);
  pinMode(LED_BUILTIN, OUTPUT);
  net.WifiConnection(ReplyBuffer, wifiState, droneState);
  delay(250);
  rc_values[0] = 1500;
  rc_values[1] = 1500;
  rc_values[2] = 885;
  rc_values[3] = 1500;
  rc_values[4] = 1500;
  rc_values[5] = 1000;
  rc_values[6] = 1500;
  rc_values[7] = 1500;
  rc_values[9] = 1600;
  for(int i = 0; i < 3; i++){
    msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16);
  }
  delay(3000);
  msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16);
}//end setup

void loop() {
  status = WiFi.status();
  if(status != WL_CONNECTED){  
    blinkSpeed = 50;
    failsafe = 1600;
  }
  else{
    failsafe = 1000;
  }
  //MillisStuff();
  wifiState = net.WifiConnection(ReplyBuffer, wifiState, droneState);
  wifiState = net.Listen(wifiState, packetBuffer);
  DroneSystems();
  MSPLoop();
  if(millis() - updateTime > 5000 && serialUSB){
    Serial.println("<--------------------------->\nDrone Data");
    Serial.print("Throttle: "); Serial.println(throttle);
    Serial.print("Pitch: "); Serial.println(pitch);
    Serial.print("Roll: "); Serial.println(roll);
    Serial.print("Yaw: "); Serial.println(yaw);
    Serial.print("Armed: "); Serial.println(isArmed);
    Serial.print("Failsafe: "); Serial.println(isFailsafed);
    Serial.print("Killswitch: "); Serial.println(isKilled);
    Serial.println("<--------------------------->");
    updateTime = millis();
  }
  if(wifiState == 5)
  {
    roll = net.ManualControlMessage.roll;
    pitch = net.ManualControlMessage.pitch;
    throttle = net.ManualControlMessage.throttle;
    yaw = net.ManualControlMessage.yaw;
    killswitch = net.ManualControlMessage.killswitch;
    armVar = net.ManualControlMessage.armVar;
    navHold = net.ManualControlMessage.navHold;
  }
  // else if (state == 5) {
  //   //call parsemanualcontrolmessage and process the results
  //   //but do it in listen
  //   // Serial.println(roll);
  //   // Serial.println(yaw);
  //   // Serial.println(pitch);
  //   // Serial.println(throttle);
  // }
}//End Loop

void DroneSystems(){
  if (droneState == -1){//starting up
    blinkSpeed = 1000;       
    throttle = 885;
    Serial.println("Drone State -1 | Pre-State");
    if(millis() - t > 1000){
      t = millis();
      droneState = 0;
    }
  }
  else if (droneState == 0){//arm drone
    blinkSpeed = 1000;
    if (millis() - t > 500){
      droneState = 1;
      t = millis();
    }
  }
  else if (droneState == 1){ //nothing
    //Roll Ch 0, pitch Ch 1, Yaw Ch 3, Throttle Ch 2, Arm Ch 4
  }
  else if(droneState == 2){
    
  }
  if(status != WL_CONNECTED){
    if(millis()- blinkTime >= blinkSpeed){
      LightSRLatch();
      blinkTime = millis();
    }
  }
  else if(droneState == -1 || droneState == 0){ //Light Blinker
    if(millis()- blinkTime >= blinkSpeed){
      LightSRLatch();
      blinkTime = millis();
    }
  }
  else if(killswitch == 1700){
    digitalWrite(LED_BUILTIN,LOW);
  }
  else{
    digitalWrite(LED_BUILTIN,HIGH);
  }
  CheckModeStates();
  // delay(10);  
}//End Drone Systems

void MSPLoop(){
  uint8_t datad = 0;
  uint8_t *data = &datad;
  // msp.sendMSP(MSP_RAW_GPS, 0, 0);
  // msp.readGPSData();
  // msp.sendMSP(MSP_ATTITUDE, data, 0);
  // msp.readAttitudeData();
  rc_values[0] = pitch;
  rc_values[1] = roll;
  rc_values[2] = throttle;
  rc_values[3] = yaw;
  rc_values[4] = navHold;
  rc_values[5] = armVar;
  rc_values[6] = 1700;
  rc_values[7] = killswitch;
  rc_values[9] = 1600;
  msp.commandMSP(MSP_SET_RAW_RC, rc_values, 16);
}

void CheckModeStates(){ //sets booleans of the modes for enabled/disabled
  if(armVar > 1500){
    isArmed = true;
  }
  else{
    isArmed = false;
  }
  if(failsafe > 1500){
    isFailsafed = true;
  }
  else{
    isFailsafed = false;
  }
  if(killswitch > 1500){
    isKilled = true;
  }
  else{
    isKilled = false;
  }
}

void LightSRLatch(){
  if(lightOn){
    digitalWrite(LED_BUILTIN, LOW);
    lightOn = false;    
  }
  else if(!lightOn){
    digitalWrite(LED_BUILTIN, HIGH);
    lightOn = true;    
  }
}

void printBoardInfo(){
  Serial.println("Board Information:");
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print your network's SSID:
  Serial.println();
  Serial.println("Network Information:");
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);
  Serial.println("---------------------------------------");
  Serial.println("You're connected to the network");
  Serial.println("---------------------------------------");
}