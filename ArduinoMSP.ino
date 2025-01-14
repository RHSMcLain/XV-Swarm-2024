#include <WiFiNINA.h>//https://github.com/arduino-librariesWiFiNINA/tree/master
#include <WiFiUDP.h> 

#define MSP_ATTITUDE 108
#define MSP_SET_RAW_RC 200
#define MSP_RAW_GPS 106
#define MSP_WP 118
#define MSP_SET_WP 209

char ssid[] = "XV_Basestation";          //  network SSID (name)
unsigned long previousMillisInfo = 0;    //will store last time Wi-Fi information was updated
const int intervalInfo = 5000;           // interval at which to update the board information
char packetBuffer[256];                  //buffer to hold incoming packet
WiFiUDP Udp;
unsigned int localPort = 2390;
char  ReplyBuffer[] = "Drone 1";
int wifiState = 0;                       //Wifi connection state
bool firstConnectFrame = false;          //First Loop while connected to wifi
int status;
IPAddress bsip; //holds the base station ip address
bool bootComplete = false;

int updateTime = 0;
int connectTime = 0;

uint16_t rc_values[8];                   //RC Channels 0-7
long start;
bool light;
int droneState = 0;

struct{
  int lat;
  int lon;
  int alt;
  const char *droneId;
  const IPAddress *bsIp;
} send_data;

struct{
  uint8_t wp_no;
  uint32_t lat;
  uint32_t lon;
  uint32_t altHold;
  uint16_t heading;
  uint16_t time;
  uint8_t navFlag;
  uint8_t state;
} incoming_command;

struct{
  int16_t roll;
  int16_t pitch;
  int16_t yaw;
} msp_attitude;

struct{
  uint8_t gpsFix;
  uint8_t numSat;
  uint32_t lat;
  uint32_t lon;
  uint16_t gpsAlt;
  uint16_t gpsSpeed;
  uint16_t gpsCourse;
} msp_raw_gps;

struct ManualControlMessage{
  IPAddress sourceIP;
  String cmd;
  double yaw;
  double pitch;
  double roll;
  double throttle;
  double killswitch;
  double pytime;
};

struct BSIPMessage{
  String cmd;
  IPAddress BSIP;
};

void setup() {
  send_data.droneId = "NAME HERE";
  pinMode(13, OUTPUT);
  start = millis();
  delay(250);
  Serial1.begin(9600);
  Serial.begin(9600);
  rc_values[0] = 1000;
  rc_values[1] = 1100;
  rc_values[2] = 1200;
  rc_values[3] = 1300;
  rc_values[4] = 1400;
  rc_values[5] = 1500;
  rc_values[6] = 1500;
  rc_values[7] = 1500;
  WifiConnection();
}

void loop() {
  status = WiFi.status();
  WifiConnection();
  Listen();
  if (wifiState == 1 && droneState == 1 && status == WL_CONNECTED){
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.write("State: 1 -> 2");
    Udp.endPacket();
    wifiState = 2;
  }
  else if (wifiState == 2){ 
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.write("AmDrone");
    Udp.endPacket();
    wifiState = 3;
  }
  else if (wifiState == 4) {
    Udp.beginPacket(bsip, 5005);
    Udp.write("HND|-1|NEWDRONE");
    Udp.endPacket();
    wifiState = 5; 
  }
  if((millis()-start) > 1000){
    if(light)
    {
      digitalWrite(13, HIGH); 
      light = false;
    }
    else
    {
      digitalWrite(13, LOW); 
      light = true;
    }
    start = millis();
  }
  uint8_t datad = 0;
  uint8_t *data = &datad;
  // commandMSPRC(MSP_SET_RAW_RC, rc_values, 16);
  // mspWPSet(MSP_SET_WP);
  // sendMSP(MSP_RAW_GPS, 0, 0);
  // readGPSData();
  sendMSP(MSP_ATTITUDE, data, 0);
  readAttitudeData();
}

void commandMSPRC(uint8_t cmd, uint16_t data[], uint8_t n_cbytes){
  uint8_t checksum = 0;

  Serial1.write((byte *) "$M<", 3);
  Serial1.write(n_cbytes);
  checksum ^= (n_cbytes);
  Serial1.write(cmd);
  checksum ^= cmd;
  uint16_t cur_byte = 0;
  while(cur_byte < (n_cbytes/2)){
    int8_t byte1 = ((uint16_t)data[cur_byte] >> 0) & 0xFF;
    int8_t byte2 = ((uint16_t)data[cur_byte] >> 8) & 0xFF;
    Serial1.write(byte1);
    Serial1.write(byte2);
    checksum ^= byte1;
    checksum ^= byte2;
    cur_byte++;
  }
  Serial1.write(checksum);
  while(Serial1.available()){
    Serial1.read();
    Serial.println("clear");
  }
}

