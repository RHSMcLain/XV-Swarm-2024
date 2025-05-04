#include <Coms.h>

void FcComs::begin(int speed){
    Serial1.begin(speed);
}

void FcComs::commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes){

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
  }
}

void FcComs::reqMSP(uint8_t req, uint8_t *data, uint8_t n_bytes){

  uint8_t checksum = 0;

  Serial1.write((byte *) "$M>", 3);
  Serial1.write(n_bytes);
  checksum ^= n_bytes;

  Serial1.write(req);
  checksum ^= req;

  Serial1.write(checksum);
}

void FcComs::sendWaypoints(Waypoint wp[]){
  uint8_t checksum = 0;
  uint8_t n_bytes = 0;
  uint8_t size = sizeof(wp);
  n_bytes = size*18;

  Serial1.write((byte *) "$M<", 3);
  Serial1.write(n_bytes);
  checksum ^= n_bytes;

  Serial1.write(MSP_SET_WP);
  checksum ^= MSP_SET_WP;

  for(uint8_t i = 0; i < size; i++){
    Serial1.write(i);
    checksum ^= i;
    //lat
    uint8_t lat1 = ((uint32_t)wp[i].lat >> 0) & 0xFF;
    uint8_t lat2 = ((uint32_t)wp[i].lat >> 8) & 0xFF;
    uint8_t lat3 = ((uint32_t)wp[i].lat >> 16) & 0xFF;
    uint8_t lat4 = ((uint32_t)wp[i].lat >> 24) & 0xFF;
    Serial1.write(lat1);
    Serial1.write(lat2);
    Serial1.write(lat3);
    Serial1.write(lat4);
    checksum ^= lat1;
    checksum ^= lat2;
    checksum ^= lat3;
    checksum ^= lat4;
    //lon
    uint8_t lon1 = ((uint32_t)wp[i].lon >> 0) & 0xFF;
    uint8_t lon2 = ((uint32_t)wp[i].lon >> 8) & 0xFF;
    uint8_t lon3 = ((uint32_t)wp[i].lon >> 16) & 0xFF;
    uint8_t lon4 = ((uint32_t)wp[i].lon >> 24) & 0xFF;
    Serial1.write(lon1);
    Serial1.write(lon2);
    Serial1.write(lon3);
    Serial1.write(lon4);
    checksum ^= lon1;
    checksum ^= lon2;
    checksum ^= lon3;
    checksum ^= lon4;
    //alt
    uint8_t alt1 = ((uint32_t)wp[i].alt >> 0) & 0xFF;
    uint8_t alt2 = ((uint32_t)wp[i].alt >> 8) & 0xFF;
    uint8_t alt3 = ((uint32_t)wp[i].alt >> 16) & 0xFF;
    uint8_t alt4 = ((uint32_t)wp[i].alt >> 24) & 0xFF;
    Serial1.write(alt1);
    Serial1.write(alt2);
    Serial1.write(alt3);
    Serial1.write(alt4);
    checksum ^= alt1;
    checksum ^= alt2;
    checksum ^= alt3;
    checksum ^= alt4;
    //heading
    uint8_t head1 = ((uint16_t)wp[i].heading >> 0) & 0xFF;
    uint8_t head2 = ((uint16_t)wp[i].heading >> 8) & 0xFF;
    Serial1.write(head1);
    Serial1.write(head2);
    checksum ^= head1;
    checksum ^= head2;
    //time
    uint8_t time1 = ((uint16_t)wp[i].time >> 0) & 0xFF;
    uint8_t time2 = ((uint16_t)wp[i].time >> 8) & 0xFF;
    Serial1.write(time1);
    Serial1.write(time2);
    checksum ^= time1;
    checksum ^= time2;
    //flag
    Serial1.write(wp[i].flag);
    checksum ^= wp[i].flag;
  }
}