void mspWPSet(uint8_t cmd){
  uint8_t n_cbytes = 18;
  uint8_t checksum = 0;
  int8_t byte1;
  int8_t byte2;
  int8_t byte3;
  int8_t byte4;
  Serial1.write((byte *) "$M<", 3);
  Serial1.write(n_cbytes);
  checksum ^= (n_cbytes);
  Serial1.write(cmd);
  checksum ^= cmd;
  Serial1.write(incoming_command.wp_no);
  checksum ^= incoming_command.wp_no;
  int i = 0;
  while(i < 3){
    i++;
    if(i == 1){
      byte1 = (incoming_command.lat >> 0) & 0xFF;
      byte2 = (incoming_command.lat >> 8) & 0xFF;
      byte3 = (incoming_command.lat >> 16) & 0xFF;
      byte4 = (incoming_command.lat >> 24) & 0xFF;
    }
    else if(i == 2){
      byte1 = (incoming_command.lon >> 0) & 0xFF;
      byte2 = (incoming_command.lon >> 8) & 0xFF;
      byte3 = (incoming_command.lon >> 16) & 0xFF;
      byte4 = (incoming_command.lon >> 24) & 0xFF;
    }
    else if(i == 3){
      byte1 = (incoming_command.altHold >> 0) & 0xFF;
      byte2 = (incoming_command.altHold >> 8) & 0xFF;
      byte3 = (incoming_command.altHold >> 16) & 0xFF;
      byte4 = (incoming_command.altHold >> 24) & 0xFF;
    }
    Serial1.write(byte1);
    Serial1.write(byte2);
    Serial1.write(byte3);
    Serial1.write(byte4);
    checksum ^= byte1;
    checksum ^= byte2;
    checksum ^= byte3;
    checksum ^= byte4;
  }
  i = 0;
  while(i < 2){
    i++;
    if(i == 1){
      byte1 = (incoming_command.heading >> 0) & 0xFF;
      byte2 = (incoming_command.heading >> 8) & 0xFF;
    }
    else if(i == 2){
      byte1 = (incoming_command.time >> 0) & 0xFF;
      byte2 = (incoming_command.time >> 8) & 0xFF;
    }
    Serial1.write(byte1);
    Serial1.write(byte2);
    checksum ^= byte1;
    checksum ^= byte2;
  }
  Serial1.write(incoming_command.navFlag);
  checksum ^= incoming_command.navFlag;
  Serial1.write(checksum);
  while(Serial1.available()){
    Serial1.read();
    Serial.println("clear");
  }
}


void sendMSP(uint8_t req, uint8_t *data, uint8_t n_bytes) {

    uint8_t checksum = 0;

    Serial1.write((byte *) "$M<", 3);
    Serial1.write(n_bytes);
    checksum ^= n_bytes;

    Serial1.write(req);
    checksum ^= req;

    Serial1.write(checksum);
}

void readAttitudeData() {
  delay(100);
  byte count = 0;

  int16_t rollRec;
  int16_t pitchRec;
  int16_t yawRec;

  while (Serial1.available()) {
    count += 1;
    byte first;
    byte second;
    switch (count) {
      //first five bytes are header-type informatin, so start at 6
    case 1 ... 5:
      Serial1.read();
      break;
    case 6:
      first = Serial1.read();
      second = Serial1.read();
      rollRec = second;
      rollRec <<= 8;
      rollRec += first;
      break;
    case 7:
      first = Serial1.read();
      second = Serial1.read();
      pitchRec = second;
      pitchRec <<= 8;
      pitchRec += first;
      break;  
    case 8:
      first = Serial1.read();
      second = Serial1.read();
      yawRec = second;
      yawRec <<= 8;
      yawRec += first;
      break;
    case 9:
      Serial1.read();
      break;
    }
  }
  Serial.print("Roll: " + String(rollRec/10.0));
  Serial.print(" Pitch: " + String(pitchRec/10.0));
  Serial.println(" Yaw: " + String(yawRec));
}

void readGPSData(){
  delay(100);
  byte count = 0;
  uint8_t gpsFix;
  uint8_t numSat;
  uint32_t lat;
  uint32_t lon;
  uint16_t gpsAlt;
  uint16_t gpsSpeed;
  uint16_t gpsCourse;
  while (Serial1.available()) {
    count += 1;
    byte first;
    byte second;
    byte third;
    byte fourth;
    switch (count) {
      //first five bytes are header-type informatin, so start at 6
    case 1 ... 5:
      Serial1.read();
      break;
    case 6: //Fix, 1 is yes, 0 is no
      gpsFix = Serial1.read();
      break;
    case 7: //Number of satellites
      numSat = Serial1.read();
      break;  
    case 8: //Combine latitude bytes
      first = Serial1.read();
      second = Serial1.read();
      third = Serial1.read();
      fourth = Serial1.read();
      lat = fourth;
      lat <<= 8;
      lat += third;
      lat <<= 8;
      lat += second;
      lat <<= 8;
      lat += first;
      break;
    case 9: //Combine longitude bytes
      first = Serial1.read();
      second = Serial1.read();
      third = Serial1.read();
      fourth = Serial1.read();
      lon = fourth;
      lon <<= 8;
      lon += third;
      lon <<= 8;
      lon += second;
      lon <<= 8;
      lon += first;
      break;
    case 10: //Altitude in meters
      first = Serial1.read();
      second = Serial1.read();
      gpsAlt = second;
      gpsAlt <<= 8;
      gpsAlt += first;
      break;
    case 11: //Speed in cm/s
      first = Serial1.read();
      second = Serial1.read();
      gpsSpeed = second;
      gpsSpeed <<= 8;
      gpsSpeed += first;
      break;
    case 12: //Degrees times 10
      first = Serial1.read();
      second = Serial1.read();
      gpsCourse = second;
      gpsCourse <<= 8;
      gpsCourse += first;
      break;
    case 13:
      Serial1.read();
      break;
    }
  }
  Serial.print("Fix: " + String(gpsFix));
  Serial.print(" NumSat: " + String(numSat));
  Serial.print(" Lat: " + String(lat/10000000.0, 5));
  Serial.print(" Lon: " + String(lon/10000000.0, 5));
  Serial.print(" GPSALT: " + String(gpsAlt));
  Serial.print(" SOG: " + String(gpsSpeed));
  Serial.println(" GPSCourse: " + String(gpsCourse/10.0));
  msp_raw_gps.gpsFix = gpsFix;
}

void WifiConnection(){
  // attempt to connect to Wi-Fi network:
  if(status != WL_CONNECTED && ((millis() - connectTime) > 5000)) {
    Serial.print("Attempting to connect to network: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid);
    //Retry every 5 seconds
    firstConnectFrame = true;
    connectTime = millis();
  }
  else if(status == WL_CONNECTED && firstConnectFrame)
  {
    Udp.begin(localPort);
      // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.beginPacket("192.168.4.22", 80);
    Udp.write("State: 0 -> 1 |Connected|");
    Udp.endPacket();
    wifiState = 1;
    
    Udp.beginPacket("192.168.4.22", 80);
    Udp.write(ReplyBuffer);
    Udp.endPacket();
    // you're connected now, so print out the data:
    firstConnectFrame = false;
    bootComplete = true;
  }
}

void SendMessage(char msg[]){
  Udp.begin(localPort);
  // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  Udp.beginPacket("192.168.4.22", 80);
  Udp.write(msg);
  Udp.endPacket();
  Serial.println("Sent");
  Serial.println(msg);
  Serial.println("**********");
}

ManualControlMessage parseMessage(char buffer[]){
  ManualControlMessage msg;
  char *token;
  token = strtok(buffer, "|");
  int i = 0;
  while(token != 0){
    //Serial.println(token);
    switch(i){
      case 0:
        msg.cmd = token;
        break;
      case 1:
        msg.sourceIP = token;
        break;
      case 2:
        msg.yaw = atoi(token);       
        break;
      case 3:
        msg.pitch = atoi(token);  //pitch
        break;
      case 4: 
        msg.roll = atoi(token);
        break;
      case 5:
        msg.throttle = atoi(token);
        break;
      case 6:
        msg.killswitch = atoi(token);
        break;
      case 7:
        msg.pytime = atoi(token);
        break;
      }
    i++;
    token = strtok(NULL, "|"); 
  }
  return msg;  
  //HAS REQUIRED PACKETS FROM LISTEN, CODE FOR MANUAL MODE HERE --------------
  //Currently does not include a break, repeats loop forever
}  

BSIPMessage parseBSIP(char buffer[]){
  BSIPMessage msg;
  char *token;
  token = strtok(buffer, "|");
  int i = 0;
  Serial.println("In parseBSIP");
  while(token != 0){
    Serial.println(token);
    switch(i){
      case 0:
        msg.cmd = token;
        break;
      case 1:
        msg.BSIP = token;
        break;        
      }
    i++;
    token = strtok(NULL, "|");
    
  }
  return msg;  
}  

void Listen(){
  int packetSize = Udp.parsePacket();
  if(packetSize){
    //Serial.print("Received packet of size ");
    //Serial.println(packetSize);
    //Serial.print("From ");
    IPAddress remoteIp = Udp.remoteIP();
    //Serial.print(remoteIp);
    //Serial.print(", port ");
    //Serial.println(Udp.remotePort());
    // read the packet into packetBufffer
    int len = Udp.read(packetBuffer, 255);
    //Serial.println(packetBuffer);
    if (len > 0) {
      packetBuffer[len] = 0;
      if (wifiState == 3){
        Serial.println("Parsing BSIP Message");
        //read BSID response from AP      
        BSIPMessage msg = parseBSIP(packetBuffer);
        if (msg.cmd == "BSIP"){
          bsip = msg.BSIP;
          Serial.print("Base Station IP: ");
          Serial.println(bsip);
          wifiState = 4;
        }
      }
      else if (wifiState == 5){
        //Serial.println("listening for manual message");
        ManualControlMessage msg = parseMessage(packetBuffer);
        Serial.print("packet: ");
        Serial.print(msg.throttle);
        Serial.print(" recived at: ");
        Serial.print(millis());
        if (msg.cmd == "MAN"){
        }
      }
    }    
  }
}