void FcComs::readAttitudeData(){
  byte count = 0;
  reqMSP(MSP_ATTITUDE, 0, 0);
  delay(10);
  int16_t rollRec;
  int16_t pitchRec;
  int16_t yawRec;

  while (Serial1.available()){
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
  msp_attitude.roll = rollRec;
  msp_attitude.pitch = pitchRec;
  msp_attitude.yaw = yawRec;
}

void FcComs::readGPSData(){
  byte count = 0;
  reqMSP(MSP_RAW_GPS, 0, 0);
  delay(10);
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
  msp_raw_gps.gpsFix = gpsFix;
  msp_raw_gps.numSat = numSat;
  msp_raw_gps.lat = lat;
  msp_raw_gps.lon = lon;
  msp_raw_gps.gpsAlt = gpsAlt;
  msp_raw_gps.gpsSpeed = gpsSpeed;
  msp_raw_gps.gpsCourse = gpsCourse;
}

IPAddress bsip;
int connectTime = 0;
WiFiUDP Udp;
bool firstconnectframe = false;

PrevMessage_h WifiComs::parseMessage(char buffer[]){
    PrevMessage_h msg;
    char *token;
    token = strtok(buffer, "|");
    int i = 0;
    int wpNum = 0;
    int length;
    char lastWp;
    while(token != 0){
      //Serial.println(token);
      switch(i){
        case 0:
          msg.cmd = token;
          break;
        case 1:
          msg.sourceIP = token;
          break;
        if(msg.cmd == "MAN"){
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
            msg.armVar = atoi(token);
            break;
          case 8:
            msg.navHold = atoi(token);
            break;
        }
        else if(msg.cmd == "SWM"){
          if(i == 2){
            i = 9;
          }
          case 9:
            state = atoi(token);
            break;
          case 10:
            length = atoi(token);
            break;
          case 11:
            do{
              wpNum = atoi(token);
              token = strtok(NULL, "|"); 
              waypointArr[wpNum].lon = atoi(token);
              token = strtok(NULL, "|"); 
              waypointArr[wpNum].lat = atoi(token);
              token = strtok(NULL, "|"); 
              waypointArr[wpNum].alt = atoi(token);
              token = strtok(NULL, "|"); 
              waypointArr[wpNum].heading = atoi(token);
              token = strtok(NULL, "|"); 
              waypointArr[wpNum].time = atoi(token);
              token = strtok(NULL, "|"); 
              waypointArr[wpNum].flag = atoi(token);
              token = strtok(NULL, "|"); 
              lastWp = *token;
            }while(lastWp == *"loop");
            newWaypoints = true;
            break;
        }
      }
      i++;
      token = strtok(NULL, "|"); 
    }
    return msg;
    //HAS REQUIRED PACKETS FROM LISTEN, CODE FOR MANUAL MODE HERE --------------
    //Currently does not include a break, repeats loop forever
}

BSIPMessage_h WifiComs::parseBSIP(char buffer[]){
    BSIPMessage_h msg;
    char *token;
    token = strtok(buffer, "|");
    int i = 0;
    // Serial.println("In parseBSIP");
    while(token != 0){
      // Serial.println(token);
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

void WifiComs::SendMessage(char msg[]){
    Udp.begin(localPort);
    // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.beginPacket("192.168.4.22", 80);
    Udp.write(msg);
    Udp.endPacket();
}

int WifiComs::WifiConnection(char ReplyBuffer[]){
    // attempt to connect to Wi-Fi network:
    if(WiFi.status() != WL_CONNECTED && ((millis() - connectTime) > 2000)) {
      // Connect to WPA/WPA2 network:
      WiFi.begin(ssid);
      //Retry every 5 seconds
      connectTime = millis();
      firstconnectframe = true;
      return 0;
    }
    else if(WiFi.status() == WL_CONNECTED && firstconnectframe){
      Udp.begin(localPort);
      // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.beginPacket("192.168.4.22", 80);
      Udp.write("State: 0 -> 1 |Connected|");
      Udp.endPacket();
      wifiState = 1;
      Udp.beginPacket("192.168.4.22", 80);
      Udp.write(ReplyBuffer);
      Udp.endPacket();
      return 1;
    }
    if(wifiState == 1 && WiFi.status() == WL_CONNECTED){
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("State: 1 -> 2");
      Udp.endPacket();
      return 2;
    }
    else if(wifiState == 2){ 
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("AmDrone");
      Udp.endPacket();
      return 3;
    }
    else if(wifiState == 4) {
      Udp.beginPacket(bsip, 5005);
      Udp.write(handShake);
      Udp.endPacket();
      return 5;
    }
    else
    {
      return wifiState;
    }
}

int WifiComs::Listen(char packetBuffer[255]){
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
          // Serial.println("Parsing BSIP Message");
          //read BSID response from AP      
          BSIPMessage = parseBSIP(packetBuffer);
          BSIPMessage_h msg;
          msg = BSIPMessage;
          if (msg.cmd == "BSIP"){
            bsip = msg.BSIP;
            // Serial.print("Base Station IP: ");
            // Serial.println(bsip);
            return 4;
          }
        }
        else if (wifiState == 5){
          PrevMessage = parseMessage(packetBuffer);
          return 5;
        }
      }    
    }
    return wifiState;
}